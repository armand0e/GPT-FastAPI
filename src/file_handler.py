import json
import os
import dotenv
from pydantic import BaseModel
import aiofiles
from logger import get_logger, LOG_DIR
from fastapi import APIRouter, HTTPException
import ast

router = APIRouter()
dotenv.load_dotenv()

# Configure logging
logger = get_logger()

class WriteFileRequest(BaseModel):
    filepath: str
    content: str

class AppendFileRequest(BaseModel):
    filepath: str
    content: str | list

class ReadFileRequest(BaseModel):
    filepath: str

class ReadLinesRequest(BaseModel):
    filepath: str
    start_line: int
    num_lines: int

class ReplaceFunctionRequest(BaseModel):
    filepath: str
    function_name: str
    new_function_code: str  # Should be a complete function definition

class FunctionReplacer(ast.NodeTransformer):
    def __init__(self, target_name: str, new_node: ast.FunctionDef):
        self.target_name = target_name
        self.new_node = new_node

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Replace the function if the name matches
        if node.name == self.target_name:
            return self.new_node
        return node

@router.post("/replace-function")
async def replace_function(req: ReplaceFunctionRequest):
    # Construct the full file path
    file_path = os.path.join(os.getcwd(), req.filepath)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Read the original file content
    async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
        source = await f.read()
    
    # Parse the file into an AST
    try:
        tree = ast.parse(source)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing source file: {str(e)}")
    
    # Parse the new function code to get its AST node
    try:
        new_tree = ast.parse(req.new_function_code)
        # Expecting one function definition at the module level
        new_funcs = [node for node in new_tree.body if isinstance(node, ast.FunctionDef)]
        if not new_funcs:
            raise ValueError("No function definition found in new_function_code")
        new_func_node = new_funcs[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing new function code: {str(e)}")
    
    # Replace the target function using our NodeTransformer
    replacer = FunctionReplacer(req.function_name, new_func_node)
    modified_tree = replacer.visit(tree)
    ast.fix_missing_locations(modified_tree)
    
    # Convert the modified AST back to source code.
    # Python 3.9+ provides ast.unparse, otherwise you might need to use astunparse.
    try:
        new_source = ast.unparse(modified_tree)
    except Exception as e:
        try:
            import astunparse
            new_source = astunparse.unparse(modified_tree)
        except ImportError:
            raise HTTPException(status_code=500, detail="ast.unparse not available and astunparse is not installed")
    
    # Write to a temporary file first for atomicity
    temp_file_path = file_path + ".tmp"
    async with aiofiles.open(temp_file_path, "w", encoding="utf-8") as f:
        await f.write(new_source)
    
    # Replace the original file with the temporary file
    try:
        os.replace(temp_file_path, file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error replacing original file: {str(e)}")
    
    return {"message": f"Function '{req.function_name}' successfully replaced."}

async def read_file(file_path):
    file_path = os.path.join(os.getcwd(), file_path)
    if not os.path.exists(file_path):
        return json.dumps({"error": "File not found"})
    try:
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            content = ""
            async for line in f:
                content += line
        return json.dumps({"file": file_path, "content": content})
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Read error: {str(e)}")

async def make_file(file_path, content):
    file_path = os.path.join(os.getcwd(), file_path)
    try:
        async with aiofiles.open(file_path, "w", encoding="utf-8", newline="\n") as f:
            await f.write(content)
            await f.flush()
    except Exception as e:
        logger.error(f"Write error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Write error: {str(e)}")
    return {"message": f"File '{file_path}' saved successfully"}

async def append_to_file(file_path, content):
    file_path = os.path.join(os.getcwd(), file_path)
    if not os.path.exists(file_path):
        return json.dumps({"error": "File not found"})
    try:
        async with aiofiles.open(file_path, "a", encoding="utf-8", newline="\n") as f:
            if isinstance(content, list):
                await f.writelines([line + "\n" for line in content])
            else:
                await f.write(content + "\n")
            await f.flush()
    except Exception as e:
        logger.error(f"Append error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Append error: {str(e)}")
    return {"message": f"Content appended to '{file_path}' successfully"}

async def read_lines_from_file(file_path, start_line, num_lines):
    file_path = os.path.join(os.getcwd(), file_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    try:
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            lines = await f.readlines()
            if start_line < 0 or start_line >= len(lines):
                raise HTTPException(status_code=400, detail="Invalid start line index")
            return {"lines": lines[start_line : start_line + num_lines]}

    except Exception as e:
        logger.error(f"Read error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Read error: {str(e)}")

@router.post("/read-file")
async def get_file(request: ReadFileRequest):
    content = await read_file(request.filepath)
    return {"content": content}

@router.post("/write-file")
async def write_file(request: WriteFileRequest):
    return await make_file(request.filepath, request.content)

@router.post("/append-file")
async def append_file(request: AppendFileRequest):
    return await append_to_file(request.filepath, request.content)

@router.post("/read-lines")
async def read_lines(request: ReadLinesRequest):
    return await read_lines_from_file(request.filepath, request.start_line, request.num_lines)

class LogRequest(BaseModel):
    num_lines: int = 10  # Default to reading last 10 lines

@router.post("/read-log")
async def read_log(request: LogRequest):
    """Reads the last N lines from the log file, maintaining order."""
    log_path = os.path.join(LOG_DIR, "system.log")

    if not os.path.exists(log_path):
        raise HTTPException(status_code=404, detail="Log file not found")

    try:
        async with aiofiles.open(log_path, "r", encoding="utf-8") as f:
            lines = await f.readlines()  # Read all lines
        
        # Get the last N lines while preserving order
        snippet = lines[-request.num_lines:]

        return {"logs": snippet}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Log read error: {str(e)}")
