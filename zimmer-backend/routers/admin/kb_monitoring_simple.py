from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from database import SessionLocal
from models.automation import Automation
from models.user_automation import UserAutomation
from models.user import User
from utils.auth_dependency import get_current_admin_user, get_db

router = APIRouter()

@router.get("/kb-status-simple")
def get_kb_status_simple(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Simple version of KB status endpoint without external API calls
    """
    try:
        print("KB Monitoring Simple: Starting...")
        
        # Get all active automations
        automations = db.query(Automation).filter(Automation.status == True).all()
        print(f"Found {len(automations)} active automations")
        
        if not automations:
            # Return empty result instead of error
            return {
                "status": "success",
                "data": [],
                "total_users": 0,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "No active automations found"
            }
        
        # Get all user automations for these automations
        automation_ids = [auto.id for auto in automations]
        user_automations = db.query(UserAutomation).filter(
            UserAutomation.automation_id.in_(automation_ids)
        ).all()
        print(f"Found {len(user_automations)} user automations")
        
        if not user_automations:
            # Return empty result instead of error
            return {
                "status": "success",
                "data": [],
                "total_users": 0,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "No user automations found"
            }
        
        # Get users for these user automations
        user_ids = [ua.user_id for ua in user_automations]
        users = db.query(User).filter(User.id.in_(user_ids)).all()
        user_dict = {user.id: user for user in users}
        print(f"Found {len(users)} users")
        
        # Create automation lookup
        automation_dict = {auto.id: auto for auto in automations}
        
        # Prepare results
        results = []
        
        for user_auto in user_automations:
            automation = automation_dict.get(user_auto.automation_id)
            user = user_dict.get(user_auto.user_id)
            
            if not automation or not user:
                continue
                
            # Create mock KB status since we don't have external APIs
            results.append({
                "user_id": user.id,
                "username": user.name,
                "automation_id": automation.id,
                "automation_name": automation.name,
                "user_automation_id": user_auto.id,
                "last_updated": datetime.utcnow().isoformat(),
                "backup_status": True,  # Mock data
                "kb_health": "healthy",  # Mock data
                "error_logs": [],  # Mock data
                "kb_size": 1024,  # Mock data
                "last_backup": datetime.utcnow().isoformat(),  # Mock data
                "supports_reset": True  # Mock data
            })
        
        print(f"Returning {len(results)} KB status entries")
        
        return {
            "status": "success",
            "data": results,
            "total_users": len(results),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        import traceback
        print(f"KB Monitoring Simple Error: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching KB status: {str(e)}")

@router.post("/kb-status-simple/refresh")
def refresh_all_kb_status_simple(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Simple refresh endpoint
    """
    try:
        return get_kb_status_simple(db=db, current_admin=current_admin)
    except Exception as e:
        import traceback
        print(f"KB Monitoring Simple Refresh Error: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error refreshing KB status: {str(e)}") 