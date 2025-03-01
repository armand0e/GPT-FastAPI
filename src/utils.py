"""Utility functions for file handling, text replacements, and logging."""
import os
import aiofiles
import ast
from pathlib import Path


# Helper function for cross-platform path handling
def resolve_path(filepath: str) -> Path:
    """Resolves a file path for cross-platform compatibility."""
    path = Path(filepath).resolve()
    if os.name == "nt" and "WSL2" in os.uname().release:
        return Path("/mnt/" + path.drive.lower().replace(':', '') + path.as_posix()[2:])
    return path


async def read_file(file_path: str):
    """Reads the content of a file asynchronously."""
    resolved_path = resolve_path(file_path)
    if not resolved_path.exists():
        return {"error": "File not found"}

    try:
        async with aiofiles.open(resolved_path, "r", encoding="utf-8") as f:
            content = await f.read()
        return {"file": str(resolved_path), "content": content}
    except Exception as e:
        return {"error": f"Read error: {str(e)}"}


async def write_file(file_path: str, content: str):
    """Writes content to a file asynchronously."""
    resolved_path = resolve_path(file_path)
    try:
        async with aiofiles.open(resolved_path, "w", encoding="utf-8") as f:
            await f.write(content)
        return {"message": f"File '{resolved_path}' saved successfully"}
    except Exception as e:
        return {"error": f"Write error: {str(e)}"}


async def append_file(file_path: str, content):
    """Appends content to a file asynchronously."""
    resolved_path = resolve_path(file_path)
    if not resolved_path.exists():
        return {"error": "File not found"}

    try:
        async with aiofiles.open(resolved_path, "a", encoding="utf-8") as f:
            if isinstance(content, list):
                await f.writelines([line + "\n" for line in content])
            else:
                await f.write(content + "\n")
        return {"message": f"Content appended to '{resolved_path}' successfully"}
    except Exception as e:
        return {"error": f"Append error: {str(e)}"}


async def read_lines(file_path: str, start_line: int, num_lines: int):
    """Reads a specified number of lines from a file starting at a given line."""
    resolved_path = resolve_path(file_path)
    if not resolved_path.exists():
        return {"error": "File not found"}

    try:
        async with aiofiles.open(resolved_path, "r", encoding="utf-8") as f:
            lines = await f.readlines()
        if start_line < 0 or start_line >= len(lines):
            return {"error": "Invalid start line index"}
        return {"lines": lines[start_line : start_line + num_lines]}
    except Exception as e:
        return {"error": f"Read error: {str(e)}"}


async def read_logs():
    """Reads the last the log file, preserving order."""
    log_path = resolve_path("logs/system.log")
    if not log_path.exists():
        return {"error": "Log file not found"}
    try:
        async with aiofiles.open(log_path, "r", encoding="utf-8") as f:
            lines = await f.readlines()
        lines ="\n".join(lines)
        return {"logs": lines}
    except Exception as e:
        return {"error": f"Log read error: {str(e)}"}
    
    
async def replace_text(file_path: str, original_text: str, replacement_text: str):
    """Replaces original text with updated text within a specified file."""
    file_data = await read_file(file_path)
    if "error" in file_data:
        return {"error": "File not found"}
    content = file_data["content"]
    if original_text not in content:
        return {"error": "Original text not found in the file"}
    new_content = content.replace(original_text, replacement_text)
    return await write_file(file_path, new_content)


async def replace_function(file_path: str, function_name: str, new_function_code: str):
    """Replaces a function definition in a Python file with a new one."""
    file_data = await read_file(file_path)
    if "error" in file_data:
        return {"error": "File not found"}
    content = file_data["content"]
    try:
        tree = ast.parse(content)
    except Exception as e:
        return {"error": f"Error parsing source file: {str(e)}"}
    try:
        new_tree = ast.parse(new_function_code)
        new_func_node = next((node for node in new_tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))), None)
        if not new_func_node:
            return {"error": "No function definition found in new_function_code"}
    except Exception as e:
        return {"error": f"Error parsing new function code: {str(e)}"}
    from helpers import FunctionReplacer
    replacer = FunctionReplacer(function_name, new_func_node)
    modified_tree = replacer.visit(tree)
    ast.fix_missing_locations(modified_tree)
    if not replacer.replaced:
        return {"error": f"Function '{function_name}' not found in the source file."}
    try:
        new_source = ast.unparse(modified_tree)
    except Exception as e:
        try:
            import astunparse
            new_source = astunparse.unparse(modified_tree)
        except ImportError:
            return {"error": "ast.unparse not available and astunparse is not installed"}
    return await write_file(file_path, new_source)


async def read_func(filepath: str, function_name: str):
    file_data = await read_file(filepath)
    if "error" in file_data:
        return {"error": "File not found"}
    
    content = file_data["content"]
    try:
        tree = ast.parse(content)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
                return {"function_name": function_name, "source_code": ast.unparse(node)}
        
        return {"error": f"Function '{function_name}' not found in {filepath}"}
    except Exception as e:
        return {"error", f"Error parsing file: {str(e)}"}