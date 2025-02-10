import json
import os
from pydantic import BaseModel
import aiofiles
from fastapi import APIRouter, HTTPException

router = APIRouter()

class WriteFileRequest(BaseModel):
    filepath: str
    content: str

class ReadFileRequest(BaseModel):
    filepath: str

class ListFilesRequest(BaseModel):
    directory: str

class FileMetadataRequest(BaseModel):
    filepath: str


async def read_file(file_path):
    if not os.path.exists(file_path):
        return json.dumps({"error": "File not found"})
    with open(file_path, "r", encoding="utf-8") as f:
        return json.dumps({"file": file_path, "content": f.read()})

async def make_file(file_path, content):
    try:
        async with aiofiles.open(file_path, "w", encoding="utf-8", newline="\n") as f:
            await f.write(content)
            await f.flush()  # Ensure content is fully written
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Write error: {str(e)}")

    return {"message": f"File '{file_path}' saved successfully"}

@router.post("/read-file")
async def get_file(request: ReadFileRequest):
    """API to read a file (filepath provided in request body)."""
    content = await read_file(request.filepath)
    return {"content": content}

@router.post("/write-file")
async def write_file(request: WriteFileRequest):
    """Writes content to a file."""
    return await make_file(request.filepath, request.content)

@router.post("/list_file")
async def list_files(request: ListFilesRequest):
    """Lists all files in the specified directory. Expects request body."""
    if not os.path.exists(request.directory) or not os.path.isdir(request.directory):
        raise HTTPException(status_code=404, detail="Directory not found")
    try:
        files = os.listdir(request.directory)
        return {"directory": request.directory, "files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@router.post("/file-metadata")
async def file_metadata(request: FileMetadataRequest):
    """Retrieves metadata such as size and modification date for a given file. Expects request body."""
    if not os.path.exists(request.filepath):
        raise HTTPException(status_code=404, detail="File not found")

    file_stat = os.stat(request.filepath)
    return {
        "filepath": request.filepath,
        "size_bytes": file_stat.st_size,
        "last_modified": file_stat.st_mtime,
    }
