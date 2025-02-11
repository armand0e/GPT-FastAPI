from fastapi import Request, HTTPException
import os

def authenticate_request(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized. Use 'Authorization: Bearer <API_KEY>'")

    api_key = auth_header.split(" ")[1]
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
