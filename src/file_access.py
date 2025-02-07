import aiofiles
import os
import hashlib
import shutil
from thefuzz import fuzz
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel

router = APIRouter()

class FileWriteRequest(BaseModel):
    filepath: str
    content: str

async def read_file(file_path: str):
    async with aiofiles.open(file_path, "r") as f:
        return await f.read()

async def write_file(file_path: str, content: str):
    async with aiofiles.open(file_path, "w") as f:
        await f.write(content)
    return {"message": f"File '{file_path}' saved successfully"}

@router.get("/api/read-file")
async def get_file(filepath: str):
    """Retrieves the contents of a specified file."""
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    content = await read_file(filepath)
    return {"filepath": filepath, "content": content}

@router.post("/api/write-file")
async def write_file_api(request: FileWriteRequest):
    """Writes content to a file."""
    return await write_file(request.filepath, request.content)

@router.post("/api/fuzzy-search-file")
async def fuzzy_search(filepath: str, query: str):
    """Performs a fuzzy search within a file to find relevant lines."""
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")

    content = await read_file(filepath)
    lines = content.split("\n")
    matches = [(i, line, fuzz.ratio(query, line)) for i, line in enumerate(lines) if fuzz.ratio(query, line) > 70]

    return {"matches": matches}

@router.post("/api/upload-file")
async def upload_file(filepath: str, file: UploadFile = File(...)):
    """Uploads a file and saves it to the specified location."""
    async with aiofiles.open(filepath, "wb") as f:
        content = await file.read()
        await f.write(content)
    return {"message": f"File '{filepath}' uploaded successfully"}

@router.get("/api/list-files")
async def list_files(directory: str):
    """Lists all files in the specified directory."""
    if not os.path.exists(directory) or not os.path.isdir(directory):
        raise HTTPException(status_code=404, detail="Directory not found")
    try:
        files = os.listdir(directory)
        return {"directory": directory, "files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@router.get("/api/file-metadata")
async def file_metadata(filepath: str):
    """Retrieves metadata such as size and modification date for a given file."""
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")

    file_stat = os.stat(filepath)
    return {
        "filepath": filepath,
        "size_bytes": file_stat.st_size,
        "last_modified": file_stat.st_mtime,
    }

@router.delete("/api/delete-file")
async def delete_file(filepath: str):
    """Deletes a specified file."""
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    os.remove(filepath)
    return {"message": f"File '{filepath}' deleted successfully"}

@router.delete("/api/delete-directory")
async def delete_directory(directory: str):
    """Deletes an entire directory and all its contents."""
    if not os.path.exists(directory):
        raise HTTPException(status_code=404, detail="Directory not found")
    if not os.path.isdir(directory):
        raise HTTPException(status_code=400, detail="Path is not a directory")
    shutil.rmtree(directory)
    return {"message": f"Directory '{directory}' deleted successfully"}
