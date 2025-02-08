import asyncio
import platform
import os
import subprocess
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import time
from log_handler import log
router = APIRouter()

class CommandRequest(BaseModel):
    command: str

shell = None  # Persistent shell process


async def start_shell():
    """Start a persistent shell session if not already running."""
    global shell

    shell_cmd = [os.getenv("SHELL", "/bin/bash")]

    if shell is None or shell.poll() is not None:  # Ensure shell is running
        try:
            shell = subprocess.Popen(
                shell_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
        except Exception as e:
            print(f'Failed to start shell: {e}')
            shell = None  # Mark shell as inactive
            raise HTTPException(status_code=500, detail=f"Failed to start shell: {str(e)}")

async def run_command(command: str, timeout: int = 15):
    """Executes a command inside the persistent shell and returns the output."""
    global shell
    if shell is None:
        await start_shell()
    if shell is None:
        return {"error": "Shell is not running"}

    if shell.stdin is None or shell.stdout is None:
        raise HTTPException(status_code=500, detail="Shell process not initialized properly.")

    try:
        # Redirect output to a temporary file
        temp_file = "./tmp/shell_output.txt"
        # Write the command and ensure "DONE" is written at the end
        shell.stdin.write(f"{command} > {temp_file} 2>&1; echo DONE >> {temp_file}\n")
        shell.stdin.flush()

        # Wait for the command to complete
        start_time = time.time()
        while time.time() - start_time < timeout:
            with open(temp_file, "r") as f:
                output = f.read().strip()
                if "DONE" in output:
                    return {"output": output.replace("DONE", "").strip()}
            await asyncio.sleep(0.1)  # Non-blocking wait

        return {"error": f"Command timed out after {timeout} seconds"}

    except Exception as e:
        return {"error": str(e)}


@router.post("/api/run-terminal")
async def run_terminal_script(request: CommandRequest):
    """Executes a command in Git Bash (Windows) or standard shell (Linux/macOS)."""
    output = await run_command(request.command)
    return output

@router.post("/api/interrupt-terminal")
async def interrupt_terminal():
    """Interrupts the active shell process."""
    global shell
    if shell and shell.poll() is None:
        shell.terminate()
        shell = None
        return {"message": "Shell session terminated"}
    return {"message": "No shell session running"}

@router.get("/api/check-shell-status")
async def check_shell_status():
    """Checks if a shell session is active."""
    global shell
    return {"shell_running": shell is not None and shell.poll() is None}

async def close_shell():
    """Gracefully closes the shell when FastAPI shuts down."""
    global shell
    if shell is not None and shell.poll() is None:
        shell.terminate()
        shell = None
        print("✅ Shell closed on server shutdown")
