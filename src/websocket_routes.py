from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from typing import List
import os
import asyncio
import json

router = APIRouter()
active_connections: List[WebSocket] = []

async def authenticate_websocket(websocket: WebSocket):
    """Authenticate WebSocket using Bearer API Key."""
    auth_header = websocket.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        await websocket.close()
        raise HTTPException(status_code=401, detail="Unauthorized. Use 'Authorization: Bearer <API_KEY>'")

    api_key = auth_header.split(" ")[1]
    if api_key != os.getenv("API_KEY"):
        await websocket.close()
        raise HTTPException(status_code=403, detail="Invalid API Key")

@router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """Handles WebSocket connections with authentication."""
    await websocket.accept()
    
    try:
        await authenticate_websocket(websocket)
    except HTTPException as e:
        print(f"❌ WebSocket authentication failed: {e.detail}")
        return

    active_connections.append(websocket)
    print(f"✅ WebSocket client connected: {websocket.client}")

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print(f"❌ WebSocket client disconnected: {websocket.client}")

async def broadcast_log(message: str):
    """Broadcasts logs to all authenticated WebSocket clients."""
    disconnected_clients = []
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except Exception:
            disconnected_clients.append(connection)

    # Remove any disconnected clients
    for client in disconnected_clients:
        active_connections.remove(client)

@router.get("/api/get-active-websockets")
async def get_active_websockets():
    """Returns the number of active WebSocket connections."""
    return {"active_websockets": len(active_connections)}

@router.post("/api/broadcast-log")
async def broadcast_log_api(message: str):
    """Allows API clients to broadcast a log message to all connected WebSockets."""
    await broadcast_log(message)
    return {"status": "success", "message": f"Log broadcasted: {message}"}

@router.post("/api/disconnect-all-websockets")
async def disconnect_all_websockets():
    """Forcibly disconnects all active WebSocket connections."""
    for connection in active_connections:
        try:
            await connection.close()
        except Exception:
            pass
    active_connections.clear()
    return {"status": "success", "message": "All WebSocket connections have been closed."}

@router.get("/api/get-logs-stream")
async def get_logs_stream():
    """GPT-Builder calls this API to receive logs (proxy for WebSockets)"""
    async def log_stream():
        queue = asyncio.Queue()
        async def receive_logs():
            while True:
                log_message = await queue.get()
                yield f"data: {json.dumps({'log': log_message})}\n\n"

        async def listen_to_websockets():
            while True:
                await asyncio.sleep(0.5)  # Prevent CPU overuse
                if active_connections:
                    for ws in active_connections:
                        try:
                            message = await ws.receive_text()
                            await queue.put(message)
                        except Exception:
                            pass

        asyncio.create_task(listen_to_websockets())
        return receive_logs()

    return log_stream()
