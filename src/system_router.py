import subprocess
import pyautogui
from pydantic import BaseModel
import asyncio
import os
from logger import get_logger
import threading
import uuid
import atexit
import select
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
    '''Runs a terminal command.'''
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

def cleanup_processes():
    """Terminates all running subprocesses on exit."""
    for process_id, process in running_processes.items():
        if isinstance(process, subprocess.Popen):
            process.terminate()
            process.wait()
    logger.info("All running subprocesses have been cleaned up.")

# Register cleanup function to run when the script exits
atexit.register(cleanup_processes)
def run_long_command(command, process_id):
    # Start the subprocess with stdout piped and in text mode.
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    output_buffer = []  # List to store output lines
    running_processes[process_id] = {"process": process, "output_buffer": output_buffer}

    # Define a function to continuously read output.
    def read_output():
        try:
            # Read line by line until the process ends.
            for line in process.stdout:
                output_buffer.append(line)
        except Exception as e:
            output_buffer.append(f"Error reading output: {e}")
        finally:
            if process.stdout:
                process.stdout.close()

    # Start the output reader in a daemon thread.
    output_thread = threading.Thread(target=read_output, daemon=True)
    output_thread.start()

    # Wait for the process to complete.
    process.wait()

@router.post("/start-process")
async def start_process(request: CommandRequest):
    """Starts a long-running process and returns a process ID."""
    process_id = str(uuid.uuid4())
    thread = threading.Thread(target=run_long_command, args=(request.command, process_id), daemon=True)
    thread.start()
    return {"message": "Process started", "process_id": process_id}

@router.post("/stop-process/{process_id}")
async def stop_process(process_id: str):
    """Stops a running process given its process ID."""
    if process_id not in running_processes:
        raise HTTPException(status_code=404, detail="Process not found")
    
    proc_info = running_processes[process_id]
    process = proc_info.get("process")
    
    if isinstance(process, subprocess.Popen):
        process.terminate()
        process.wait()
        del running_processes[process_id]
        return {"message": "Process stopped successfully"}
    
    return {"message": "Process already completed or not found"}

@router.post("/check-process-status/{process_id}")
async def check_process_status(process_id: str):
    """Checks the status of a running process and returns live output."""
    if process_id not in running_processes:
        raise HTTPException(status_code=404, detail="Process not found")

    proc_info = running_processes[process_id]
    process = proc_info.get("process")
    output_buffer = proc_info.get("output_buffer", [])

    # Determine if the process is still running.
    if process and process.poll() is None:
        status_message = "Process is still running"
        completed = False
    else:
        status_message = "Process completed"
        completed = True

    # Return the accumulated output as a single string.
    output = "".join(output_buffer) if output_buffer else "No output yet."
    return {"message": status_message, "output": output, "completed": completed}

@router.post("/list-running-processes")
async def list_processes():
    """Lists running processes on the system."""
    process_list = []
    for process_id, proc_info in running_processes.items():
        process_list.append({"process_id": process_id, "status": "running" if proc_info.get("process").poll() is None else "completed"})
    return {"processes": process_list}

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