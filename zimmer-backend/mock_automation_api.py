#!/usr/bin/env python3
"""
Mock Automation API Server for testing KB monitoring
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(title="Mock Automation API", version="1.0.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
mock_kb_statuses = {
    1: {
        "status": "healthy",
        "last_updated": "2025-01-28T15:30:00Z",
        "backup_status": True,
        "error_logs": [],
        "supports_reset": True,
        "kb_size": 1250
    },
    2: {
        "status": "warning",
        "last_updated": "2025-01-28T14:45:00Z",
        "backup_status": True,
        "error_logs": ["Last backup was 2 hours ago"],
        "supports_reset": True,
        "kb_size": 890
    },
    3: {
        "status": "error",
        "last_updated": "2025-01-28T13:20:00Z",
        "backup_status": False,
        "error_logs": ["Database connection failed", "Backup service unavailable"],
        "supports_reset": False,
        "kb_size": 0
    }
}

def verify_token(authorization: Optional[str] = Header(None)):
    """Verify the service token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "")
    expected_token = "default_service_token"  # Should match ZIMMER_SERVICE_TOKEN
    
    if token != expected_token:
        raise HTTPException(status_code=401, detail="Invalid service token")
    
    return token

class KBStatusRequest(BaseModel):
    user_id: int
    user_automation_id: int

class KBResetRequest(BaseModel):
    user_automation_id: int

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Mock Automation API",
        "version": "1.0.0",
        "endpoints": {
            "kb_status": "/api/kb-status",
            "kb_reset": "/api/kb-reset"
        }
    }

@app.post("/api/kb-status")
async def get_kb_status(request: KBStatusRequest, token: str = Depends(verify_token)):
    """Mock KB status endpoint"""
    user_automation_id = request.user_automation_id
    
    # Simulate different responses based on user_automation_id
    if user_automation_id in mock_kb_statuses:
        return mock_kb_statuses[user_automation_id]
    else:
        # Default healthy status for unknown IDs
        return {
            "status": "healthy",
            "last_updated": datetime.utcnow().isoformat(),
            "backup_status": True,
            "error_logs": [],
            "supports_reset": True,
            "kb_size": 1000
        }

@app.post("/api/kb-reset")
async def reset_kb(request: KBResetRequest, token: str = Depends(verify_token)):
    """Mock KB reset endpoint"""
    user_automation_id = request.user_automation_id
    
    # Simulate reset process
    if user_automation_id in mock_kb_statuses:
        # Reset the status to healthy
        mock_kb_statuses[user_automation_id] = {
            "status": "healthy",
            "last_updated": datetime.utcnow().isoformat(),
            "backup_status": True,
            "error_logs": [],
            "supports_reset": True,
            "kb_size": 0
        }
    
    return {
        "status": "success",
        "message": f"KB reset initiated for user automation {user_automation_id}",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "mock-automation-api"}

if __name__ == "__main__":
    print("🚀 Starting Mock Automation API Server...")
    print("📡 Server will run on http://localhost:8001")
    print("🔑 Use token: default_service_token")
    print("📋 Available endpoints:")
    print("  - POST /api/kb-status")
    print("  - POST /api/kb-reset")
    print("  - GET /health")
    
    uvicorn.run(app, host="0.0.0.0", port=8001) 