from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from typing import Optional
import httpx
import os
from database import SessionLocal
from models.automation import Automation
from models.user_automation import UserAutomation
from models.user import User
from schemas.automation import ProvisionRequest, ProvisionResponse
from utils.auth_dependency import get_current_admin_user, get_current_user, get_db
from utils.service_tokens import verify_token
from datetime import datetime, timezone
from services.automation_health import probe, classify
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/automations")
async def get_automations(
    status: Optional[bool] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Get all automations (admin only)
    """
    try:
        query = db.query(Automation)
        
        # Apply filters if provided
        if status is not None:
            query = query.filter(Automation.status == status)
        
        # Get automations ordered by newest first
        automations = query.order_by(Automation.created_at.desc()).all()
        
        # Format response
        formatted_automations = []
        for automation in automations:
            formatted_automations.append({
                "id": automation.id,
                "name": automation.name,
                "description": automation.description,
                "pricing_type": automation.pricing_type,
                "price_per_token": automation.price_per_token,
                "status": automation.status,
                "api_base_url": automation.api_base_url,
                "api_provision_url": automation.api_provision_url,
                "api_usage_url": automation.api_usage_url,
                "api_kb_status_url": automation.api_kb_status_url,
                "api_kb_reset_url": automation.api_kb_reset_url,
                "has_service_token": bool(automation.service_token_hash),
                "service_token_masked": automation.service_token_hash[:8] + "..." if automation.service_token_hash else None,
                "health_check_url": automation.health_check_url,
                "health_status": automation.health_status,
                "last_health_at": automation.last_health_at,
                "is_listed": automation.is_listed,
                "created_at": automation.created_at,
                "updated_at": automation.updated_at
            })
        
        return formatted_automations
        
    except Exception as e:
        logger.error(f"Failed to retrieve automations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve automations: {str(e)}"
        )

@router.post("/automations")
async def create_automation(
    automation_data: dict,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Create a new automation (admin only)
    """
    try:
        automation = Automation(**automation_data)
        db.add(automation)
        db.commit()
        db.refresh(automation)
        
        # Run health check if health_check_url is provided
        if automation.health_check_url:
            result = await probe(automation.health_check_url)
            automation.health_status = classify(result)
            automation.last_health_at = datetime.now(timezone.utc)
            automation.health_details = result
            automation.is_listed = (automation.health_status == "healthy")
        else:
            automation.health_status = "unknown"
            automation.is_listed = False
        
        db.commit()
        db.refresh(automation)
        return automation
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create automation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create automation: {str(e)}"
        )

@router.put("/automations/{automation_id}")
async def update_automation(
    automation_id: int = Path(...),
    automation_data: dict = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Update an existing automation (admin only)
    """
    try:
        automation = db.query(Automation).filter(Automation.id == automation_id).first()
        if not automation:
            raise HTTPException(status_code=404, detail="Automation not found")
        
        # Update fields if provided
        if automation_data:
            for field, value in automation_data.items():
                if hasattr(automation, field):
                    setattr(automation, field, value)
            automation.updated_at = datetime.utcnow()
            
            # Run health check if health_check_url was provided or changed
            if automation.health_check_url:
                result = await probe(automation.health_check_url)
                automation.health_status = classify(result)
                automation.last_health_at = datetime.now(timezone.utc)
                automation.health_details = result
                automation.is_listed = (automation.health_status == "healthy")
            else:
                automation.health_status = "unknown"
                automation.is_listed = False
            
            db.commit()
            db.refresh(automation)
        
        return automation
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update automation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update automation: {str(e)}"
        )

@router.delete("/automations/{automation_id}")
async def delete_automation(
    automation_id: int = Path(...),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Delete an automation (admin only)
    """
    try:
        automation = db.query(Automation).filter(Automation.id == automation_id).first()
        if not automation:
            raise HTTPException(status_code=404, detail="Automation not found")
        
        db.delete(automation)
        db.commit()
        return {"message": "Automation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete automation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete automation: {str(e)}"
        )

@router.post("/automations/{automation_id}/provision", response_model=ProvisionResponse)
async def provision_automation(
    automation_id: int = Path(...),
    provision_data: ProvisionRequest = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Provision a user automation with the external automation service
    """
    # Fetch automation
    automation = db.query(Automation).filter(Automation.id == automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    
    # Verify user automation belongs to current user
    user_automation = db.query(UserAutomation).filter(
        UserAutomation.id == provision_data.user_automation_id,
        UserAutomation.user_id == current_user.id,
        UserAutomation.automation_id == automation_id
    ).first()
    
    if not user_automation:
        raise HTTPException(status_code=404, detail="User automation not found")
    
    # Check if automation has provision URL
    if not automation.api_provision_url:
        raise HTTPException(
            status_code=400, 
            detail="این اتوماسیون قابلیت اتصال مستقیم ندارد"
        )
    
    # Get service token from environment (for MVP)
    # TODO: Replace with secure secret manager in production
    service_token = os.getenv(f"AUTOMATION_{automation_id}_SERVICE_TOKEN")
    if not service_token:
        logger.error(f"No service token found for automation {automation_id}")
        raise HTTPException(
            status_code=500,
            detail="خطا در پیکربندی سرویس"
        )
    
    # Verify service token hash
    if not verify_token(service_token, automation.service_token_hash):
        logger.error(f"Invalid service token for automation {automation_id}")
        raise HTTPException(
            status_code=500,
            detail="خطا در احراز هویت سرویس"
        )
    
    # Prepare request to external automation
    provision_payload = {
        "user_automation_id": user_automation.id,
        "user_id": current_user.id,
        "bot_token": provision_data.bot_token,
        "demo_tokens": user_automation.demo_tokens
    }
    
    headers = {
        "X-Zimmer-Service-Token": service_token,
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                automation.api_provision_url,
                json=provision_payload,
                headers=headers
            )
            
            if response.status_code == 200:
                # Update user automation with provision info
                user_automation.provisioned_at = datetime.utcnow()
                user_automation.integration_status = "active"
                
                # Save any returned fields from external service
                response_data = response.json()
                if "webhook_url" in response_data:
                    # Store webhook URL if provided
                    pass  # Add field to UserAutomation if needed
                
                db.commit()
                
                return ProvisionResponse(
                    success=True,
                    message="اتصال با سرویس اتوماسیون برقرار شد ✅",
                    provisioned_at=user_automation.provisioned_at,
                    integration_status=user_automation.integration_status
                )
            else:
                logger.error(f"External automation returned {response.status_code}: {response.text}")
                raise HTTPException(
                    status_code=502,
                    detail="اتصال با سرویس اتوماسیون برقرار نشد. لطفاً بعداً دوباره تلاش کنید."
                )
                
    except httpx.RequestError as e:
        logger.error(f"Network error calling external automation: {e}")
        raise HTTPException(
            status_code=502,
            detail="اتصال با سرویس اتوماسیون برقرار نشد. لطفاً بعداً دوباره تلاش کنید."
        )
    except Exception as e:
        logger.error(f"Unexpected error during provision: {e}")
        raise HTTPException(
            status_code=500,
            detail="خطای غیرمنتظره در اتصال به سرویس"
        )