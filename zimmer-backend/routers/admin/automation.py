from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
import httpx
import os
import secrets
import hashlib
from database import SessionLocal
from models.automation import Automation
from models.user_automation import UserAutomation
from models.user import User
from schemas.automation import ProvisionRequest, ProvisionResponse
from schemas.automation_admin import AutomationCreateRequest, AutomationUpdateRequest, AutomationResponse
from utils.auth_dependency import get_current_admin_user, get_current_user
from database import get_db
from utils.service_tokens import verify_token
from datetime import datetime, timezone
from services.automation_health import probe, classify
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/automations/generate-token")
async def generate_service_token(
    password_data: dict,
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Generate a service token for a new automation (admin only)
    Requires admin password verification
    """
    try:
        # Verify admin password
        from utils.auth import verify_password
        if not verify_password(password_data.get("password", ""), current_admin.password_hash):
            raise HTTPException(
                status_code=401,
                detail="رمز عبور ادمین نادرست است"
            )

        # Generate a secure random token
        service_token = secrets.token_urlsafe(32)
        
        # Hash the token for storage
        token_hash = hashlib.sha256(service_token.encode()).hexdigest()
        
        logger.info(f"Admin {current_admin.email} generated a new service token")
        
        return {
            "token": service_token,
            "message": "توکن سرویس با موفقیت تولید شد. لطفاً آن را در جای امنی ذخیره کنید.",
            "warning": "این توکن فقط یک بار نمایش داده می‌شود"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate service token: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"خطا در تولید توکن سرویس: {str(e)}"
        )

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
                "service_token_masked": (automation.service_token_hash[:8] + "...") if automation.service_token_hash else None,
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

@router.post("/automations", response_model=AutomationResponse)
async def create_automation(
    automation_data: dict,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Create a new automation (admin only)
    """
    try:
        # Extract service token if provided
        service_token = automation_data.pop('service_token', None)
        service_token_hash = None
        
        if service_token:
            # Hash the service token for storage
            service_token_hash = hashlib.sha256(service_token.encode()).hexdigest()
        
        # Create automation with validated data
        automation = Automation(
            name=automation_data.get('name'),
            description=automation_data.get('description'),
            price_per_token=automation_data.get('price_per_token', 0),
            pricing_type=automation_data.get('pricing_type', 'token_per_session'),
            status=automation_data.get('status', True),
            api_base_url=automation_data.get('api_base_url'),
            api_provision_url=automation_data.get('api_provision_url'),
            api_usage_url=automation_data.get('api_usage_url'),
            api_kb_status_url=automation_data.get('api_kb_status_url'),
            api_kb_reset_url=automation_data.get('api_kb_reset_url'),
            health_check_url=automation_data.get('health_check_url'),
            service_token_hash=service_token_hash
        )
        
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
        
        # Return formatted response
        return AutomationResponse(
            id=automation.id,
            name=automation.name,
            description=automation.description,
            price_per_token=automation.price_per_token,
            pricing_type=automation.pricing_type,
            status=automation.status,
            api_base_url=automation.api_base_url,
            api_provision_url=automation.api_provision_url,
            api_usage_url=automation.api_usage_url,
            api_kb_status_url=automation.api_kb_status_url,
            api_kb_reset_url=automation.api_kb_reset_url,
            has_service_token=bool(automation.service_token_hash),
            service_token_masked=(automation.service_token_hash[:8] + "...") if automation.service_token_hash else None,
            health_check_url=automation.health_check_url,
            health_status=automation.health_status,
            last_health_at=automation.last_health_at.isoformat() if automation.last_health_at else None,
            is_listed=automation.is_listed,
            created_at=automation.created_at.isoformat() if automation.created_at else None,
            updated_at=automation.updated_at.isoformat() if automation.updated_at else None
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create automation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create automation: {str(e)}"
        )

@router.put("/automations/{automation_id}", response_model=AutomationResponse)
async def update_automation(
    automation_id: int = Path(...),
    automation_data: AutomationUpdateRequest = None,
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

        logger.info(f"Admin {current_admin.email} attempting to update automation {automation.name} (ID: {automation_id})")

        # Update only the fields that are provided in the request
        if automation_data.name is not None:
            automation.name = automation_data.name
        if automation_data.description is not None:
            automation.description = automation_data.description
        if automation_data.price_per_token is not None:
            automation.price_per_token = automation_data.price_per_token
        if automation_data.pricing_type is not None:
            automation.pricing_type = automation_data.pricing_type
        if automation_data.status is not None:
            automation.status = automation_data.status
        if automation_data.api_base_url is not None:
            automation.api_base_url = automation_data.api_base_url
        if automation_data.api_provision_url is not None:
            automation.api_provision_url = automation_data.api_provision_url
        if automation_data.api_usage_url is not None:
            automation.api_usage_url = automation_data.api_usage_url
        if automation_data.api_kb_status_url is not None:
            automation.api_kb_status_url = automation_data.api_kb_status_url
        if automation_data.api_kb_reset_url is not None:
            automation.api_kb_reset_url = automation_data.api_kb_reset_url
        if automation_data.health_check_url is not None:
            automation.health_check_url = automation_data.health_check_url

        # Update the updated_at timestamp
        automation.updated_at = datetime.now(timezone.utc)
        
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
        
        logger.info(f'✅ Successfully updated automation {automation.name} (ID: {automation_id})')
        
        # Return formatted response
        return AutomationResponse(
            id=automation.id,
            name=automation.name,
            description=automation.description,
            price_per_token=automation.price_per_token,
            pricing_type=automation.pricing_type,
            status=automation.status,
            api_base_url=automation.api_base_url,
            api_provision_url=automation.api_provision_url,
            api_usage_url=automation.api_usage_url,
            api_kb_status_url=automation.api_kb_status_url,
            api_kb_reset_url=automation.api_kb_reset_url,
            has_service_token=bool(automation.service_token_hash),
            service_token_masked=automation.service_token_masked,
            health_check_url=automation.health_check_url,
            health_status=automation.health_status,
            last_health_at=automation.last_health_at.isoformat() if automation.last_health_at else None,
            is_listed=automation.is_listed,
            created_at=automation.created_at.isoformat() if automation.created_at else None,
            updated_at=automation.updated_at.isoformat() if automation.updated_at else None
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f'❌ Failed to update automation {automation_id}: {e}')
        raise HTTPException(
            status_code=500,
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
    Handles foreign key constraints by deleting related records first
    """
    try:
        automation = db.query(Automation).filter(Automation.id == automation_id).first()
        if not automation:
            raise HTTPException(status_code=404, detail="Automation not found")

        logger.info(f"Admin {current_admin.email} attempting to delete automation {automation.name} (ID: {automation_id})")

        # Use completely separate database connections to avoid transaction issues
        from sqlalchemy import create_engine
        import os
        
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise HTTPException(status_code=500, detail="Database configuration error")
        
        # Create a new engine for separate connections
        separate_engine = create_engine(database_url)
        
        # List of tables to clean up
        cleanup_operations = [
            ('kb_templates', f'DELETE FROM kb_templates WHERE automation_id = {automation_id}'),
            ('openai_key_usage', f'DELETE FROM openai_key_usage WHERE openai_key_id IN (SELECT id FROM openai_keys WHERE automation_id = {automation_id})'),
            ('openai_keys', f'DELETE FROM openai_keys WHERE automation_id = {automation_id}'),
            ('payments', f'DELETE FROM payments WHERE automation_id = {automation_id}'),
            ('user_automations', f'DELETE FROM user_automations WHERE automation_id = {automation_id}'),
            ('kb_status_history', f'DELETE FROM kb_status_history WHERE automation_id = {automation_id}')
        ]
        
        # Clean up each table using separate connections
        for table_name, sql_query in cleanup_operations:
            try:
                # Use a separate connection for each operation
                with separate_engine.begin() as conn:
                    conn.execute(text(sql_query))
                logger.info(f'✅ Deleted from {table_name} for automation {automation_id}')
            except Exception as e:
                if "relation "" in str(e) and "" does not exist" in str(e):
                    logger.warning(f'⚠️  Table {table_name} does not exist, skipping')
                else:
                    logger.warning(f'⚠️  Could not delete from {table_name}: {str(e)[:100]}...')
                # Continue with next table
        
        # Finally delete the automation itself using the main session
        db.query(Automation).filter(Automation.id == automation_id).delete()
        db.commit()
        
        logger.info(f'✅ Successfully deleted automation {automation.name} (ID: {automation_id})')
        return {"message": f"Automation {automation.name} deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f'❌ Failed to delete automation {automation_id}: {e}')
        raise HTTPException(status_code=500, detail=f"Failed to delete automation: {str(e)}")
    finally:
        # Close the separate engine
        if 'separate_engine' in locals():
            separate_engine.dispose()
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