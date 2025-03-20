import asyncio
import os
import uuid
import json
import subprocess
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from rich.console import Console

console = Console()
router = APIRouter()

SESSION_FILE = '/mnt/c/Users/aranr/Documents/Github/GPT-FastAPI/shell_sessions.json'

def save_sessions(shells):
    """Save active shell sessions to a file."""
    try:
        with open(SESSION_FILE, 'w') as f:
            json.dump(shells, f)
    except Exception as e:
        console.log(f"[red]Failed to save shell sessions:[/red] {e}")

def load_sessions():
    """Load active shell sessions from a file."""
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            console.log(f"[red]Failed to load shell sessions:[/red] {e}")
    return {}

class ShellManager:
    def __init__(self):
        self.shells = load_sessions()

    def start_shell(self, shell_name='bash'):
        shell_id = str(uuid.uuid4())
        process = subprocess.Popen(shell_name, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        self.shells[shell_id] = {
            "shell_name": shell_name,
            "pid": process.pid
        }
        save_sessions(self.shells)
        console.log(f"[green]Started shell:[/green] {shell_id}")
        return shell_id

    def execute_command(self, shell_id: str, command: str):
        if shell_id not in self.shells:
            raise HTTPException(status_code=404, detail="Shell session not found")
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        return {"stdout": stdout, "stderr": stderr}

    def stop_shell(self, shell_id: str):
        if shell_id in self.shells:
            try:
                os.kill(self.shells[shell_id]["pid"], 9)
                del self.shells[shell_id]
                save_sessions(self.shells)
                console.log(f"[red]Stopped shell:[/red] {shell_id}")
                return {"message": "Shell stopped"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        raise HTTPException(status_code=404, detail="Shell session not found")

shell_manager = ShellManager()

@router.post('/start-shell')
def start_shell(shell_name: str = 'bash'):
    shell_id = shell_manager.start_shell(shell_name)
    return {"message": "Shell started", "shell_id": shell_id}

@router.post('/execute')
def execute_command(shell_id: str, command: str):
    return shell_manager.execute_command(shell_id, command)

@router.post('/stop-shell/{shell_id}')
def stop_shell(shell_id: str):
    return shell_manager.stop_shell(shell_id)