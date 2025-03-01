import time
import logging
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from fastapi.openapi.utils import get_openapi
from importlib import import_module

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Store the time when the application starts
APP_START_TIME = time.time()

def get_app():
    """Dynamically import the main FastAPI app to prevent circular imports."""
    try:
        app_module = import_module("main")
        return getattr(app_module, "app", None)
    except ModuleNotFoundError:
        logger.error("Failed to import main app module.")
        return None

@router.post("/docs")
async def get_openapi_spec():
    """Returns the OpenAPI documentation."""
    app = get_app()
    if app:
        return get_openapi(title="FastAPI Terminal Server", version="1.0", routes=app.routes)
    return {"error": "Failed to retrieve OpenAPI spec"}

@router.post("/metadata")
async def get_metadata():
    """Provides metadata about the API."""
    app = get_app()
    if app:
        return {
            "name": "FastAPI Terminal Server",
            "version": "1.0",
            "description": "An API server for managing terminal commands, file access, AI processing, and web automation.",
            "routes": [route.path for route in app.routes]
        }
    return {"error": "Failed to retrieve API metadata"}

@router.post("/health")
async def health_check():
    """Returns the API status and uptime."""
    uptime_seconds = int(time.time() - APP_START_TIME)
    uptime_info = {
        "days": uptime_seconds // 86400,
        "hours": (uptime_seconds % 86400) // 3600,
        "minutes": (uptime_seconds % 3600) // 60,
        "seconds": uptime_seconds % 60
    }

    return {
        "status": "running",
        "uptime": uptime_info
    }
@router.post("/get-api-logs")
async def get_api_logs():
    """Returns the last 50 API request logs."""
    log_path = Path("logs/api_requests.log")

    if not log_path.exists():
        return {"logs": "No logs found."}

    with open(log_path, "r") as f:
        logs = f.readlines()

    return {"logs": logs[-50:]}  # Return last 50 logs


@router.post("/get-api-key")
async def get_api_key(request: Request):
    """Returns the API key (admin-only)."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header.split(" ")[-1] != os.getenv("ADMIN_API_KEY"):
        raise HTTPException(status_code=403, detail="Unauthorized")

    return {"api_key": os.getenv("API_KEY")}

