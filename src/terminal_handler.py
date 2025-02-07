import asyncio
import platform
import os
import subprocess
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import time
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
            raise HTTPException(status_code=500, detail=f"Failed to start shell: {str(e)}")

async def run_command(command: str, timeout: int = 10):
    """Execute a shell command safely without blocking."""
    global shell
    if shell is None:
        await start_shell()

    if shell.stdin is None or shell.stdout is None:
        raise HTTPException(status_code=500, detail="Shell process not initialized properly.")

    try:
        # Send command to shell
        shell.stdin.write(command + "\n")
        shell.stdin.flush()

        # Read output in real-time (non-blocking)
        output_lines = []
        start_time = time.time()

        while time.time() - start_time < timeout:
            line = shell.stdout.readline().strip()
            if line:
                output_lines.append(line)
            else:
                break  # Exit loop when no more output

        if not output_lines:
            return {"error": "No output received"}

        return {"output": "\n".join(output_lines)}
    
    except asyncio.TimeoutError:
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
