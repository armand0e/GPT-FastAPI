import json
import os
import dotenv
from pydantic import BaseModel
import aiofiles
from logger import get_logger, LOG_DIR
from fastapi import APIRouter, HTTPException

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
    start_line: int = 0
    num_lines: int = 10  # Default to reading last 10 lines

@router.post("/read-log")
async def read_log(request: LogRequest):
    """Reads a snippet from the specified log file."""
    log_path = os.path.join(LOG_DIR, "system.log")  # Use absolute path

    if not os.path.exists(log_path):
        raise HTTPException(status_code=404, detail="Log file not found")

    try:
        async with aiofiles.open(log_path, "r", encoding="utf-8") as f:
            lines = await f.readlines()  # Read all lines (async)
            total_lines = len(lines)

            # Handle negative indexing for "last N lines"
            if request.start_line < 0:
                request.start_line = max(0, total_lines + request.start_line)

            # Extract the requested lines
            snippet = lines[request.start_line : request.start_line + request.num_lines]

        return {"logs": snippet}
    
    except Exception as e:
        logger.error(f"Error reading log file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Log read error: {str(e)}")
