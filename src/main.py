from fastapi.responses import JSONResponse
import uuid, dotenv, uvicorn, json, os, sys, asyncio
from contextlib import asynccontextmanager
from fastapi.requests import Request
from fastapi import FastAPI, Depends, HTTPException
from auth import authenticate_request
from logger import system_logger
from docs_router import router as docs
from vision_router import router as vision
from info_router import router as info
from system_router import cleanup_processes, router as system
from file_handler import router as file

logger = system_logger
ENV_PATH = dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')

env = dotenv.load_dotenv(ENV_PATH)
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = '3000'
'Runs the Uvicorn server on the externally accessible port.'
API_KEY = dotenv.get_key(ENV_PATH, 'API_KEY')
'Generate API Key if not found'
if not API_KEY:
    API_KEY = str(uuid.uuid4())
    dotenv.set_key(ENV_PATH, 'API_KEY', API_KEY)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app startup and shutdown."""
    generate_openapi_json()
    yield
    
    cleanup_processes()
    logger.info('Shutting down server...')

app = FastAPI(title='FastAPI Terminal Server', version='1.0', lifespan=lifespan)
'Include routers with authentication dependency'
app.include_router(vision, tags=['Computer Vision'], dependencies=[Depends(authenticate_request)])
app.include_router(system, tags=['System Control'], dependencies=[Depends(authenticate_request)])
app.include_router(file, tags=['Read/Write Files'], dependencies=[Depends(authenticate_request)])
app.include_router(info, tags=['System Information'], dependencies=[Depends(authenticate_request)])
app.include_router(docs, tags=['Api Documentation'], dependencies=[Depends(authenticate_request)])

@app.post('/')
async def root():
    return {'message': 'AI System Control API is running!'}

def generate_openapi_json():
    openapi_schema = app.openapi()
    openapi_schema['servers'] = [{'url': 'https://api.armand0e.online', 'description': 'Production server'}]
    parent_directory = os.path.dirname(os.path.dirname(__file__))
    openapi_path = os.path.join(parent_directory, 'openapi.json')
    with open(openapi_path, 'w', encoding='utf-8') as f:
        json.dump(openapi_schema, f, indent=2)
    print(f'✅ OpenAPI schema saved at {openapi_path}')

@app.get("/docs-json")
async def read_json_file():
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'openapi.json'), "r") as file:
        data = json.load(file)
    return JSONResponse(content=data)

@app.post('/restart-server')
async def restart_server(request: Request):
    """Endpoint to restart the API server."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header.split(' ')[-1] != os.getenv('API_KEY'):
        raise HTTPException(status_code=403, detail='Unauthorized')
    logger.info('Server restart requested. Cleaning up processes...')

    logger.info('Cleanup completed. Restarting server...')

    async def delayed_restart():
        await asyncio.sleep(1)
        os.execv(sys.executable, [sys.executable] + sys.argv)
    asyncio.create_task(delayed_restart())
    return {'message': 'Server will restart shortly'}

@app.get('/privacy-policy')
def privacy_policy():
    return JSONResponse(content={
        'title': 'Privacy Policy',
        'description': 'We do not collect, store, or share any personal data. This API operates entirely locally or securely with authorized access only.',
        'contact': 'aran.rafiee@gmail.com'
    })

if __name__ == '__main__':
    PORT = dotenv.get_key(ENV_PATH, 'PORT')
    HOST = dotenv.get_key(ENV_PATH, 'HOST')
    'Set to HOST to DEFAULT_HOST if not found'
    if not HOST:
        HOST = DEFAULT_HOST
        dotenv.set_key(ENV_PATH, 'HOST', DEFAULT_HOST)
    'Set to PORT to DEFAULT_PORT if not found'
    if not PORT:
        PORT = DEFAULT_PORT
        dotenv.set_key(ENV_PATH, 'PORT', DEFAULT_PORT)
    'Runs the Uvicorn server directly inside the script.'
    print('🚀 Starting Uvicorn server...')
    print(f'🔑 Your API Key: {API_KEY}')
    uvicorn.run('main:app', host=HOST, port=int(PORT), log_level='debug')