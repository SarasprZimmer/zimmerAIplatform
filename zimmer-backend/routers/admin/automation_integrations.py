from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from database import SessionLocal
from models.automation import Automation
from models.user import User
from schemas.automation import TokenRotationResponse, AutomationIntegrationResponse
from utils.auth_dependency import get_current_admin_user
from database import get_db
from utils.service_tokens import generate_token, hash_token, mask_token
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/automations/{automation_id}/rotate-token", response_model=TokenRotationResponse)
def rotate_service_token(
    automation_id: int = Path(...),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Generate a new service token for an automation and store only the hash
    """
    automation = db.query(Automation).filter(Automation.id == automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    
    # Generate new token and hash
    new_token = generate_token()
    token_hash = hash_token(new_token)
    
    # Store only the hash
    automation.service_token_hash = token_hash
    automation.updated_at = datetime.utcnow()
    db.commit()
    
    # Log the rotation event
    logger.info(f"Service token rotated for automation {automation_id} by admin {current_admin.id}")
    
    return TokenRotationResponse(
        automation_id=automation_id,
        new_token=new_token,
        masked_token=mask_token(new_token),
        rotated_at=datetime.utcnow(),
        message="Service token rotated successfully"
    )

@router.get("/automations/{automation_id}/integration", response_model=AutomationIntegrationResponse)
def get_automation_integration(
    automation_id: int = Path(...),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Get automation integration information including masked token
    """
    automation = db.query(Automation).filter(Automation.id == automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    
    # Create a masked token if we have a hash
    masked_token = None
    if automation.service_token_hash:
        # Generate a consistent masked version for display
        masked_token = "****" + "abcd"  # This will be consistent for display purposes
    
    return AutomationIntegrationResponse(
        id=automation.id,
        name=automation.name,
        api_base_url=automation.api_base_url,
        api_provision_url=automation.api_provision_url,
        api_usage_url=automation.api_usage_url,
        api_kb_status_url=automation.api_kb_status_url,
        api_kb_reset_url=automation.api_kb_reset_url,
        service_token_masked=masked_token,
        has_service_token=bool(automation.service_token_hash)
    )
