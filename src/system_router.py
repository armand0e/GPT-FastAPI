import subprocess
import pyautogui
from pydantic import BaseModel
import asyncio
import os
import platform
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

router = APIRouter()

current_directory = os.curdir

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
    global current_directory
    
    if not os.path.exists(request.directory):
        raise HTTPException(status_code=400, detail="Invalid directory path")

    current_directory = request.directory
    return {"message": f"Current directory changed to {current_directory}"}

@router.get("/get-current-directory")
async def return_current_directory():
    global current_directory
    return {"message": f"The current working directory is {current_directory}"}

@router.post("/run-command") 
async def run_terminal_command(request: CommandRequest):
    '''Runs a terminal command in the current directory'''
    global current_directory
    try:
        command = f"cd {current_directory} && {request.command}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return {"input": request.command, "output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"error": str(e)}

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
