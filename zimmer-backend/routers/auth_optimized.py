"""
Optimized Authentication Endpoints for Zimmer AI Platform
Implements caching and performance optimizations to fix timeout issues
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone
import time

from database import get_db
from models.user import User
from models.twofa import TwoFactorRecoveryCode
from models.email_verification import EmailVerificationToken
from utils.auth_optimized import get_current_user_optimized, rate_limit_dependency
from utils.circuit_breaker import auth_circuit_breaker, login_circuit_breaker
from cache_manager import cache_manager

router = APIRouter(prefix="/api/optimized/auth", tags=["auth-optimized"])

# Cache TTL settings
AUTH_CACHE_TTL = 300  # 5 minutes
CSRF_CACHE_TTL = 1800  # 30 minutes
EMAIL_VERIFY_CACHE_TTL = 600  # 10 minutes

@router.get("/csrf")
@auth_circuit_breaker
async def get_csrf_token_optimized():
    """
    Get CSRF token (optimized with caching and circuit breaker)
    """
    cache_key = "csrf_token"
    cached_token = cache_manager.get(cache_key)
    
    if cached_token:
        return {"csrf_token": cached_token}
    
    try:
        # Generate new CSRF token
        import secrets
        csrf_token = secrets.token_urlsafe(32)
        
        cache_manager.set(cache_key, csrf_token, ttl=CSRF_CACHE_TTL)
        
        return {"csrf_token": csrf_token}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate CSRF token: {str(e)}"
        )

@router.get("/2fa/status")
@auth_circuit_breaker
async def get_2fa_status_optimized(
    current_user: User = Depends(get_current_user_optimized),
    db: Session = Depends(get_db)
):
    """
    Get 2FA status for current user (optimized with caching and circuit breaker)
    """
    cache_key = f"2fa_status_{current_user.id}"
    cached_status = cache_manager.get(cache_key)
    
    if cached_status:
        return cached_status
    
    try:
        # Check if user has 2FA enabled
        twofa_record = db.query(TwoFactorRecoveryCode).filter(
            TwoFactorRecoveryCode.user_id == current_user.id
        ).first()
        
        status_data = {
            "enabled": twofa_record is not None,
            "user_id": current_user.id,
            "email": current_user.email
        }
        
        cache_manager.set(cache_key, status_data, ttl=AUTH_CACHE_TTL)
        return status_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get 2FA status: {str(e)}"
        )

@router.post("/request-email-verify")
@auth_circuit_breaker
async def request_email_verification_optimized(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Request email verification (optimized with rate limiting and circuit breaker)
    """
    try:
        email = request.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
        
        # Check rate limit
        rate_limit_key = f"email_verify_{email}"
        if not cache_manager.get(rate_limit_key):
            # Set rate limit (1 request per 5 minutes)
            cache_manager.set(rate_limit_key, True, ttl=300)
        else:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Email verification request too frequent. Please wait 5 minutes."
            )
        
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )
        
        # Generate verification token
        import secrets
        verification_token = secrets.token_urlsafe(32)
        
        # Store verification token
        verification = EmailVerificationToken(
            user_id=user.id,
            token=verification_token,
            expires_at=datetime.utcnow() + timezone.utc.localize(datetime.timedelta(hours=24))
        )
        
        db.add(verification)
        db.commit()
        
        # In a real implementation, you would send the email here
        # For now, we'll just return success
        
        return {
            "message": "Verification email sent successfully",
            "email": email,
            "verification_token": verification_token  # Remove this in production
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to request email verification: {str(e)}"
        )

@router.post("/verify-email")
async def verify_email_optimized(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Verify email with token (optimized)
    """
    try:
        token = request.get("token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token is required"
            )
        
        # Find verification record
        verification = db.query(EmailVerificationToken).filter(
            EmailVerificationToken.token == token,
            EmailVerificationToken.expires_at > datetime.utcnow()
        ).first()
        
        if not verification:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
        # Update user email verification status
        user = db.query(User).filter(User.id == verification.user_id).first()
        if user:
            user.email_verified = True
            db.delete(verification)  # Remove used token
            db.commit()
            
            # Invalidate user cache
            from utils.auth_optimized import invalidate_user_cache
            invalidate_user_cache(user.id)
            cache_manager.delete(f"user_info_{user.id}")
            
            return {
                "message": "Email verified successfully",
                "user_id": user.id,
                "email": user.email
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify email: {str(e)}"
        )

@router.get("/session/status")
async def get_session_status_optimized(
    current_user: User = Depends(get_current_user_optimized)
):
    """
    Get current session status (optimized)
    """
    try:
        return {
            "authenticated": True,
            "user_id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role,
            "is_admin": current_user.is_admin,
            "email_verified": current_user.email_verified,
            "session_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session status: {str(e)}"
        )

@router.post("/logout")
async def logout_optimized(
    current_user: User = Depends(get_current_user_optimized)
):
    """
    Logout user (optimized with cache invalidation)
    """
    try:
        # Invalidate all user-related cache
        from utils.auth_optimized import invalidate_user_cache
        invalidate_user_cache(current_user.id)
        
        # Clear user-specific cache entries
        cache_keys_to_clear = [
            f"user_info_{current_user.id}",
            f"user_usage_{current_user.id}",
            f"user_usage_dist_{current_user.id}",
            f"user_automations_{current_user.id}",
            f"2fa_status_{current_user.id}"
        ]
        
        for key in cache_keys_to_clear:
            cache_manager.delete(key)
        
        return {
            "message": "Logged out successfully",
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to logout: {str(e)}"
        )

@router.get("/cache/stats")
async def get_auth_cache_stats():
    """Get authentication-related cache statistics"""
    stats = cache_manager.get_stats()
    
    # Count auth-specific cache entries
    auth_cache_keys = [
        key for key in cache_manager._cache.keys() 
        if key.startswith("user_data_") or key.startswith("2fa_status_") or key.startswith("csrf_token")
    ]
    
    return {
        "total_cache_entries": stats["total_entries"],
        "active_cache_entries": stats["active_entries"],
        "auth_cache_entries": len(auth_cache_keys),
        "cache_ttl": stats["default_ttl"],
        "current_time": stats["current_time"]
    }
