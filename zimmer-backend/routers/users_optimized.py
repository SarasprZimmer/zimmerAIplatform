"""
Optimized User Endpoints for Zimmer AI Platform
Implements caching and performance optimizations to fix timeout issues
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
import time

from database import get_db
from models.user import User
from models.user_automation import UserAutomation
from models.automation import Automation
from models.token_usage import TokenUsage
from utils.auth_optimized import get_current_user_optimized, invalidate_user_cache
from utils.circuit_breaker import user_circuit_breaker
from schemas.user import UserResponse, UserUpdateRequest
from cache_manager import cache_manager

router = APIRouter(prefix="/api/optimized/user", tags=["users-optimized"])

# Cache TTL settings
USER_DATA_CACHE_TTL = 300  # 5 minutes
USER_USAGE_CACHE_TTL = 180  # 3 minutes
USER_AUTOMATIONS_CACHE_TTL = 300  # 5 minutes

@router.get("/me", response_model=UserResponse)
@user_circuit_breaker
async def get_current_user_info_optimized(
    current_user: User = Depends(get_current_user_optimized)
):
    """
    Get current user's basic information (optimized with caching and circuit breaker)
    """
    cache_key = f"user_info_{current_user.id}"
    cached_data = cache_manager.get(cache_key)
    
    if cached_data:
        return UserResponse(**cached_data)
    
    try:
        user_data = UserResponse.from_orm(current_user)
        cache_manager.set(cache_key, user_data.dict(), ttl=USER_DATA_CACHE_TTL)
        return user_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user info: {str(e)}"
        )

@router.put("/profile", response_model=UserResponse)
async def update_user_profile_optimized(
    user_data: UserUpdateRequest,
    current_user: User = Depends(get_current_user_optimized),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile information (optimized)
    """
    try:
        # Update user fields if provided
        if user_data.name is not None:
            current_user.name = user_data.name
        if user_data.phone_number is not None:
            current_user.phone_number = user_data.phone_number
        
        db.commit()
        db.refresh(current_user)
        
        # Invalidate user cache
        invalidate_user_cache(current_user.id)
        cache_manager.delete(f"user_info_{current_user.id}")
        
        return current_user
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user profile: {str(e)}"
        )

@router.get("/usage")
async def get_user_token_usage_optimized(
    current_user: User = Depends(get_current_user_optimized),
    db: Session = Depends(get_db)
):
    """
    Get user's token usage statistics (optimized with caching)
    """
    cache_key = f"user_usage_{current_user.id}"
    cached_data = cache_manager.get(cache_key)
    
    if cached_data:
        return cached_data
    
    try:
        # Get user automations with tokens
        user_automations = db.query(UserAutomation).filter(
            UserAutomation.user_id == current_user.id,
            UserAutomation.status == "active"
        ).all()
        
        total_tokens = sum(ua.tokens_remaining for ua in user_automations)
        
        # Get recent token usage (last 30 days)
        thirty_days_ago = datetime.utcnow() - timezone.utc.localize(datetime.timedelta(days=30))
        recent_usage = db.query(TokenUsage).filter(
            TokenUsage.user_id == current_user.id,
            TokenUsage.created_at >= thirty_days_ago
        ).all()
        
        used_tokens = sum(usage.tokens_used for usage in recent_usage)
        
        usage_data = {
            "total_tokens": total_tokens,
            "used_tokens": used_tokens,
            "remaining_tokens": total_tokens - used_tokens,
            "automations_count": len(user_automations),
            "usage_period": "30_days"
        }
        
        cache_manager.set(cache_key, usage_data, ttl=USER_USAGE_CACHE_TTL)
        return usage_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve usage data: {str(e)}"
        )

@router.get("/usage/distribution")
async def get_user_usage_distribution_optimized(
    current_user: User = Depends(get_current_user_optimized),
    db: Session = Depends(get_db)
):
    """
    Get user's token usage distribution by automation (optimized)
    """
    cache_key = f"user_usage_dist_{current_user.id}"
    cached_data = cache_manager.get(cache_key)
    
    if cached_data:
        return cached_data
    
    try:
        # Get user automations with usage data
        user_automations = db.query(UserAutomation).filter(
            UserAutomation.user_id == current_user.id
        ).all()
        
        distribution = []
        for ua in user_automations:
            automation = db.query(Automation).filter(
                Automation.id == ua.automation_id
            ).first()
            
            if automation:
                # Get usage for this automation
                usage = db.query(TokenUsage).filter(
                    TokenUsage.user_automation_id == ua.id
                ).all()
                
                used_tokens = sum(u.tokens_used for u in usage)
                
                distribution.append({
                    "automation_id": automation.id,
                    "automation_name": automation.name,
                    "tokens_remaining": ua.tokens_remaining,
                    "tokens_used": used_tokens,
                    "total_tokens": ua.tokens_remaining + used_tokens
                })
        
        cache_manager.set(cache_key, distribution, ttl=USER_USAGE_CACHE_TTL)
        return distribution
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve usage distribution: {str(e)}"
        )

@router.get("/automations/active")
async def get_user_active_automations_optimized(
    current_user: User = Depends(get_current_user_optimized),
    db: Session = Depends(get_db)
):
    """
    Get user's active automations (optimized with caching)
    """
    cache_key = f"user_automations_{current_user.id}"
    cached_data = cache_manager.get(cache_key)
    
    if cached_data:
        return cached_data
    
    try:
        # Get user automations with automation details
        user_automations = db.query(UserAutomation).filter(
            UserAutomation.user_id == current_user.id,
            UserAutomation.status == "active"
        ).all()
        
        automations = []
        for ua in user_automations:
            automation = db.query(Automation).filter(
                Automation.id == ua.automation_id
            ).first()
            
            if automation:
                automations.append({
                    "id": automation.id,
                    "name": automation.name,
                    "description": automation.description,
                    "tokens_remaining": ua.tokens_remaining,
                    "status": ua.status,
                    "provisioned_at": ua.provisioned_at.isoformat() if ua.provisioned_at else None,
                    "integration_status": ua.integration_status
                })
        
        cache_manager.set(cache_key, automations, ttl=USER_AUTOMATIONS_CACHE_TTL)
        return automations
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve active automations: {str(e)}"
        )

@router.post("/password")
@user_circuit_breaker
async def change_user_password_optimized(
    request: dict,
    current_user: User = Depends(get_current_user_optimized),
    db: Session = Depends(get_db)
):
    """
    Change user password (optimized with circuit breaker)
    """
    try:
        new_password = request.get("new_password")
        confirm_password = request.get("confirm_password")
        
        if not new_password or not confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="رمز عبور جدید و تکرار آن الزامی است"
            )
        
        if new_password != confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="رمز عبور و تکرار آن یکسان نیست"
            )
        
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="رمز عبور باید حداقل 8 کاراکتر باشد"
            )
        
        # Hash new password
        from utils.auth import hash_password
        current_user.password_hash = hash_password(new_password)
        db.commit()
        
        # Invalidate user cache
        invalidate_user_cache(current_user.id)
        cache_manager.delete(f"user_info_{current_user.id}")
        
        return {"message": "رمز عبور با موفقیت تغییر یافت"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="خطا در تغییر رمز عبور"
        )

@router.get("/cache/stats")
async def get_user_cache_stats():
    """Get user-related cache statistics"""
    stats = cache_manager.get_stats()
    
    # Count user-specific cache entries
    user_cache_keys = [
        key for key in cache_manager._cache.keys() 
        if key.startswith("user_") or key.startswith("user_data_")
    ]
    
    return {
        "total_cache_entries": stats["total_entries"],
        "active_cache_entries": stats["active_entries"],
        "user_cache_entries": len(user_cache_keys),
        "cache_ttl": stats["default_ttl"],
        "current_time": stats["current_time"]
    }
