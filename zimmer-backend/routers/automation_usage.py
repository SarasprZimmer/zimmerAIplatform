from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from database import SessionLocal
from models.automation import Automation
from models.user_automation import UserAutomation
from schemas.automation import UsageConsumeRequest, UsageConsumeResponse
from utils.auth_dependency import get_db
from utils.service_tokens import verify_token
from services.token_manager import deduct_tokens
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/automation-usage/consume", response_model=UsageConsumeResponse)
def consume_usage(
    usage_data: UsageConsumeRequest,
    x_zimmer_service_token: Optional[str] = Header(None, alias="X-Zimmer-Service-Token"),
    db: Session = Depends(get_db)
):
    if not x_zimmer_service_token:
        raise HTTPException(status_code=401, detail="دسترسی غیرمجاز: توکن سرویس نامعتبر است.")
    
    user_automation = db.query(UserAutomation).filter(
        UserAutomation.id == usage_data.user_automation_id
    ).first()
    
    if not user_automation:
        raise HTTPException(status_code=404, detail="User automation not found")
    
    automation = db.query(Automation).filter(
        Automation.id == user_automation.automation_id
    ).first()
    
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    
    if not automation.service_token_hash:
        logger.error(f"No service token hash for automation {automation.id}")
        raise HTTPException(status_code=401, detail="دسترسی غیرمجاز: توکن سرویس نامعتبر است.")
    
    if not verify_token(x_zimmer_service_token, automation.service_token_hash):
        logger.warning(f"Invalid service token for automation {automation.id}")
        raise HTTPException(status_code=401, detail="دسترسی غیرمجاز: توکن سرویس نامعتبر است.")
    
    result = deduct_tokens(
        db=db,
        user_automation_id=usage_data.user_automation_id,
        amount=usage_data.units,
        usage_type=usage_data.usage_type,
        meta=usage_data.meta
    )
    
    if not result["success"]:
        return UsageConsumeResponse(
            accepted=False,
            remaining_demo_tokens=user_automation.demo_tokens,
            remaining_paid_tokens=user_automation.tokens_remaining or 0,
            message=result["message"]
        )
    
    db.refresh(user_automation)
    
    return UsageConsumeResponse(
        accepted=True,
        remaining_demo_tokens=user_automation.demo_tokens,
        remaining_paid_tokens=user_automation.tokens_remaining or 0,
        message="Token consumption successful"
    )