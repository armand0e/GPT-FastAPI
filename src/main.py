import uuid, dotenv, uvicorn, json
from fastapi import FastAPI, Depends
from auth import authenticate_request

# Import all routers
from docs_router import router as docs
from vision_router import router as vision
from info_router import router as info
from system_router import router as system
from file_handler import router as file

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
app.include_router(file, tags =["Read/Write Files"], dependencies=[Depends(authenticate_request)])
app.include_router(info, tags =["System Information"], dependencies=[Depends(authenticate_request)])
app.include_router(docs, tags =["Api Documentation"], dependencies=[Depends(authenticate_request)])

@app.post("/")
async def root():
    return {"message": "AI System Control API is running!"}

def generate_openapi_json():
    openapi_schema = app.openapi()
    
    # Add custom 'servers' field
    openapi_schema["servers"] = [
        {"url": "https://api.armand0e.online", "description": "Production server"}
    ]
    
    with open("openapi.json", "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2)
    print("✅ OpenAPI schema saved as openapi.json")

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
    
    generate_openapi_json()
    
    """Runs the Uvicorn server directly inside the script."""
    print("🚀 Starting Uvicorn server...")
    print(f"🔑 Your API Key: {API_KEY}")
    uvicorn.run("main:app", host=HOST, port=int(PORT), log_level="debug")