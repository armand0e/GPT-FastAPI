from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
import platform
import os
import shutil
import psutil
import torch
import subprocess
import socket

router = APIRouter()
load_dotenv()

def get_gpu_info():
    """Detects GPU using PyTorch or system commands."""
    try:
        if torch.cuda.is_available():
            return torch.cuda.get_device_name(0)
        elif platform.system() == "Windows":
            result = subprocess.run(["wmic", "path", "win32_videocontroller", "get", "name"], capture_output=True, text=True)
            return result.stdout.strip().split("\n")[1] if result.returncode == 0 else "Unknown GPU"

        elif platform.system() == "Linux":
            result = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], capture_output=True, text=True)
            return result.stdout.strip() if result.returncode == 0 else "Unknown GPU"
        else:
            return "GPU not detected"
 
    except Exception:
        return "GPU detection failed"

def get_cpu_info():
    """Detects CPU using system commands"""

@router.post("/info")
async def get_host_info():
    """Returns detailed system information about the host machine."""
    return {
        "system": platform.system(),
        "architecture": platform.machine(),
        "version": platform.version(),
        "gpu": get_gpu_info(),
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
        "uptime": psutil.boot_time()
    }

@router.post("/list-running-processes")
async def list_processes():
    """Lists running processes on the system."""
    processes = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent"]):
        processes.append(proc.info)
    return {"processes": processes}
