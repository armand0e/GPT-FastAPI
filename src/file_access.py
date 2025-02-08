import aiofiles
import os
import hashlib
import shutil
from thefuzz import fuzz
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel

router = APIRouter()

class WriteFileRequest(BaseModel):
    filepath: str
    content: str

class ReadFileRequest(BaseModel):
    filepath: str

class FuzzySearchRequest(BaseModel):
    filepath: str
    query: str

class ListFilesRequest(BaseModel):
    directory: str

class FileMetadataRequest(BaseModel):
    filepath: str

async def write_file(file_path: str, content: str):
    async with aiofiles.open(file_path, "w") as f:
        await f.write(content)
    return {"message": f"File '{file_path}' saved successfully"}

async def read_file(filepath: str):
    """Reads a file asynchronously with UTF-8 encoding."""
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"File not found: {filepath}")
    try:
        async with aiofiles.open(filepath, mode="r", encoding="utf-8") as f:
            return await f.read()
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail=f"Encoding issue: Cannot read file {filepath} as UTF-8.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
async def fuzzy_search(filepath: str, query: str):
    """Search for a query inside a file asynchronously."""
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"File not found: {filepath}")

    matches = []
    try:
        async with aiofiles.open(filepath, mode="r", encoding="utf-8") as f:
            async for line in f:
                if query.lower() in line.lower():
                    matches.append(line.strip())
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail=f"Encoding issue: Cannot read file {filepath} as UTF-8.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    return matches

@router.post("/api/read-file")
async def get_file(request: ReadFileRequest):
    """API to read a file (filepath provided in request body)."""
    content = await read_file(request.filepath)
    return {"content": content}

@router.post("/api/write-file")
async def write_file_api(request: WriteFileRequest):
    """Writes content to a file."""
    return await write_file(request.filepath, request.content)

@router.post("/api/fuzzy-search-file")
async def fuzzy_search_file(request: FuzzySearchRequest):
    """API for fuzzy searching inside a file. Expects filepath & query in the body."""
    matches = await fuzzy_search(request.filepath, request.query)
    return {"matches": matches}

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

