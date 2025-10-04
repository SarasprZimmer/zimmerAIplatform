from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
import httpx
import os
from database import SessionLocal
from models.automation import Automation
from models.user_automation import UserAutomation
from models.user import User
from schemas.automation import ProvisionRequest, ProvisionResponse
from utils.auth_dependency import get_current_user
from database import get_db
from utils.service_tokens import verify_token
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/automations")
def list_automations(db: Session = Depends(get_db)):
    """List all public automations"""
    automations = db.query(Automation).filter(Automation.is_listed == "true").all()
    return {"automations": automations}

@router.get("/automations/marketplace")
def get_marketplace_automations(db: Session = Depends(get_db)):
    """Get automations available in the marketplace (public endpoint)"""
    automations = db.query(Automation).filter(
        Automation.status == True,
        Automation.is_listed == True,
        Automation.health_status == "healthy",
        Automation.service_token_hash.isnot(None)  # Must have service token
    ).all()

    marketplace_data = []
    for automation in automations:
        marketplace_data.append({
            "id": automation.id,
            "name": automation.name,
            "description": automation.description,
            "pricing_type": automation.pricing_type,
            "price_per_token": automation.price_per_token,
            "health_status": automation.health_status,
            "last_health_at": automation.last_health_at,
            "created_at": automation.created_at
        })

    return {
        "automations": marketplace_data,
        "total": len(marketplace_data),
        "message": "Available automations in marketplace"
    }

@router.get("/automations/available")
def get_available_automations(db: Session = Depends(get_db)):
    """Get available automations for users (public endpoint)"""
    try:
        automations = db.query(Automation).filter(
            Automation.status == True,
            Automation.is_listed == True,
            Automation.health_status == "healthy",
            Automation.service_token_hash.isnot(None)  # Must have service token
        ).all()

        available_data = []
        for automation in automations:
            available_data.append({
                "id": automation.id,
                "name": automation.name,
                "description": automation.description,
                "pricing_type": automation.pricing_type,
                "price_per_token": automation.price_per_token,
                "health_status": automation.health_status,
                "created_at": automation.created_at.isoformat() if automation.created_at else None
            })

        return available_data
    except Exception as e:
        logger.error(f"Error fetching available automations: {e}")
        raise HTTPException(status_code=500, detail="خطا در بارگذاری اتوماسیون‌ها")

@router.post("/automations/{automation_id}/provision", response_model=ProvisionResponse)
async def provision_automation(
    automation_id: int = Path(...),
    provision_data: ProvisionRequest = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    automation = db.query(Automation).filter(Automation.id == automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")

    user_automation = db.query(UserAutomation).filter(
        UserAutomation.id == provision_data.user_automation_id,
        UserAutomation.user_id == current_user.id,
        UserAutomation.automation_id == automation_id
    ).first()

    if not user_automation:
        raise HTTPException(status_code=404, detail="User automation not found")

    if not automation.api_provision_url:
        raise HTTPException(status_code=400, detail="این اتوماسیون قابلیت اتصال مستقیم ندارد")

    service_token = os.getenv(f"AUTOMATION_{automation_id}_SERVICE_TOKEN")
    if not service_token:
        logger.error(f"No service token found for automation {automation_id}")
        raise HTTPException(status_code=500, detail="خطا در پیکربندی سرویس")

    if not verify_token(service_token, automation.service_token_hash):
        logger.error(f"Invalid service token for automation {automation_id}")
        raise HTTPException(status_code=500, detail="خطا در احراز هویت سرویس")

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
                user_automation.provisioned_at = datetime.utcnow()
                user_automation.integration_status = "active"
                db.commit()

                return ProvisionResponse(
                    success=True,
                    message="اتصال با سرویس اتوماسیون برقرار شد ✅",
                    provisioned_at=user_automation.provisioned_at,
                    integration_status=user_automation.integration_status
                )
            else:
                logger.error(f"External automation returned {response.status_code}: {response.text}")
                raise HTTPException(status_code=502, detail="اتصال با سرویس اتوماسیون برقرار نشد. لطفاً بعداً دوباره تلاش کنید.")

    except httpx.RequestError as e:
        logger.error(f"Network error calling external automation: {e}")
        raise HTTPException(status_code=502, detail="اتصال با سرویس اتوماسیون برقرار نشد. لطفاً بعداً دوباره تلاش کنید.")
    except Exception as e:
        logger.error(f"Unexpected error during provision: {e}")
        raise HTTPException(status_code=500, detail="خطای غیرمنتظره در اتصال")
