import uuid
import json
import os
import uvicorn
import sys
from helpers import RequestLoggerMiddleware
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Request
from dotenv import load_dotenv
from auth import authenticate_request


# Import all routers
from docs_router import router as docs
from vision_router import router as vision
from info_router import router as info
from system_router import router as system
from file_handler import router as file

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = "3000"

# Get API Key (Generate if missing)
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    API_KEY = str(uuid.uuid4())
    with open(ENV_PATH, "a") as env_file:
        env_file.write(f"\nAPI_KEY={API_KEY}")

# Initialize FastAPI App
app = FastAPI(title="FastAPI Terminal Server", version="1.0")

# Include routers with authentication dependency
app.include_router(vision, tags=["Computer Vision"], dependencies=[Depends(authenticate_request)])
app.include_router(system, tags=["System Control"], dependencies=[Depends(authenticate_request)])
app.include_router(file, tags=["Read/Write Files"], dependencies=[Depends(authenticate_request)])
app.include_router(info, tags=["System Information"], dependencies=[Depends(authenticate_request)])
app.include_router(docs, tags=["API Documentation"], dependencies=[Depends(authenticate_request)])

@app.post("/")
async def root():
    return {"message": "AI System Control API is running!"}

def generate_openapi_json():
    """Generates OpenAPI schema and saves it as a JSON file."""
    openapi_schema = app.openapi()
    openapi_schema["servers"] = [
        {"url": "https://api.armand0e.online", "description": "Production server"}
    ]
    
    openapi_path = BASE_DIR / "openapi.json"
    with open(openapi_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2)
    
    print("✅ OpenAPI schema saved as openapi.json")

app.add_middleware(RequestLoggerMiddleware)

@app.post("/restart-server")
async def restart_server(request: Request):
    """Restarts the API server (admin-only)."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header.split(" ")[-1] != os.getenv("ADMIN_API_KEY"):
        raise HTTPException(status_code=403, detail="Unauthorized")

    os.execv(sys.executable, ['python'] + sys.argv)

if __name__ == "__main__":
    PORT = os.getenv("PORT", DEFAULT_PORT)
    HOST = os.getenv("HOST", DEFAULT_HOST)

    generate_openapi_json()

    print("🚀 Starting Uvicorn server...")
    print(f"🔑 Your API Key: {API_KEY}")

    uvicorn.run("main:app", host=HOST, port=int(PORT), log_level="debug")
