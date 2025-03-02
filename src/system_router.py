import subprocess
import asyncio
import atexit
from pathlib import Path
from fastapi import APIRouter, HTTPException, WebSocket
from logger import get_logger
from schemas import CommandRequest
from helpers import ShellManager
# Configure logging
logger = get_logger()
router = APIRouter()

running_shells = {}

shell_manager = ShellManager()  # Global instance

@router.post("/execute")
async def execute_command(request: CommandRequest, shell_id: int = 0):
    """Executes a command in a persistent shell. Defaults to shell ID 1."""
    try:
        shell = shell_manager.get_shell(shell_id) if shell_id else shell_manager.get_shell(1)
        if not shell or not shell.process or shell.process.stdin is None:
            raise HTTPException(status_code=500, detail="Shell is not running")
        
        # Send command to the selected shell
        shell.process.stdin.write((request.command + "\n").encode())
        await shell.process.stdin.drain()
        
        stdout, stderr = await asyncio.gather(
            shell.process.stdout.read(),
            shell.process.stderr.read()
        )
        
        output = stdout.decode().strip()
        error = stderr.decode().strip()

        if output:
            return {"message": f"Command executed in shell {shell.shell_id} ({shell.name})", "output": output}
        else:
            return {"error": error}
                
    except asyncio.TimeoutError:
        # Process is running for more than 5 seconds, kill the process in bash and start background process
        bash_process.stdin.write(b"\x03")  # Ctrl+C (ASCII 0x03)
        await bash_process.stdin.drain()
        bash_process.
        

        process_name = " ".join(request.command.split()[:3])[:30]  # Take first 3 words, limit to 30 chars
        process_id = process_manager.add_process(name=process_name, command=request.command, process=process)
        return {"message": "Command was executed in an external session", "process_id": process_id}

    except Exception as e:
        logger.error(f"Command execution failed: {request.command} | Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Command execution error: {str(e)}")

@router.post("/send-input/{process_id}")
async def send_process_input(process_id: int, input_text: str):
    """Sends input (stdin) to a running process (given process_id)"""
    process_info = process_manager.get_process(process_id)
    if not process_info:
        raise HTTPException(status_code=404, detail="Process not found")
    
    process = process_info["process"]
    if process.stdin is None:
        raise HTTPException(status_code=400, detail="Process does not accept input")
    
    try:
        process.stdin.write((input_text + "\n").encode())
        await process.stdin.drain()
        return {"message": "Input sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send input: {str(e)}")

@router.post("/kill-process/{process_id}")
async def stop_process(process_id: int):
    """Stops a running process given its process ID."""
    process_info = process_manager.get_process(process_id)
    if not process_info:
        raise HTTPException(status_code=404, detail="Process not found")
    
    if process_info["name"] == "bash":
        raise HTTPException(status_code=403, detail="Cannot kill the persistent shell")
    
    process = process_info["process"]
    try:
        process.terminate()
        await process.wait()
        process_manager.remove_process(process_id)
        return {"message": "Process stopped successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop process: {str(e)}")

@router.get("/list-processes")
async def list_processes():
    """Returns a list of all running processes."""
    processes = [{"id": pid, "name": info["name"], "command": info["command"]} 
             for pid, info in process_manager.processes.items() 
             if info["name"] != "bash"]  # Exclude persistent shell
    return {"running_processes": processes}

@router.websocket("/ws/shell/{shell_id}")
async def websocket_shell_status(websocket: WebSocket, shell_id: int):
    """Streams live output from a persistent shell."""
    await websocket.accept()

    shell = shell_manager.get_shell(shell_id)
    if not shell:
        await websocket.send_text("Error: Shell not found")
        await websocket.close()
        return

    while shell.process and shell.process.returncode is None:
        try:
            line = await shell.process.stdout.readline()
            if not line:
                break
            await websocket.send_text(line.decode().strip())
        except Exception as e:
            await websocket.send_text(f"Error reading shell output: {str(e)}")
            break
        await asyncio.sleep(0.5)

    await websocket.send_text("Shell session closed.")
    await websocket.close()

@router.get("/check-process/{process_id}")
async def check_process(process_id: int):
    """Returns the latest output of a running process by reading from the WebSocket."""
    process_info = process_manager.get_process(process_id)
    if not process_info:
        raise HTTPException(status_code=404, detail="Process not found")
    
    process = process_info["process"]
    output_lines = []

    try:
        while process and process.returncode is None:
            line = await process.stdout.readline()
            if not line:
                break
            output_lines.append(line.decode().strip())
        return {"process_id": process_id, "output": output_lines}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving process output: {str(e)}")

# Start a persistent bash shell
async def start_persistent_shell():
    """Starts a global bash process for persistent command execution."""
    global bash_process
    bash_process = await asyncio.create_subprocess_exec(
        "bash",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    if not bash_process:
        raise RuntimeError("Failed to start persistent bash shell")

# Ensure bash starts when the API boots
asyncio.create_task(start_persistent_shell())

def cleanup_processes():
    """Terminates all running subprocesses on exit."""
    for process_id, process in running_processes.items():
        if isinstance(process, subprocess.Popen):
            process.terminate()
            process.wait()
    logger.info("All running subprocesses have been cleaned up.")
# Register cleanup function to run when the script exits
atexit.register(cleanup_processes)

@router.get("/check-shell/{shell_id}")
async def check_shell(shell_id: int):
    """Returns the latest output from a persistent shell."""
    shell = shell_manager.get_shell(shell_id)
    if not shell:
        raise HTTPException(status_code=404, detail="Shell not found")
    
    output_lines = []
    try:
        while shell.process and shell.process.returncode is None:
            line = await shell.process.stdout.readline()
            if not line:
                break
            output_lines.append(line.decode().strip())
        return {"shell_id": shell_id, "output": output_lines}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving shell output: {str(e)}")
