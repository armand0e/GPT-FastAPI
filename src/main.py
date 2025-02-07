import os
import uuid
import subprocess
import sys
import dotenv
from fastapi import FastAPI, Depends, HTTPException
from auth import authenticate_request
from pydantic import BaseModel
from typing import List, Dict, Any
import httpx

# Import all routers
from ai_handler import router as ai_router
from docs import router as docs_router
from file_access import router as file_router
from system_info import router as system_router
from terminal_handler import router as terminal_router
from web_handler import router as web_router
from websocket_routes import router as websocket_router

# Load environment variables
dotenv.load_dotenv(dotenv_path=".env")

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = "3000"

"""Runs the Uvicorn server on the externally accessible port."""
print("🚀 Starting Uvicorn server...")
API_KEY = dotenv.get_key(".env", "API_KEY")
PORT = dotenv.get_key(".env", "PORT")
HOST = dotenv.get_key(".env", "HOST")

"""Set to HOST to DEFAULT_HOST if not found"""
if not HOST:
    HOST = DEFAULT_HOST
    dotenv.set_key('.env', "HOST", DEFAULT_HOST)
"""Set to PORT to DEFAULT_PORT if not found"""
if not PORT:
    PORT = DEFAULT_PORT
    dotenv.set_key('.env', "PORT", DEFAULT_PORT)
"""Generate API Key if not found"""
if not API_KEY:
    API_KEY = str(uuid.uuid4())
    dotenv.set_key(".env", "API_KEY", API_KEY)

print(f"🔑 Your API Key: {API_KEY}")
app = FastAPI(title="FastAPI Terminal Server", version="1.0")

"""Include routers with authentication dependency"""
app.include_router(terminal_router, dependencies=[Depends(authenticate_request)])
app.include_router(file_router, dependencies=[Depends(authenticate_request)])
app.include_router(ai_router, dependencies=[Depends(authenticate_request)])
app.include_router(websocket_router, dependencies=[Depends(authenticate_request)])
app.include_router(web_router, dependencies=[Depends(authenticate_request)])
app.include_router(system_router, dependencies=[Depends(authenticate_request)])
app.include_router(docs_router, dependencies=[Depends(authenticate_request)])

class BulkRequest(BaseModel):
    """Schema for bulk queuing API calls"""
    requests: List[Dict[str, Any]]

@app.post("/api/queue-requests", dependencies=[Depends(authenticate_request)])
async def queue_requests(bulk_request: BulkRequest):
    """
    Accepts multiple API requests and processes them sequentially in order.
    """
    results = []
    async with httpx.AsyncClient() as client:
        for req in bulk_request.requests:
            router = req.get("router")
            endpoint = req.get("endpoint")
            method = req.get("method", "POST").upper()
            data = req.get("data", {})

            if not router or not endpoint:
                results.append({"error": "Invalid request format", "details": req})
                continue

            url = f"http://localhost:3000{endpoint}"  # Assumes local execution
            headers = {"Authorization": f"Bearer {API_KEY}"}

            try:
                if method == "GET":
                    response = await client.get(url, headers=headers, params=data)
                else:
                    response = await client.post(url, headers=headers, json=data)
                
                results.append({"router": router, "endpoint": endpoint, "status": response.status_code, "response": response.json()})
            except Exception as e:
                results.append({"router": router, "endpoint": endpoint, "error": str(e)})

    return {"status": "queued", "requests": results}

