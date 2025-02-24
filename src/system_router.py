import subprocess
import pyautogui
from pydantic import BaseModel
import asyncio
import os
from logger import get_logger
import threading
import uuid
import atexit
from fastapi import APIRouter, HTTPException

# Configure logging
logger = get_logger()
router = APIRouter()

running_processes = {}

class CDRequest(BaseModel):
    directory: str

class CommandRequest(BaseModel):
    command: str

class MouseAction(BaseModel):
    x: int
    y: int
    action: str  # "click", "doubleclick", "rightclick"

class KeyboardAction(BaseModel):
    key: str  # Example: "enter", "ctrl+c"

@router.post("/set-current-directory")
async def change_current_directory(request: CDRequest):
    '''Changes the current working directory.'''
    if not os.path.exists(request.directory):
        raise HTTPException(status_code=400, detail="Invalid directory path")
    os.chdir(request.directory)  # Change the working directory
    logger.info(f"Current directory changed to {request.directory}")
    return {"message": f"Current directory changed to {request.directory}"}

@router.post("/get-current-directory")
async def return_current_directory():
    '''Returns the current working directory.'''
    return {"message": f"The current working directory is {os.getcwd()}"}

@router.post("/run-command") 
async def run_terminal_command(request: CommandRequest):
    '''Runs a terminal command asynchronously to prevent timeouts.'''
    try:
        process = await asyncio.create_subprocess_shell(
            request.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        logger.info(f"Executed command: {request.command} | Output: {stdout.decode().strip()} | Error: {stderr.decode().strip()}")
        return {"input": request.command, "output": stdout.decode(), "error": stderr.decode()}
    except Exception as e:
        logger.error(f"Command execution failed: {request.command} | Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Command execution error: {str(e)}")

def run_long_command(command, process_id):
    """Executes a command and saves the output to the process dictionary."""
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    running_processes[process_id] = process
    try:
        stdout, stderr = process.communicate()
        running_processes[process_id] = {"stdout": stdout, "stderr": stderr, "completed": True}
    except Exception as e:
        running_processes[process_id] = {"stdout": "", "stderr": f"Error: {str(e)}", "completed": False}
    logger.info(f"Long-running command: {command} | Output: {stdout.strip()} | Error: {stderr.strip()}")

def cleanup_processes():
    """Terminates all running subprocesses on exit."""
    for process_id, process in running_processes.items():
        if isinstance(process, subprocess.Popen):
            process.terminate()
            process.wait()
    logger.info("All running subprocesses have been cleaned up.")

# Register cleanup function to run when the script exits
atexit.register(cleanup_processes)

@router.post("/run-long-command")
async def run_long_terminal_command(request: CommandRequest):
    """Starts a long-running command and returns a process ID."""
    process_id = str(uuid.uuid4())
    thread = threading.Thread(target=run_long_command, args=(request.command, process_id), daemon=True)
    thread.start()
    return {"message": "Command started", "process_id": process_id}

@router.post("/check-command-status/{process_id}")
async def check_command_status(process_id: str):
    """Checks the status of a running command."""
    if process_id not in running_processes:
        raise HTTPException(status_code=404, detail="Process not found")
    return running_processes[process_id]

@router.post("/mouse")
async def control_mouse(action: MouseAction):
    """Controls mouse movement & clicks."""
    pyautogui.moveTo(action.x, action.y)
    if action.action == "click":
        pyautogui.click()
    elif action.action == "doubleclick":
        pyautogui.doubleClick()
    elif action.action == "rightclick":
        pyautogui.rightClick()
    return {"status": "success"}

@router.post("/keyboard")
async def control_keyboard(action: KeyboardAction):
    """Simulates keyboard input."""
    pyautogui.press(action.key)
    return {"status": "success"}
