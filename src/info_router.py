from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
import platform
import os
import shutil
import psutil
import socket

router = APIRouter()
load_dotenv()

@router.post("/info")
async def get_host_info():
    """Returns detailed system information about the host machine."""
    return {
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
    }

@router.post("/host-resources")
async def get_host_resources():
    """Returns system resource usage (CPU, RAM, Disk)."""
    return {
        "cpu_usage": psutil.cpu_percent(interval=1),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage("/").percent,
        "system_uptime": psutil.boot_time()
    }
