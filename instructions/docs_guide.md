# API Documentation Handler Guide

## Overview
This module provides routes for accessing API documentation and metadata, making it easier to integrate with external tools and services.

## Available Routes

### 1. Get OpenAPI Specification
**Endpoint**: `GET /api/docs`

**Description**:
Retrieves the OpenAPI specification for the FastAPI application.

**Response Example**:
```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "FastAPI Terminal Server",
    "version": "1.0"
  },
  "paths": {
    ...
  }
}
```

### 2. Get API Metadata
**Endpoint**: `GET /api/metadata`

**Description**:
Provides general metadata about the API, including version, available routes, and description.

**Response Example**:
```json
{
  "title": "FastAPI Terminal Server",
  "version": "1.0",
  "description": "API for managing terminal commands, file access, and AI interaction.",
  "routes": [
    "/api/docs",
    "/api/metadata",
    "/api/health"
  ]
}
```

### 3. API Health Check
**Endpoint**: `GET /api/health`

**Description**:
Returns the health status of the API to indicate if it is running properly.

**Response Example**:
```json
{
  "status": "healthy",
  "uptime": "2 hours 15 minutes"
}
```

## Implementation Details

### Code Implementation
```python
from fastapi import APIRouter
from fastapi.openapi.utils import get_openapi
from main import app

router = APIRouter()

@router.get("/api/docs")
def get_openapi_spec():
    return get_openapi(title="FastAPI Terminal Server", version="1.0", routes=app.routes)

@router.get("/api/metadata")
def get_api_metadata():
    return {
        "title": "FastAPI Terminal Server",
        "version": "1.0",
        "description": "API for managing terminal commands, file access, and AI interaction.",
        "routes": [route.path for route in app.routes]
    }

@router.get("/api/health")
def health_check():
    return {"status": "healthy", "uptime": "2 hours 15 minutes"}  # Example uptime
```

## Usage
These routes can be used to fetch the OpenAPI specification for integration with API tools like Postman or Swagger UI, retrieve API metadata, and monitor the API's health status.

### Example Request
Using `curl` to check API health:
```
curl -X GET http://localhost:3000/api/health
```

Using Python requests:
```python
import requests
response = requests.get("http://localhost:3000/api/metadata")
print(response.json())
```

## Notes
- The `docs` route provides the OpenAPI JSON format.
- The `metadata` route lists all registered routes dynamically.
- The `health` route can be expanded to include more monitoring details like database connectivity.

---

This documentation ensures that developers can understand and interact with the API efficiently.

