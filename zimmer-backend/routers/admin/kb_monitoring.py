from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import httpx
import os
from datetime import datetime
from database import get_db
from models.automation import Automation
from models.user_automation import UserAutomation
from models.user import User
from models.kb_status_history import KBStatusHistory
from utils.auth_dependency import get_current_admin_user

router = APIRouter()

async def call_automation_api(url: str, data: dict, automation_id: int, timeout: int = 10) -> dict:
    """Make authenticated call to automation API with service token"""
    # Get service token from environment for specific automation
    service_token = os.getenv(f"AUTOMATION_{automation_id}_SERVICE_TOKEN")
    if not service_token:
        raise HTTPException(
            status_code=500,
            detail="Service token not configured for this automation"
        )
    
    headers = {
        "X-Zimmer-Service-Token": service_token,
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Automation API timeout"
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Automation API error: {e.response.status_code}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to call automation API: {str(e)}"
        )

@router.get("/kb-status")
async def get_kb_status(
    automation_id: int = Query(..., description="Automation ID to check KB status for"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get KB status for all users of a specific automation"""
    
    # Get automation
    automation = db.query(Automation).filter(Automation.id == automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    
    if not automation.api_kb_status_url:
        raise HTTPException(
            status_code=400, 
            detail="Automation does not have KB status URL configured"
        )
    
    # Get all users with this automation
    user_automations = db.query(UserAutomation, User).join(
        User, UserAutomation.user_id == User.id
    ).filter(
        UserAutomation.automation_id == automation_id
    ).all()
    
    kb_statuses = []
    
    for user_automation, user in user_automations:
        try:
            # Call automation's KB status API
            response_data = await call_automation_api(
                automation.api_kb_status_url,
                {
                    "user_id": user.id,
                    "user_automation_id": user_automation.id
                },
                automation_id
            )
            
            # Normalize response
            kb_health = response_data.get("status", "unknown")
            backup_status = response_data.get("backup_status", False)
            error_logs = response_data.get("error_logs", [])
            
            kb_status = {
                "user_id": user.id,
                "name": user.name,
                "kb_health": kb_health,
                "last_updated": response_data.get("last_updated", datetime.utcnow().isoformat()),
                "backup_status": backup_status,
                "error_logs": error_logs,
                "supports_reset": response_data.get("supports_reset", False)
            }
            
            kb_statuses.append(kb_status)
            
            # Save to history
            try:
                history_record = KBStatusHistory(
                    user_id=user.id,
                    user_automation_id=user_automation.id,
                    automation_id=automation_id,
                    kb_health=kb_health,
                    backup_status=backup_status,
                    error_logs=error_logs if error_logs else None
                )
                db.add(history_record)
            except Exception as e:
                # Log error but don't fail the main request
                print(f"Error saving KB history: {e}")
            
        except HTTPException:
            # If API call fails, add error status
            error_status = {
                "user_id": user.id,
                "name": user.name,
                "kb_health": "error",
                "last_updated": datetime.utcnow().isoformat(),
                "backup_status": False,
                "error_logs": ["Failed to connect to automation API"],
                "supports_reset": False
            }
            kb_statuses.append(error_status)
            
            # Save error status to history
            try:
                history_record = KBStatusHistory(
                    user_id=user.id,
                    user_automation_id=user_automation.id,
                    automation_id=automation_id,
                    kb_health="error",
                    backup_status=False,
                    error_logs=["Failed to connect to automation API"]
                )
                db.add(history_record)
            except Exception as e:
                # Log error but don't fail the main request
                print(f"Error saving KB history: {e}")
    
    # Commit all history records
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error committing KB history: {e}")
    
    return {
        "automation_id": automation_id,
        "automation_name": automation.name,
        "total_users": len(kb_statuses),
        "kb_statuses": kb_statuses
    }

@router.post("/kb-reset/{user_automation_id}")
async def reset_user_kb(
    user_automation_id: int = Path(..., description="User automation ID to reset KB for"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Reset KB for a specific user automation"""
    
    # Get user automation
    user_automation = db.query(UserAutomation).filter(
        UserAutomation.id == user_automation_id
    ).first()
    
    if not user_automation:
        raise HTTPException(status_code=404, detail="User automation not found")
    
    # Get automation
    automation = db.query(Automation).filter(
        Automation.id == user_automation.automation_id
    ).first()
    
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    
    if not automation.api_kb_reset_url:
        raise HTTPException(
            status_code=400,
            detail="Automation does not have KB reset URL configured"
        )
    
    try:
        # Call automation's KB reset API
        response_data = await call_automation_api(
            automation.api_kb_reset_url,
            {
                "user_automation_id": user_automation_id
            },
            automation.id
        )
        
        return {
            "message": "KB reset initiated successfully",
            "user_automation_id": user_automation_id,
            "automation_name": automation.name,
            "reset_status": response_data.get("status", "success")
        }
        
    except HTTPException:
        raise HTTPException(
            status_code=500,
            detail="Failed to reset KB - automation API error"
        ) 