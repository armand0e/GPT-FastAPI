import dotenv
from fastapi import APIRouter
from logger import get_logger, LOG_DIR
from utils import read_file, write_file, append_file, replace_function_logic, replace_text_logic, read_lines, read_logs, read_func
from schemas import WriteFileRequest, AppendFileRequest, ReadFileRequest, ReadLinesRequest, ReplaceFunctionRequest, ReplaceTextRequest, ReadFuncRequest

router = APIRouter()

@router.post("/replace-function")
async def replace_function(req: ReplaceFunctionRequest):
    return await replace_function_logic(req.filepath, req.function_name, req.new_function_code)

@router.post("/replace-text")
async def replace_text(req: ReplaceTextRequest):
    return await replace_text_logic(req.filepath, req.original_text, req.replacement_text)

@router.post("/read-file")
async def get_file(request: ReadFileRequest):
    return await read_file(request.filepath)

@router.post("/write-file")
async def write_file_endpoint(request: WriteFileRequest):
    return await write_file(request.filepath, request.content)

@router.post("/append-file")
async def append_file_endpoint(request: AppendFileRequest):
    return await append_file(request.filepath, request.content)

@router.post("/read-lines")
async def read_lines(request: ReadLinesRequest):
    return await read_lines(request.filepath, request.start_line, request.num_lines)

@router.post("/read-shell-logs")
async def read_log():
    """Reads the last 5 command logs from the persistent shell"""
    return await read_logs()

@router.post("/read-function")
async def read_function(request: ReadFuncRequest):
    """Reads the source code of a specific function from a Python file."""
    return await read_func(request.filepath, request.function_name)
