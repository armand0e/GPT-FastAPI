from pydantic import BaseModel

class CommandRequest(BaseModel):
    command: str
    
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

class ReplaceTextRequest(BaseModel):
    filepath: str
    original_text: str
    replacement_text: str

class ReadFuncRequest(BaseModel):
    filepath: str
    function_name: str