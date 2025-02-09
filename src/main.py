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
import uvicorn

# Import all routers
from docs_router import router as docs
from vision_router import router as vision
from info_router import router as info
from system_router import router as system

# Load environment variables
dotenv.load_dotenv(dotenv_path='./.env')

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = "3000"

"""Runs the Uvicorn server on the externally accessible port."""
API_KEY = dotenv.get_key("./.env", "API_KEY")

"""Generate API Key if not found"""
if not API_KEY:
    API_KEY = str(uuid.uuid4())
    dotenv.set_key("./.env", "API_KEY", API_KEY)

app = FastAPI(title="FastAPI Terminal Server", version="1.0")

"""Include routers with authentication dependency"""
app.include_router(vision, tags =["Computer Vision"], dependencies=[Depends(authenticate_request)])
app.include_router(system, tags =["System Control"], dependencies=[Depends(authenticate_request)])
app.include_router(info, tags =["System Information"], dependencies=[Depends(authenticate_request)])
app.include_router(docs, tags =["Api Documentation"], dependencies=[Depends(authenticate_request)])

class BulkRequest(BaseModel):
    """Schema for bulk queuing API calls"""
    requests: List[Dict[str, Any]]

@app.post("/api/queue-requests", dependencies=[Depends(authenticate_request)])
async def queue_requests(bulk_request: BulkRequest):
    """
    Accepts multiple API requests and processes them sequentially in order.
    Only supports POST requests with body-based parameters.
    """
    results = []
    async with httpx.AsyncClient() as client:
        for req in bulk_request.requests:
            endpoint = req.get("endpoint")
            method = req.get("method", "POST").upper()
            data = req.get("data", {})

            if not endpoint:
                results.append({"error": "Invalid request format", "details": req})
                continue
            
            url = f"http://localhost:3000{endpoint}"  # Assumes local execution
            headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
            

            try:
                response = await client.post(url, headers=headers, json=data)
                results.append({
                    "endpoint": endpoint,
                    "status": response.status_code,
                    "response": response.json()
                })
            except Exception as e:
                results.append({"endpoint": endpoint, "error": str(e)})

    return {"status": "queued", "requests": results}

@app.get("/")
async def root():
    return {"message": "AI System Control API is running!"}

if __name__ == "__main__":
    PORT = dotenv.get_key("./.env", "PORT")
    HOST = dotenv.get_key("./.env", "HOST")

    """Set to HOST to DEFAULT_HOST if not found"""
    if not HOST:
        HOST = DEFAULT_HOST
        dotenv.set_key('.env', "HOST", DEFAULT_HOST)
    """Set to PORT to DEFAULT_PORT if not found"""
    if not PORT:
        PORT = DEFAULT_PORT
        dotenv.set_key('.env', "PORT", DEFAULT_PORT)
    
    """Runs the Uvicorn server directly inside the script."""
    print("🚀 Starting Uvicorn server...")
    print(f"🔑 Your API Key: {API_KEY}")
    uvicorn.run("main:app", host=HOST, port=int(PORT), log_level="debug")