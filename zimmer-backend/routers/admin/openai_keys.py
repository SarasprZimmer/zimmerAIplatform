from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import time
import httpx

from database import get_db
from utils.auth_dependency import get_current_admin_user
from models.user import User
from models.openai_key import OpenAIKey, OpenAIKeyStatus
from models.openai_key_usage import OpenAIKeyUsage, UsageStatus
from schemas.openai_key import (
    OpenAIKeyCreate, OpenAIKeyUpdate, OpenAIKeyOut, OpenAIKeyUsageOut,
    OpenAIKeyTestResponse, OpenAIKeyStatusUpdate
)
from utils.crypto import encrypt_secret, mask_secret
from services.openai_key_manager import OpenAIKeyManager

router = APIRouter(tags=["admin-openai-keys"])

@router.post("/", response_model=OpenAIKeyOut)
async def create_openai_key(
    key_data: OpenAIKeyCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Create a new OpenAI key for an automation"""
    
    # Check if automation exists
    from models.automation import Automation
    automation = db.query(Automation).filter(Automation.id == key_data.automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="اتوماسیون یافت نشد")
    
    # Check if alias already exists for this automation
    existing_key = db.query(OpenAIKey).filter(
        OpenAIKey.automation_id == key_data.automation_id,
        OpenAIKey.alias == key_data.alias
    ).first()
    if existing_key:
        raise HTTPException(status_code=400, detail="نام مستعار برای این اتوماسیون قبلاً استفاده شده است")
    
    # Encrypt the API key
    try:
        encrypted_key = encrypt_secret(key_data.api_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail="خطا در رمزگذاری کلید API")
    
    # Create the key
    new_key = OpenAIKey(
        automation_id=key_data.automation_id,
        alias=key_data.alias,
        key_encrypted=encrypted_key,
        status=key_data.status,
        rpm_limit=key_data.rpm_limit,
        daily_token_limit=key_data.daily_token_limit
    )
    
    db.add(new_key)
    db.commit()
    db.refresh(new_key)
    
    # Return with masked key
    return OpenAIKeyOut(
        **{k: v for k, v in new_key.__dict__.items() if not k.startswith('_')},
        masked_key=mask_secret(key_data.api_key)
    )

@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify router is working"""
    return {"message": "OpenAI keys router is working"}

@router.get("/list", response_model=List[OpenAIKeyOut])
async def list_openai_keys(
    automation_id: Optional[int] = Query(None, description="Filter by automation ID"),
    status: Optional[OpenAIKeyStatus] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """List OpenAI keys with optional filters"""
    
    query = db.query(OpenAIKey)
    
    if automation_id:
        query = query.filter(OpenAIKey.automation_id == automation_id)
    
    if status:
        query = query.filter(OpenAIKey.status == status)
    
    keys = query.all()
    
    # Return with masked keys
    result = []
    for key in keys:
        # Decrypt and mask for display
        try:
            from utils.crypto import decrypt_secret
            decrypted = decrypt_secret(key.key_encrypted)
            masked = mask_secret(decrypted)
        except:
            masked = "***"
        
        result.append(OpenAIKeyOut(
            **{k: v for k, v in key.__dict__.items() if not k.startswith('_')},
            masked_key=masked
        ))
    
    return result

@router.get("/keys/{key_id}", response_model=OpenAIKeyOut)
async def get_openai_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get a specific OpenAI key"""
    
    key = db.query(OpenAIKey).filter(OpenAIKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="کلید OpenAI یافت نشد")
    
    # Decrypt and mask for display
    try:
        from utils.crypto import decrypt_secret
        decrypted = decrypt_secret(key.key_encrypted)
        masked = mask_secret(decrypted)
    except:
        masked = "***"
    
    return OpenAIKeyOut(
        **{k: v for k, v in key.__dict__.items() if not k.startswith('_')},
        masked_key=masked
    )

@router.put("/keys/{key_id}", response_model=OpenAIKeyOut)
async def update_openai_key(
    key_id: int,
    key_data: OpenAIKeyUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Update an OpenAI key"""
    
    key = db.query(OpenAIKey).filter(OpenAIKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="کلید OpenAI یافت نشد")
    
    # Update fields
    if key_data.alias is not None:
        # Check if alias already exists for this automation
        existing_key = db.query(OpenAIKey).filter(
            OpenAIKey.automation_id == key.automation_id,
            OpenAIKey.alias == key_data.alias,
            OpenAIKey.id != key_id
        ).first()
        if existing_key:
            raise HTTPException(status_code=400, detail="نام مستعار برای این اتوماسیون قبلاً استفاده شده است")
        key.alias = key_data.alias
    
    if key_data.api_key is not None:
        # Re-encrypt the new API key
        try:
            key.key_encrypted = encrypt_secret(key_data.api_key)
        except Exception as e:
            raise HTTPException(status_code=500, detail="خطا در رمزگذاری کلید API")
    
    if key_data.rpm_limit is not None:
        key.rpm_limit = key_data.rpm_limit
    
    if key_data.daily_token_limit is not None:
        key.daily_token_limit = key_data.daily_token_limit
    
    if key_data.status is not None:
        key.status = key_data.status
    
    db.commit()
    db.refresh(key)
    
    # Return with masked key
    try:
        from utils.crypto import decrypt_secret
        decrypted = decrypt_secret(key.key_encrypted)
        masked = mask_secret(decrypted)
    except:
        masked = "***"
    
    return OpenAIKeyOut(
        **{k: v for k, v in key.__dict__.items() if not k.startswith('_')},
        masked_key=masked
    )

@router.patch("/keys/{key_id}/status", response_model=OpenAIKeyOut)
async def update_key_status(
    key_id: int,
    status_data: OpenAIKeyStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Update the status of an OpenAI key"""
    
    key = db.query(OpenAIKey).filter(OpenAIKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="کلید OpenAI یافت نشد")
    
    key.status = status_data.status
    db.commit()
    db.refresh(key)
    
    # Return with masked key
    try:
        from utils.crypto import decrypt_secret
        decrypted = decrypt_secret(key.key_encrypted)
        masked = mask_secret(decrypted)
    except:
        masked = "***"
    
    return OpenAIKeyOut(
        **{k: v for k, v in key.__dict__.items() if not k.startswith('_')},
        masked_key=masked
    )

@router.post("/keys/{key_id}/test", response_model=OpenAIKeyTestResponse)
async def test_openai_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Test an OpenAI key with a simple API call"""
    
    key_manager = OpenAIKeyManager(db)
    key_data = key_manager.get_key_with_decrypted(key_id)
    
    if not key_data:
        raise HTTPException(status_code=404, detail="کلید OpenAI یافت نشد")
    
    key, decrypted_key = key_data
    
    if key.status != OpenAIKeyStatus.ACTIVE:
        return OpenAIKeyTestResponse(
            success=False,
            error_message="کلید غیرفعال است"
        )
    
    # Test the key with a simple API call
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {decrypted_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": "ping"}],
                    "max_tokens": 10
                },
                timeout=10.0
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                model = data.get("model", "unknown")
                return OpenAIKeyTestResponse(
                    success=True,
                    latency_ms=latency_ms,
                    model=model
                )
            else:
                return OpenAIKeyTestResponse(
                    success=False,
                    latency_ms=latency_ms,
                    error_message=f"خطای API: {response.status_code}"
                )
    
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        return OpenAIKeyTestResponse(
            success=False,
            latency_ms=latency_ms,
            error_message=str(e)
        )

# TEMPORARILY COMMENTED OUT TO RESOLVE ROUTE CONFLICT WITH /usage/stats
# @router.get("/usage", response_model=List[OpenAIKeyUsageOut])
# async def get_key_usage(
#     automation_id: Optional[int] = Query(None, description="Filter by automation ID"),
#     key_id: Optional[int] = Query(None, description="Filter by key ID"),
#     status: Optional[UsageStatus] = Query(None, description="Filter by status"),
#     date_from: Optional[datetime] = Query(None, description="Filter from date"),
#     date_to: Optional[datetime] = Query(None, description="Filter to date"),
#     limit: int = Query(100, le=1000, description="Number of records to return"),
#     offset: int = Query(0, ge=0, description="Number of records to skip"),
#     db: Session = Depends(get_db),
#     current_admin: User = Depends(get_current_admin_user)
# ):
#     """Get OpenAI key usage audit records"""
#     
#     query = db.query(OpenAIKeyUsage)
#     
#     if automation_id:
#         query = query.filter(OpenAIKeyUsage.automation_id == automation_id)
#     
#     if key_id:
#         query = query.filter(OpenAIKeyUsage.openai_key_id == key_id)
#     
#     if status:
#         query = query.filter(OpenAIKeyUsage.status == status)
#     
#     if date_from:
#         query = query.filter(OpenAIKeyUsage.created_at >= date_from)
#     
#     if date_to:
#         query = query.filter(OpenAIKeyUsage.created_at <= date_to)
#     
#     # Order by newest first
#     query = query.order_by(OpenAIKeyUsage.created_at.desc())
#     
#     # Pagination
#     query = query.offset(offset).limit(limit)
#     
#     return query.all()

@router.delete("/keys/{key_id}")
async def delete_openai_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Delete an OpenAI key"""
    
    key = db.query(OpenAIKey).filter(OpenAIKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="کلید OpenAI یافت نشد")
    
    db.delete(key)
    db.commit()
    
    return {"message": "کلید با موفقیت حذف شد"}

@router.post("/reset-daily")
async def reset_daily_usage(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Manually reset daily token usage for all keys"""
    
    key_manager = OpenAIKeyManager(db)
    reset_count = key_manager.reset_daily_usage()
    
    return {
        "message": f"بازنشانی استفاده روزانه برای {reset_count} کلید انجام شد",
        "reset_count": reset_count
    }
