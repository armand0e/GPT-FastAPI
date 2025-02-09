import aiofiles
import os
import hashlib
import shutil
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel

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

async def write_file(file_path: str, content: str):
    """Writes content to a file safely, ensuring encoding and avoiding corruption."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure directory exists

    try:
        async with aiofiles.open(file_path, "w", encoding="utf-8", newline="\n") as f:
            await f.write(content)
            await f.flush()  # Ensure content is fully written
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Write error: {str(e)}")

    return {"message": f"File '{file_path}' saved successfully"}
    
async def read_file(filepath: str):
    """Reads a file asynchronously, handling encoding and permission errors."""
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"File not found: {filepath}")

    try:
        async with aiofiles.open(filepath, mode="r", encoding="utf-8") as f:
            return await f.read()
    except PermissionError:
        raise HTTPException(status_code=403, detail=f"Permission denied: {filepath}")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail=f"Encoding issue: Cannot read {filepath} as UTF-8.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
@router.post("/api/read-file")
async def get_file(request: ReadFileRequest):
    """API to read a file (filepath provided in request body)."""
    content = await read_file(request.filepath)
    return {"content": content}

@router.post("/api/write-file")
async def write_file_api(request: WriteFileRequest):
    """Writes content to a file."""
    return await write_file(request.filepath, request.content)

@router.post("/api/list-files")
async def list_files(request: ListFilesRequest):
    """Lists all files in the specified directory. Expects request body."""
    if not os.path.exists(request.directory) or not os.path.isdir(request.directory):
        raise HTTPException(status_code=404, detail="Directory not found")
    try:
        files = os.listdir(request.directory)
        return {"directory": request.directory, "files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@router.post("/api/file-metadata")
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

