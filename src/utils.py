import os
import aiofiles
import ast
from pathlib import Path
from logger import system_logger  # Import the logger

logger = system_logger

class FunctionReplacer(ast.NodeTransformer):
    def __init__(self, target_name: str, new_node: ast.FunctionDef):
        self.target_name = target_name
        self.new_node = new_node
        self.replaced = False

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.name == self.target_name:
            self.replaced = True
            return self.new_node
        return self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        if node.name == self.target_name:
            self.replaced = True
            return self.new_node
        return self.generic_visit(node)

def resolve_path(filepath: str) -> Path:
    """
    Resolves a file path for cross-platform compatibility.
    Adjust handling if running on WSL2.
    """
    path = Path(filepath).resolve()
    # Example handling for WSL2 on Windows (adjust if needed)
    if os.name == "nt" and hasattr(os, "uname") and "WSL2" in os.uname().release:
        return Path("/mnt/" + path.drive.lower().replace(':', '') + path.as_posix()[2:])
    return path

async def read_file(file_path: str):
    """
    Reads the entire content of the specified file asynchronously.
    """
    resolved_path = resolve_path(file_path)
    if not resolved_path.exists():
        logger.error(f"File not found: {resolved_path}")
        return {"error": "File not found"}

    try:
        async with aiofiles.open(resolved_path, "r", encoding="utf-8") as f:
            content = await f.read()
        logger.info(f"Read file successfully: {resolved_path}")
        return {"file": str(resolved_path), "content": content}
    except Exception as e:
        logger.error(f"Read error in {resolved_path}: {str(e)}")
        return {"error": f"Read error: {str(e)}"}

async def write_file(file_path: str, content: str):
    """
    Writes content to the specified file asynchronously.
    """
    resolved_path = resolve_path(file_path)
    try:
        async with aiofiles.open(resolved_path, "w", encoding="utf-8") as f:
            await f.write(content)
        logger.info(f"File written successfully: {resolved_path}")
        return {"message": f"File '{resolved_path}' saved successfully"}
    except Exception as e:
        logger.error(f"Write error in {resolved_path}: {str(e)}")
        return {"error": f"Write error: {str(e)}"}

async def append_file(file_path: str, content):
    """
    Appends content to the specified file asynchronously.
    """
    resolved_path = resolve_path(file_path)
    if not resolved_path.exists():
        logger.error(f"Append failed; file not found: {resolved_path}")
        return {"error": "File not found"}

    try:
        async with aiofiles.open(resolved_path, "a", encoding="utf-8") as f:
            if isinstance(content, list):
                await f.writelines([line + "\n" for line in content])
            else:
                await f.write(content + "\n")
        logger.info(f"Appended content to file: {resolved_path}")
        return {"message": f"Content appended to '{resolved_path}' successfully"}
    except Exception as e:
        logger.error(f"Append error in {resolved_path}: {str(e)}")
        return {"error": f"Append error: {str(e)}"}

async def read_lines(file_path: str, start_line: int, num_lines: int):
    """
    Reads a specified number of lines from a file asynchronously.
    """
    resolved_path = resolve_path(file_path)
    if not resolved_path.exists():
        logger.error(f"Read lines failed; file not found: {resolved_path}")
        return {"error": "File not found"}

    try:
        async with aiofiles.open(resolved_path, "r", encoding="utf-8") as f:
            lines = await f.readlines()
        if start_line < 0 or start_line >= len(lines):
            logger.error(f"Invalid start line index {start_line} for file: {resolved_path}")
            return {"error": "Invalid start line index"}
        logger.info(f"Read {num_lines} lines from file: {resolved_path}")
        return {"lines": lines[start_line : start_line + num_lines]}
    except Exception as e:
        logger.error(f"Error reading lines from {resolved_path}: {str(e)}")
        return {"error": f"Read error: {str(e)}"}

async def read_logs():
    """
    Reads the content of the system log file asynchronously.
    """
    log_path = resolve_path("logs/system.log")
    if not log_path.exists():
        logger.error(f"System log file not found: {log_path}")
        return {"error": "Log file not found"}
    try:
        async with aiofiles.open(log_path, "r", encoding="utf-8") as f:
            lines = await f.readlines()
        logger.info(f"Read system log file: {log_path}")
        return {"logs": "\n".join(lines)}
    except Exception as e:
        logger.error(f"Error reading system log {log_path}: {str(e)}")
        return {"error": f"Log read error: {str(e)}"}

async def replace_text(file_path: str, original_text: str, replacement_text: str):
    """
    Replaces a specific text snippet with new text in the file.
    """
    file_data = await read_file(file_path)
    if "error" in file_data:
        logger.error(f"Replace text failed; file not found: {file_path}")
        return {"error": "File not found"}
    content = file_data["content"]
    if original_text not in content:
        logger.error(f"Original text not found in {file_path}")
        return {"error": "Original text not found in the file"}
    new_content = content.replace(original_text, replacement_text)
    logger.info(f"Replaced text in file: {file_path}")
    return await write_file(file_path, new_content)

async def replace_func(file_path: str, function_name: str, new_function_code: str):
    """
    Replaces the definition of a function in a Python source file using AST manipulation.
    """
    file_data = await read_file(file_path)
    if "error" in file_data:
        logger.error(f"Replace function failed; file not found: {file_path}")
        return {"error": "File not found"}
    content = file_data["content"]
    try:
        tree = ast.parse(content)
    except Exception as e:
        logger.error(f"Error parsing source file {file_path}: {str(e)}")
        return {"error": f"Error parsing source file: {str(e)}"}
    try:
        new_tree = ast.parse(new_function_code)
        new_func_node = next((node for node in new_tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))), None)
        if not new_func_node:
            logger.error("No function definition found in new function code")
            return {"error": "No function definition found in new_function_code"}
    except Exception as e:
        logger.error(f"Error parsing new function code for {file_path}: {str(e)}")
        return {"error": f"Error parsing new function code: {str(e)}"}
    
    replacer = FunctionReplacer(function_name, new_func_node)
    modified_tree = replacer.visit(tree)
    ast.fix_missing_locations(modified_tree)
    if not replacer.replaced:
        logger.error(f"Function '{function_name}' not found in {file_path}")
        return {"error": f"Function '{function_name}' not found in the source file."}
    try:
        new_source = ast.unparse(modified_tree)
    except Exception as e:
        try:
            import astunparse
            new_source = astunparse.unparse(modified_tree)
        except ImportError:
            logger.error("ast.unparse not available and astunparse is not installed")
            return {"error": "ast.unparse not available and astunparse is not installed"}
    logger.info(f"Replaced function '{function_name}' in file: {file_path}")
    return await write_file(file_path, new_source)

async def read_func(filepath: str, function_name: str):
    """
    Reads and returns the source code of a specific function from a Python file.
    """
    file_data = await read_file(filepath)
    if "error" in file_data:
        logger.error(f"Read function failed; file not found: {filepath}")
        return {"error": "File not found"}
    
    content = file_data["content"]
    try:
        tree = ast.parse(content)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
                logger.info(f"Read function '{function_name}' from {filepath}")
                return {"function_name": function_name, "source_code": ast.unparse(node)}
        logger.error(f"Function '{function_name}' not found in {filepath}")
        return {"error": f"Function '{function_name}' not found in {filepath}"}
    except Exception as e:
        logger.error(f"Error parsing file {filepath}: {str(e)}")
        return {"error": f"Error parsing file: {str(e)}"}
