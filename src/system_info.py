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

def get_public_ip():
    """Retrieve public IP address."""
    try:
        result = subprocess.run(["curl", "-s", "ifconfig.me"], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception:
        return "Unknown"

def get_private_ip():
    """Retrieve private IP address."""
    try:
        if platform.system() == "Windows":
            result = os.popen("ipconfig").read()
            for line in result.split("\n"):
                if "IPv4 Address" in line:
                    return line.split(":")[1].strip()
        else:
            result = subprocess.getoutput("hostname -I").split()
            return result[0] if result else "Unknown"
    except Exception:
        return "Unknown"

@router.get("/api/host-info")
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
        "private_ip": get_private_ip(),
        "public_ip": get_public_ip(),
    }

@router.get("/api/host-resources")
async def get_host_resources():
    """Returns system resource usage (CPU, RAM, Disk)."""
    return {
        "cpu_usage": psutil.cpu_percent(interval=1),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage("/").percent,
        "uptime": psutil.boot_time()
    }

@router.get("/api/network-info")
async def get_network_info():
    """Returns network details such as IP address and active connections."""
    return {
        "hostname": platform.node(),
        "public_ip": get_public_ip(),
        "private_ip": get_private_ip(),
    }

@router.get("/api/list-processes")
async def list_processes():
    """Lists running processes on the system."""
    processes = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent"]):
        processes.append(proc.info)
    return {"processes": processes}

@router.get("/api/check-port/{port}")
async def check_port_usage(port: int):
    """Checks if a given port is in use."""
    for conn in psutil.net_connections():
        if conn.laddr.port == port:
            return {"port": port, "status": "in use", "pid": conn.pid}
    return {"port": port, "status": "available"}
