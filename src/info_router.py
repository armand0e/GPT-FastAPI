from fastapi import APIRouter
from dotenv import load_dotenv
import platform
import os
import shutil
import psutil
import torch
import subprocess
import socket
import time
from datetime import timedelta

router = APIRouter()
load_dotenv()

def get_uptime():
    """Returns system uptime in a human-readable format."""
    uptime_seconds = time.time() - psutil.boot_time()
    return str(timedelta(seconds=int(uptime_seconds)))

@router.post("/info")
async def get_host_info():
    """Returns detailed system information about the host machine."""
    system_info = {
        "system": platform.system(),
        "architecture": platform.machine(),
        "version": platform.version(),
        "cpu": platform.processor(),
        "cpu_cores": psutil.cpu_count(logical=False),
        "cpu_threads": psutil.cpu_count(logical=True),
        "total_ram": f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB",
        "available_ram": f"{round(psutil.virtual_memory().available / (1024 ** 3), 2)} GB",
        "disk_usage": f"{shutil.disk_usage('/').free // (1024**3)} GB free",
        "python_version": platform.python_version(),
        "shell": os.getenv("SHELL", "unknown"),
        "hostname": socket.gethostname(),
        "uptime": get_uptime(),
    }

    # Detect if running on WSL2 and add Windows system details
    if "WSL2" in platform.release():
        try:
            import subprocess
            windows_info = subprocess.run(["powershell.exe", "systeminfo"], capture_output=True, text=True)
            system_info["windows_system_info"] = windows_info.stdout
        except Exception:
            system_info["windows_system_info"] = "Unable to retrieve Windows system info"

    return system_info

@router.post("/host-resources")
async def get_host_resources():
    """Returns system resource usage (CPU, RAM, Disk)."""
    return {
        "cpu_usage": psutil.cpu_percent(interval=1),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage("/").percent,
        "uptime": get_uptime()
    }
