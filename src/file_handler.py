import json
import os
import dotenv
from pydantic import BaseModel
import aiofiles
from fastapi import APIRouter, HTTPException

router = APIRouter()
dotenv.load_dotenv()

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

async def read_file(file_path):
    cd = dotenv.get_key(".env", "CURRENT_DIR")

    file_path = os.path.join(cd, file_path)
    if not os.path.exists(file_path):
        return json.dumps({"error": "File not found"})
    with open(file_path, "r", encoding="utf-8") as f:
        return json.dumps({"file": file_path, "content": f.read()})

async def make_file(file_path, content):
    cd = dotenv.get_key(".env", "CURRENT_DIR")

    file_path = os.path.join(cd, file_path)

    try:
        async with aiofiles.open(file_path, "w", encoding="utf-8", newline="\n") as f:
            await f.write(content)
            await f.flush()  # Ensure content is fully written
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Write error: {str(e)}")
    return {"message": f"File '{file_path}' saved successfully"}

async def append_to_file(file_path, content):
    """
    Appends multiple lines to the end of a file in batch mode.
    If 'content' is a string, it appends a single line.
    If 'content' is a list, it appends all lines in one operation.
    """
    cd = dotenv.get_key(".env", "CURRENT_DIR")

    file_path = os.path.join(cd, file_path)
    if not os.path.exists(file_path):
        return json.dumps({"error": "File not found"})
    try:
        async with aiofiles.open(file_path, "a", encoding="utf-8", newline="\n") as f:
            if isinstance(content, list):  # Batch append mode
                await f.writelines([line + "\n" for line in content])
            else:
                await f.write(content + "\n")
            await f.flush()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Append error: {str(e)}")
    return {"message": f"Content appended to '{file_path}' successfully"}

async def read_lines_from_file(file_path, start_line, num_lines):
    cd = dotenv.get_key(".env", "CURRENT_DIR")

    file_path = os.path.join(cd, file_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    try:
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            lines = await f.readlines()
            if start_line < 0 or start_line >= len(lines):
                raise HTTPException(status_code=400, detail="Invalid start line index")
            return {"lines": lines[start_line : start_line + num_lines]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Read error: {str(e)}")

@router.post("/read-file")
async def get_file(request: ReadFileRequest):
    """API to read a file (filepath provided in request body)."""
    content = await read_file(request.filepath)
    return {"content": content}

@router.post("/write-file")
async def write_file(request: WriteFileRequest):
    """Writes content to a file."""
    return await make_file(request.filepath, request.content)

@router.post("/append-file")
async def append_file(request: AppendFileRequest):
    """Appends content to the end of a file in batch mode."""
    return await append_to_file(request.filepath, request.content)

@router.post("/read-lines")
async def read_lines(request: ReadLinesRequest):
    """Reads a specific number of lines from a file starting from a given index."""
    return await read_lines_from_file(request.filepath, request.start_line, request.num_lines)