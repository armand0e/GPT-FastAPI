# Terminal Handler API Guide

## Overview
This API module allows executing terminal commands remotely through FastAPI, enabling AI-driven command execution, debugging, and automation.

## Features
- Persistent shell execution
- Auto-restarting shell session if closed
- Full compatibility with Windows (Git Bash), Linux, and macOS
- Multi-line command support with continuous output streaming
- Secure API authentication
- Graceful shutdown for memory management

---

## API Endpoints

### 1. Execute a Terminal Command
#### **POST** `/api/run-terminal`
Executes a terminal command and returns its output.

**Request Body:**
```json
{
  "command": "ls"
}
```

**Response:**
```json
{
  "output": "file1.txt  file2.py"
}
```

#### **Implementation Notes:**
- The command is passed to the active shell session.
- Output is captured and returned as a response.
- If the shell is closed, it **automatically restarts** before executing the command.

---

### 2. Interrupt Running Terminal Session
#### **POST** `/api/interrupt-terminal`
Forcibly stops the shell session and resets it.

**Response:**
```json
{
  "message": "Shell session terminated"
}
```

#### **Implementation Notes:**
- Terminates the current shell process.
- If no session is running, it returns `{ "message": "No shell session running" }`.

---

### 3. Check Shell Status
#### **GET** `/api/check-shell-status`
Returns whether the shell is currently active.

**Response:**
```json
{
  "status": "running"
}
```

#### **Implementation Notes:**
- Returns `running` if the shell process is active.
- Returns `stopped` if the shell is not running.

---

### 4. Close Shell Gracefully
#### **POST** `/api/close-shell`
Shuts down the active shell session cleanly.

**Response:**
```json
{
  "message": "Shell closed successfully"
}
```

#### **Implementation Notes:**
- Ensures all processes are stopped cleanly.
- Prevents memory leaks and system performance degradation.

---

## **Technical Details**

### **Persistent Shell Execution**
- The shell remains open **across multiple API calls** to optimize execution speed.
- Commands are written to `shell.stdin`, and output is captured from `shell.stdout`.
- If the shell process crashes or is interrupted, it **automatically restarts**.

### **Handling Multi-line Outputs**
- Instead of reading just one line, the API now captures full multi-line command outputs.

### **Windows Compatibility**
- Uses **Git Bash** by default on Windows (`C:\\Program Files\\Git\\bin\\bash.exe`).
- Can be overridden using the `SHELL` environment variable.

### **Why `subprocess.Popen`?**
- We use `subprocess.Popen()` instead of `asyncio.create_subprocess_exec()` to enable **real-time command streaming**.
- The `text=True` argument ensures proper **string-based handling** instead of raw bytes.

### **Graceful Shutdown**
- The `close_shell()` function ensures that the shell process is properly terminated when the server shuts down.
- Prevents memory leaks and ensures clean FastAPI shutdown behavior.

---

## **Security Considerations**
- **API Key Authentication** ensures only authorized users can execute commands.
- **Sanitization Required**: Avoid running untrusted commands, as execution happens **directly on the host machine**.
- **Use Role-Based Access Control (RBAC)** for additional security layers if needed.

---

## **Final Thoughts**
This module provides a robust API for executing and managing terminal commands, making it ideal for AI automation, debugging, and remote command execution.

🚀 **Next Steps:**
- Consider integrating AI-driven debugging suggestions based on command outputs.
- Implement **command history tracking** for better context-awareness.

