import asyncio
import os
import subprocess
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import time
import log_handler

router = APIRouter()

class CommandRequest(BaseModel):
    command: str
    
class LogRequest(BaseModel):
    num_commands: int

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
            shell = None  # Mark shell as inactive
            raise HTTPException(status_code=500, detail=f"Failed to start shell: {str(e)}")

async def get_shell_cwd():
    """Gets the current working directory inside the persistent shell."""
    global shell
    if shell is None:
        return "/unknown"

    shell.stdin.write("pwd\n")
    shell.stdin.flush()
    return shell.stdout.readline().strip()  # Read the directory from shell output

router = APIRouter()

class CommandRequest(BaseModel):
    command: str

async def run_command(command: str, timeout: int = 10):
    """Executes a command inside the persistent shell and captures output directly from stdout."""
    global shell
    if shell is None:
        await start_shell()
    if shell is None:
        return {"error": "Shell is not running"}

    if shell.stdin is None or shell.stdout is None:
        raise HTTPException(status_code=500, detail="Shell process not initialized properly.")

    try:
        # Mark the end of command output
        end_marker = "COMMAND_DONE"

        # Send command and add a marker to detect the end
        shell.stdin.write(f"{command}; echo {end_marker}\n")
        shell.stdin.flush()

        output_lines = []
        start_time = time.time()

        while time.time() - start_time < timeout:
            line = shell.stdout.readline().strip()

            if line:
                if line == end_marker:
                    break  # Stop reading when marker is reached
                output_lines.append(line)

        output_text = "\n".join(output_lines) if output_lines else "No output"

        # Special handling for `cd` – Update shell working directory
        if command.startswith("cd "):
            shell.stdin.write("pwd\n")
            shell.stdin.flush()
            new_cwd = shell.stdout.readline().strip()
        else:
            new_cwd = await get_shell_cwd()

        # Log the command and its output
        log_handler.log_command(new_cwd, command, output_text)

        return {"cwd": new_cwd, "output": output_text}

    except Exception as e:
        return {"error": str(e)}
    
@router.post("/api/run-terminal")
async def run_terminal_script(request: CommandRequest):
    """Executes a command in the persistent shell and logs output."""
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

@router.post("/api/check-shell-status")
async def check_shell_status():
    """Checks if a shell session is active."""
    global shell
    return {"shell_running": shell is not None and shell.poll() is None}

@router.post("/api/get-logs")
async def get_recent_logs(request: LogRequest):
    """
    Returns the logs for the last `num_commands` commands from the shell.log.
    If `num_commands` is greater than available logs, it returns all logs.
    """
    try:
        with open("shell.log", "r") as f:
            lines = f.readlines()
        
        if not lines:
            return {"logs": []}  # No logs available

        logs = []
        command_log = []
        command_dict = {}
        command_count = 0

        # Process logs from newest to oldest
        for line in reversed(lines):
            clean_line = line.strip()
            if "COMMAND:" in clean_line:
                command_dict["command"] = clean_line.replace("COMMAND: ", "")

            elif "PWD:" in clean_line:
                command_dict["cwd"] = clean_line.replace("PWD: ", "")

            elif "OUTPUT:" in clean_line:
                command_dict["output"] = "\n".join(command_log).strip()
                command_log = []  # Reset output capture

            elif "- INFO -" in clean_line:
                # Extract the timestamp from the log entry
                timestamp = clean_line.split(" - INFO - ")[0]
                command_dict["timestamp"] = timestamp

            elif "--------------------------------------------------" in clean_line:
                # Finished processing one command's log
                logs.insert(0, command_dict)
                command_dict = {}
                command_count += 1

                # Stop when we reach the requested number of logs
                if command_count >= request.num_commands:
                    break
            else:
                command_log.append(clean_line)  # Capture output lines

        # If not enough logs, return as many as available
        return {"logs": logs}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading logs: {str(e)}")

async def close_shell():
    """Gracefully closes the shell when FastAPI shuts down."""
    global shell
    if shell is not None and shell.poll() is None:
        shell.terminate()
        shell = None
        print("✅ Shell closed on server shutdown")
