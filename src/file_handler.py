import dotenv
from fastapi import APIRouter, HTTPException
from utils import (
    read_file, write_file, append_file, replace_func, replace_text,
    read_lines as utils_read_lines, read_logs, read_func
)
from schemas import (
    WriteFileRequest, AppendFileRequest, ReadFileRequest, ReadLinesRequest,
    ReplaceFunctionRequest, ReplaceTextRequest, ReadFuncRequest
)

router = APIRouter()

@router.post("/replace-function")
async def replace_function(req: ReplaceFunctionRequest):
    """
    Replaces the definition of a function in the specified file.
    """
    result = await replace_func(req.filepath, req.function_name, req.new_function_code)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/replace-text")
async def replace_text_endpoint(req: ReplaceTextRequest):
    """
    Replaces a specific text snippet with new text in the file.
    """
    result = await replace_text(req.filepath, req.original_text, req.replacement_text)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/read-file")
async def get_file(request: ReadFileRequest):
    """
    Reads the content of the specified file.
    """
    result = await read_file(request.filepath)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.post("/write-file")
async def write_file_endpoint(request: WriteFileRequest):
    """
    Writes new content to the specified file.
    """
    result = await write_file(request.filepath, request.content)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@router.post("/append-file")
async def append_file_endpoint(request: AppendFileRequest):
    """
    Appends content to the specified file.
    """
    result = await append_file(request.filepath, request.content)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/read-lines")
async def read_file_lines_endpoint(request: ReadLinesRequest):
    """
    Reads a specified number of lines from the file, starting from a given line index.
    """
    result = await utils_read_lines(request.filepath, request.start_line, request.num_lines)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/read-logs")
async def read_shell_logs():
    """
    Reads the contents of the system log file.
    """
    result = await read_logs()
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.post("/read-function")
async def read_function(request: ReadFuncRequest):
    """
    Reads the source code of a specific function from a Python file.
    """
    result = await read_func(request.filepath, request.function_name)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
