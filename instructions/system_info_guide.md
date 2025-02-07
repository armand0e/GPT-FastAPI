# System Information API Guide

## Overview
This API module provides real-time system diagnostics, hardware details, and network status. It allows AI-driven applications to retrieve crucial host system information and monitor performance.

## Features
- Retrieve CPU, GPU, RAM, and motherboard details
- Monitor system resource usage
- Fetch network-related information (IP, hostname, open ports)
- Detect running processes
- Check port availability

---

## API Endpoints

### 1. Get Host System Information
#### **GET** `/api/host-info`
Retrieves essential details about the host system.

**Response:**
```json
{
  "system": "Windows",
  "architecture": "AMD64",
  "version": "10.0.19043",
  "gpu": "NVIDIA GeForce RTX 3060",
  "motherboard": "ASUS PRIME B450-PLUS",
  "cpu": "AMD Ryzen 5 5600X",
  "cpu_cores": 6,
  "cpu_threads": 12,
  "total_ram": "32 GB",
  "available_ram": "12 GB",
  "disk_usage": "400 GB free",
  "python_version": "3.11.2",
  "shell": "C:\\Program Files\\Git\\bin\\bash.exe",
  "hostname": "DESKTOP-XYZ",
  "ip_address": "192.168.1.10"
}
```

#### **Implementation Notes:**
- Uses `platform`, `psutil`, and `torch` to collect system data.
- **GPU detection** prioritizes CUDA (PyTorch) but falls back to OS-based detection.
- **Motherboard details** are fetched using OS-specific commands (`wmic`, `dmidecode`, `system_profiler`).

---

### 2. Get Host Resource Usage
#### **GET** `/api/host-resources`
Returns real-time resource usage metrics (CPU, RAM, Disk).

**Response:**
```json
{
  "cpu_usage": 14.2,
  "memory_usage": 68.5,
  "disk_usage": 72.3,
  "uptime": 1678923521.1234
}
```

#### **Implementation Notes:**
- **CPU Usage** is updated every second.
- **Memory and Disk Usage** percentages represent current consumption.
- **Uptime** represents the system’s boot timestamp in seconds.

---

### 3. Get Network Information
#### **GET** `/api/network-info`
Retrieves network-related information such as IP addresses and active connections.

**Response:**
```json
{
  "hostname": "DESKTOP-XYZ",
  "public_ip": "203.120.45.18",
  "private_ip": "192.168.1.10"
}
```

#### **Implementation Notes:**
- Fetches **public IP** using `curl ifconfig.me`.
- **Private IP detection** adapts to Linux, macOS, and Windows environments.

---

### 4. List Running Processes
#### **GET** `/api/list-processes`
Lists all running processes on the system along with CPU usage.

**Response:**
```json
{
  "processes": [
    { "pid": 1234, "name": "chrome.exe", "cpu_percent": 5.2 },
    { "pid": 5678, "name": "python.exe", "cpu_percent": 10.1 }
  ]
}
```

#### **Implementation Notes:**
- Uses `psutil.process_iter()` to fetch process details.
- AI can use this to detect **high CPU usage** or **unusual activity**.

---

### 5. Check Port Availability
#### **GET** `/api/check-port/{port}`
Checks if a given port is currently in use.

**Response:**
```json
{
  "port": 22,
  "status": "in use",
  "pid": 1357
}
```

#### **Implementation Notes:**
- Uses `psutil.net_connections()` to check if a **port is occupied**.
- Returns **process ID (PID)** of the application using that port.

---

## **Technical Details**

### **Motherboard Information Extraction**
- **Windows**: Uses `wmic baseboard get`.
- **Linux**: Uses `dmidecode -t baseboard`.
- **MacOS**: Uses `system_profiler SPHardwareDataType`.

### **GPU Detection**
- **First Check**: Uses PyTorch (`torch.cuda.is_available()`)
- **Fallback**: OS-based commands (`wmic`, `nvidia-smi`)

### **Performance Considerations**
- Uses **`psutil`** for optimized performance metrics.
- Caches some results to **reduce redundant computations**.
- Supports **real-time process tracking** and **network monitoring**.

---

## **Security Considerations**
- **Restrict access**: Use API keys to prevent unauthorized system access.
- **Limit exposure**: Avoid exposing sensitive system data in public environments.
- **Monitor for misuse**: Track frequent requests to detect potential abuse.

---

## **Final Thoughts**
This API provides **critical system insights** for AI automation, system monitoring, and remote diagnostics.

🚀 **Next Steps:**
- Implement **automated alerts** for high resource usage.
- Add **remote process termination** capabilities.
- Provide **detailed GPU performance statistics** for AI acceleration.

