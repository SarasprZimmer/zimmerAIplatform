from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Dict, Any

from database import get_db
from models.automation import Automation
from services.automation_health import probe, classify
from utils.auth import get_current_admin_user

router = APIRouter(prefix="/api/admin/automations", tags=["admin:automations"])

@router.post("/{automation_id}/health-check")
async def run_health_check(
    automation_id: int = Path(..., description="Automation ID"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user),
) -> Dict[str, Any]:
    """
    Run health check for an automation
    
    Args:
        automation_id: ID of the automation to check
        db: Database session
        current_user: Current admin user
        
    Returns:
        Health check results
    """
    a = db.query(Automation).get(automation_id)
    if not a:
        raise HTTPException(status_code=404, detail="automation_not_found")
    
    result = await probe(a.health_check_url)
    status = classify(result)
    
    a.health_status = status
    a.last_health_at = datetime.now(timezone.utc)
    a.health_details = result
    # Gate listing: only list when healthy
    a.is_listed = (status == "healthy")
    
    db.commit()
    db.refresh(a)
    
    return {
        "automation_id": a.id,
        "health_status": a.health_status,
        "is_listed": a.is_listed,
        "last_health_at": a.last_health_at,
        "details": a.health_details,
    }
