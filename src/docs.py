import time
from datetime import timedelta
from fastapi import APIRouter
from fastapi.openapi.utils import get_openapi
from importlib import import_module

router = APIRouter()

# Store the time when the application starts
APP_START_TIME = time.time()

def get_app():
    """Dynamically import the main FastAPI app to prevent circular imports."""
    app_module = import_module("main")
    return getattr(app_module, "app", None)

@router.get("/api/docs")
async def get_openapi_spec():
    """Returns the OpenAPI documentation."""
    app = get_app()
    if app:
        return get_openapi(title="FastAPI Terminal Server", version="1.0", routes=app.routes)
    return {"error": "Failed to retrieve OpenAPI spec"}

@router.get("/api/metadata")
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

@router.get("/api/health")
async def health_check():
    """Returns the API status and uptime."""
    uptime_seconds = int(time.time() - APP_START_TIME)
    uptime_str = str(timedelta(seconds=uptime_seconds))

    return {
        "status": "running",
        "uptime": uptime_str
    }
