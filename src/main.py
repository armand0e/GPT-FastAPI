import os
import uuid
import subprocess
import sys
from dotenv import load_dotenv
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
load_dotenv()

app = FastAPI(title="FastAPI Terminal Server", version="1.0")

# Include routers with authentication dependency
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

if __name__ == "__main__":
    """Runs the Uvicorn server on the externally accessible port."""
    print("🚀 Starting Uvicorn server...")
    API_KEY = os.getenv("API_KEY")
    PORT = os.getenv("PORT", "3000")

    # Generate API Key on First Run
    if not API_KEY:
        API_KEY = str(uuid.uuid4())
        os.environ["API_KEY"] = API_KEY
        with open(".env", "w") as env_file:
            env_file.write(f"API_KEY={API_KEY}\n")

    print(f"🔑 Your API Key: {API_KEY}")
    cwd = os.path.dirname(os.path.abspath(__file__))  # Get current directory

    command = [
        sys.executable, "-m", "uvicorn", "main:app",
        "--host", "0.0.0.0",
        "--port", str(int(PORT)),
        "--log-level", "debug",
        "--reload"
    ]

    subprocess.run(command, check=True, cwd=cwd)