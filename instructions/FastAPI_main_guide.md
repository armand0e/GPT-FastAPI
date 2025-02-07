# FastAPI Terminal Server - Main API Guide

## Overview
This API serves as a **multi-functional command center**, handling:
- **Terminal execution**
- **File access and management**
- **AI-powered processing**
- **System information retrieval**
- **Web automation via Playwright**
- **WebSockets for real-time logs**

The API is built on **FastAPI** and supports **bulk queuing** of API calls.

---

## **Authentication**
All routes (except `/api/docs`) require an **API key** for authentication.

- Include this in the headers of your request:
  ```
  Authorization: Bearer YOUR_API_KEY
  ```
- Your **API key** is generated on the first run and stored in `.env`.

---

## **Endpoints**
### **Bulk API Queueing**
Process multiple API requests **sequentially** in a single request.

- **Endpoint:** `POST /api/queue-requests`
- **Requires Authentication:** ✅ Yes
- **Request Format:**
  ```json
  {
    "requests": [
      {"router": "terminal", "endpoint": "/api/run-terminal", "data": {"command": "echo 'Hello'"}},
      {"router": "file", "endpoint": "/api/write-file", "data": {"filename": "test.txt", "content": "Hello, World!"}},
      {"router": "web", "endpoint": "/api/web/open-page", "data": {"session_id": "123", "url": "https://example.com"}},
      {"router": "ai", "endpoint": "/api/sentence-embedding", "data": {"text": "AI is powerful"}}
    ]
  }
  ```
- **Response Example:**
  ```json
  {
    "status": "queued",
    "requests": [
      {"router": "terminal", "endpoint": "/api/run-terminal", "status": 200, "response": {"output": "Hello"}},
      {"router": "file", "endpoint": "/api/write-file", "status": 200, "response": {"message": "File saved successfully"}},
      {"router": "web", "endpoint": "/api/web/open-page", "status": 200, "response": {"status": "success", "url": "https://example.com"}},
      {"router": "ai", "endpoint": "/api/sentence-embedding", "status": 200, "response": {"embedding": [...]}}
    ]
  }
  ```

---

## **Core Functionality**
### **1️⃣ Terminal Execution**
- Run shell commands
- Interrupt terminal execution

### **2️⃣ File Management**
- Read & write files
- Perform fuzzy search in files

### **3️⃣ AI Processing**
- Generate text embeddings

### **4️⃣ Web Automation**
- Open pages & interact with elements
- Perform Google searches
- Extract page content

### **5️⃣ System Information**
- Fetch CPU, GPU, RAM, and OS details
- Monitor running processes & network stats

### **6️⃣ WebSockets (Real-Time Logs)**
- Connect WebSocket clients to stream logs

---

## **Running the API**
Start the FastAPI server using:
```sh
python main.py
```
The server will run at:
```
http://localhost:3000
```

---

## **Security & Optimization**
- **API key authentication** ensures secure access.
- **Sequential execution of queued API requests** prevents race conditions.
- **Supports batch requests** to reduce API call overhead.

---

## **Final Notes**
This API is designed to be **modular, scalable, and AI-friendly**. The bulk queuing system allows an AI to efficiently request **multiple operations in a single call** while ensuring execution **order and stability**. 🚀

