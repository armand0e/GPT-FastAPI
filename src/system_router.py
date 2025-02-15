import subprocess
import pyautogui
from pydantic import BaseModel
import asyncio
import pty
import os
import platform
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

router = APIRouter()

class CommandRequest(BaseModel):
    command: str

class MouseAction(BaseModel):
    x: int
    y: int
    action: str  # "click", "doubleclick", "rightclick"

class KeyboardAction(BaseModel):
    key: str  # Example: "enter", "ctrl+c"

if platform.system() == "Windows":
    terminal = "cmd.exe"
else:
    terminal = "/bin/bash"
# Start a persistent shell session
master, slave = pty.openpty()
shell = subprocess.Popen(
    terminal,
    stdin=slave,
    stdout=slave,
    stderr=slave,
    text=True,
    bufsize=1,
    shell=True
)

async def read_output():
    """Asynchronously reads shell output in real time."""
    loop = asyncio.get_running_loop()
    while True:
        try:
            output = await loop.run_in_executor(None, os.read, master, 1024)
            if output:
                yield output.decode()
        except Exception:
            break

@router.post("/shell")
async def run_shell_command(command: CommandRequest):
    """Executes a command in the persistent shell session and streams output."""
    os.write(master, (command.command + "\n").encode())
    return StreamingResponse(read_output(), media_type="text/event-stream")

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
