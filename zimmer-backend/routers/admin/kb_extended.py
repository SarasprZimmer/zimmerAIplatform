"""
Extended Knowledge Base Management Admin Endpoints
Handles KB templates, enhanced status, and monitoring
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from database import get_db
from models.user import User
from models.automation import Automation
from models.user_automation import UserAutomation
from utils.auth_dependency import get_current_admin_user

router = APIRouter(prefix="/api/admin", tags=["admin-kb-extended"])

class KBTemplate(BaseModel):
    id: int
    name: str
    description: str
    content: str
    automation_type: str
    created_at: datetime
    updated_at: datetime

class KBStatusRequest(BaseModel):
    automation_id: int

@router.get("/kb-templates")
async def get_kb_templates(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    automation_type: Optional[str] = Query(None),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get knowledge base templates
    """
    try:
        # For now, return mock templates since we don't have a KB templates table
        # In a real implementation, this would query a kb_templates table
        
        mock_templates = [
            {
                "id": 1,
                "name": "Sales Automation Template",
                "description": "Template for sales automation knowledge base",
                "content": "This is a template for sales automation KB...",
                "automation_type": "sales",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "id": 2,
                "name": "Customer Support Template",
                "description": "Template for customer support automation",
                "content": "This is a template for customer support KB...",
                "automation_type": "support",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "id": 3,
                "name": "Marketing Automation Template",
                "description": "Template for marketing automation knowledge base",
                "content": "This is a template for marketing automation KB...",
                "automation_type": "marketing",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        ]
        
        # Filter by automation type if specified
        if automation_type:
            mock_templates = [t for t in mock_templates if t["automation_type"] == automation_type]
        
        # Apply pagination
        total_count = len(mock_templates)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_templates = mock_templates[start_idx:end_idx]
        
        return {
            "status": "success",
            "data": {
                "templates": paginated_templates,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "total_pages": (total_count + page_size - 1) // page_size
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve KB templates: {str(e)}"
        )

@router.get("/kb-status")
async def get_kb_status(
    automation_id: int = Query(..., description="Automation ID to check KB status for"),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get KB status for a specific automation
    """
    try:
        # Validate automation exists
        automation = db.query(Automation).filter(Automation.id == automation_id).first()
        if not automation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation not found"
            )
        
        # Get user automations for this automation
        user_automations = db.query(UserAutomation).filter(
            UserAutomation.automation_id == automation_id
        ).all()
        
        # Mock KB status data (in real implementation, this would call external APIs)
        kb_status = {
            "automation_id": automation_id,
            "automation_name": automation.name,
            "kb_health": "healthy",
            "kb_size": 1024 * 1024,  # 1MB in bytes
            "last_backup": datetime.utcnow().isoformat(),
            "backup_status": "success",
            "error_logs": [],
            "supports_reset": True,
            "total_users": len(user_automations),
            "active_users": len([ua for ua in user_automations if ua.status == "active"]),
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return {
            "status": "success",
            "data": kb_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve KB status: {str(e)}"
        )

@router.get("/kb-monitoring")
async def get_kb_monitoring_overview(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    health_filter: Optional[str] = Query(None, regex="^(healthy|unhealthy|warning)$"),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get KB monitoring overview for all automations
    """
    try:
        # Get all active automations
        automations = db.query(Automation).filter(Automation.status == True).all()
        
        # Get user automations for each automation
        results = []
        for automation in automations:
            user_automations = db.query(UserAutomation).filter(
                UserAutomation.automation_id == automation.id
            ).all()
            
            # Mock KB monitoring data
            kb_health = "healthy"
            if len(user_automations) > 100:
                kb_health = "warning"
            elif len(user_automations) > 500:
                kb_health = "unhealthy"
            
            # Apply health filter
            if health_filter and kb_health != health_filter:
                continue
            
            # Get users for this automation
            user_dict = {}
            for ua in user_automations:
                if ua.user_id not in user_dict:
                    user = db.query(User).filter(User.id == ua.user_id).first()
                    if user:
                        user_dict[ua.user_id] = user
            
            for user_auto in user_automations:
                user = user_dict.get(user_auto.user_id)
                if not user:
                    continue
                
                results.append({
                    "user_id": user.id,
                    "username": user.name,
                    "user_email": user.email,
                    "automation_id": automation.id,
                    "automation_name": automation.name,
                    "user_automation_id": user_auto.id,
                    "kb_health": kb_health,
                    "kb_size": 1024 * 1024,  # Mock size
                    "last_backup": datetime.utcnow().isoformat(),
                    "backup_status": "success",
                    "error_logs": [],
                    "supports_reset": True,
                    "last_updated": datetime.utcnow().isoformat(),
                    "tokens_remaining": user_auto.tokens_remaining,
                    "status": user_auto.status
                })
        
        # Apply pagination
        total_count = len(results)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_results = results[start_idx:end_idx]
        
        # Calculate summary statistics
        health_counts = {
            "healthy": len([r for r in results if r["kb_health"] == "healthy"]),
            "warning": len([r for r in results if r["kb_health"] == "warning"]),
            "unhealthy": len([r for r in results if r["kb_health"] == "unhealthy"])
        }
        
        return {
            "status": "success",
            "data": {
                "monitoring_data": paginated_results,
                "summary": {
                    "total_entries": total_count,
                    "health_counts": health_counts,
                    "last_updated": datetime.utcnow().isoformat()
                },
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "total_pages": (total_count + page_size - 1) // page_size
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve KB monitoring data: {str(e)}"
        )

@router.post("/kb-reset")
async def reset_kb_for_automation(
    automation_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Reset KB for a specific automation
    """
    try:
        # Validate automation exists
        automation = db.query(Automation).filter(Automation.id == automation_id).first()
        if not automation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation not found"
            )
        
        # In a real implementation, this would call external APIs to reset the KB
        # For now, we'll just return a success response
        
        return {
            "status": "success",
            "message": f"KB reset initiated for automation {automation.name}",
            "data": {
                "automation_id": automation_id,
                "automation_name": automation.name,
                "reset_initiated_at": datetime.utcnow().isoformat(),
                "estimated_completion": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset KB: {str(e)}"
        )

@router.get("/kb-backup")
async def create_kb_backup(
    automation_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a backup of KB for a specific automation
    """
    try:
        # Validate automation exists
        automation = db.query(Automation).filter(Automation.id == automation_id).first()
        if not automation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation not found"
            )
        
        # In a real implementation, this would create an actual backup
        # For now, we'll return a mock backup response
        
        backup_id = f"backup_{automation_id}_{int(datetime.utcnow().timestamp())}"
        
        return {
            "status": "success",
            "message": f"KB backup created for automation {automation.name}",
            "data": {
                "backup_id": backup_id,
                "automation_id": automation_id,
                "automation_name": automation.name,
                "backup_size": "1.2 MB",
                "created_at": datetime.utcnow().isoformat(),
                "download_url": f"/api/admin/kb-backup/{backup_id}/download"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create KB backup: {str(e)}"
        )
