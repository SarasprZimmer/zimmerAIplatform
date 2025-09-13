"""
Main Authentication Router for Zimmer AI Platform
Provides standard auth endpoints that the frontend expects
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone, timedelta
import secrets
import hashlib

from database import get_db
from models.user import User
from models.twofa import TwoFactorRecoveryCode
from models.email_verification import EmailVerificationToken
from utils.auth_optimized import get_current_user_optimized, rate_limit_dependency
from utils.circuit_breaker import auth_circuit_breaker, login_circuit_breaker
from utils.jwt import create_access_token, create_jwt_token
from utils.security import hash_password, verify_password
from cache_manager import cache_manager
from schemas.user import UserSignupRequest, UserSignupResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Password functions are now imported from utils.security (bcrypt)

@router.post("/login")
async def login(request: dict, db: Session = Depends(get_db)):
    """
    User login endpoint with proper JWT authentication
    """
    try:
        email = request.get("email")
        password = request.get("password")
        
        if not email or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
        
        # Find user in database
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check email verification requirement
        from settings import settings
        if settings.REQUIRE_VERIFIED_EMAIL_FOR_LOGIN and not user.email_verified_at:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not verified. Please verify your email before logging in.",
                headers={"X-Error-Code": "email_not_verified"}
            )
        
        # Check if 2FA is required
        if hasattr(user, 'twofa_enabled') and user.twofa_enabled:
            # Generate challenge token
            challenge_token = secrets.token_urlsafe(32)
            cache_manager.set(f"challenge_{challenge_token}", user.id, ttl=300)  # 5 minutes
            
            return {
                "message": "2FA required",
                "challenge_token": challenge_token,
                "otp_required": True
            }
        
        # Create proper JWT access token
        access_token = create_access_token(user.id, user.is_admin if hasattr(user, 'is_admin') else False)
        
        # Store token in cache for validation
        cache_manager.set(f"token_{access_token}", user.id, ttl=3600)  # 1 hour
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "is_admin": user.is_admin if hasattr(user, 'is_admin') else False,
                "email_verified": user.email_verified if hasattr(user, 'email_verified') else True
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/register", response_model=UserSignupResponse)
async def register(user_data: UserSignupRequest, db: Session = Depends(get_db)):
    """
    User registration endpoint
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Hash the password
        password_hash = hash_password(user_data.password)
        
        # Create new user
        new_user = User(
            name=user_data.name,
            email=user_data.email,
            phone_number=user_data.phone_number,
            password_hash=password_hash,
            role="customer",  # Default role for regular users
            is_active=True,
            email_verified_at=None,  # Will be verified later
            twofa_enabled=False
        )
        
        # Add to database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create JWT access token
        access_token = create_access_token(new_user.id, new_user.is_admin)
        
        # Store token in cache for validation
        cache_manager.set(f"token_{access_token}", new_user.id, ttl=3600)  # 1 hour
        
        return UserSignupResponse(
            message="User registered successfully",
            user_id=new_user.id,
            email=new_user.email,
            access_token=access_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/refresh")
async def refresh_token():
    """
    Refresh access token endpoint
    """
    try:
        # In a real implementation, you would validate the refresh token from cookies
        # For now, we'll return a new token for testing
        
        # Create a new access token (in production, validate refresh token first)
        access_token = create_access_token(1, False)  # Mock user ID and admin status
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}"
        )

@router.post("/logout")
@auth_circuit_breaker
async def logout(
    current_user: User = Depends(get_current_user_optimized)
):
    """
    User logout endpoint
    """
    try:
        # Invalidate user cache
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
            detail=f"Logout failed: {str(e)}"
        )

@router.get("/csrf")
@auth_circuit_breaker
async def get_csrf_token():
    """
    Get CSRF token
    """
    try:
        cache_key = "csrf_token"
        cached_token = cache_manager.get(cache_key)
        
        if cached_token:
            return {"csrf_token": cached_token}
        
        # Generate new CSRF token
        csrf_token = secrets.token_urlsafe(32)
        cache_manager.set(cache_key, csrf_token, ttl=1800)  # 30 minutes
        
        return {"csrf_token": csrf_token}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate CSRF token: {str(e)}"
        )

@router.get("/2fa/status")
@auth_circuit_breaker
async def get_2fa_status(
    current_user: User = Depends(get_current_user_optimized),
    db: Session = Depends(get_db)
):
    """
    Get 2FA status for current user
    """
    try:
        cache_key = f"2fa_status_{current_user.id}"
        cached_status = cache_manager.get(cache_key)
        
        if cached_status:
            return cached_status
        
        # Check 2FA status
        twofa_enabled = current_user.twofa_enabled if hasattr(current_user, 'twofa_enabled') else False
        
        status_data = {
            "enabled": twofa_enabled,
            "user_id": current_user.id
        }
        
        cache_manager.set(cache_key, status_data, ttl=300)  # 5 minutes
        return status_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get 2FA status: {str(e)}"
        )

@router.post("/2fa/verify")
@auth_circuit_breaker
async def verify_2fa(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Verify 2FA OTP code
    """
    try:
        challenge_token = request.get("challenge_token")
        otp_code = request.get("otp_code")
        
        if not challenge_token or not otp_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Challenge token and OTP code are required"
            )
        
        # Get user from challenge token
        user_id = cache_manager.get(f"challenge_{challenge_token}")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired challenge token"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # In a real implementation, you would verify the OTP code
        # For now, we'll accept any 6-digit code
        
        # Create access token
        access_token = create_access_token(user.id)
        cache_manager.set(f"token_{access_token}", user.id, ttl=3600)  # 1 hour
        
        # Clear challenge token
        cache_manager.delete(f"challenge_{challenge_token}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "is_admin": user.is_admin,
                "email_verified": user.email_verified
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"2FA verification failed: {str(e)}"
        )

@router.get("/me")
async def get_current_user():
    """
    Get current user information
    """
    try:
        # For now, return mock user data
        # In production, you would validate the token and get real user data
        return {
            "id": 1,
            "email": "test@example.com",
            "name": "Test User",
            "role": "user",
            "is_admin": False,
            "email_verified": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user info: {str(e)}"
        )

@router.post("/send-email-verification")
async def send_email_verification(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Send email verification code
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
        if cache_manager.get(rate_limit_key):
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
        
        if user.email_verified_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )
        
        # Generate 6-digit verification code
        verification_code = f"{secrets.randbelow(900000) + 100000:06d}"
        
        # Store verification code in cache (5 minutes TTL)
        cache_manager.set(f"email_verify_code_{email}", verification_code, ttl=300)
        cache_manager.set(rate_limit_key, True, ttl=300)  # Rate limit
        
        # TODO: Send actual email with verification code
        # For now, we'll just return success
        print(f"Email verification code for {email}: {verification_code}")
        
        return {
            "message": "Verification code sent to email",
            "email": email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email verification: {str(e)}"
        )

@router.post("/verify-email")
async def verify_email(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Verify email with code
    """
    try:
        email = request.get("email")
        verification_code = request.get("verification_code")
        
        if not email or not verification_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and verification code are required"
            )
        
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.email_verified_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )
        
        # Verify code
        stored_code = cache_manager.get(f"email_verify_code_{email}")
        if not stored_code or stored_code != verification_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification code"
            )
        
        # Mark email as verified
        user.email_verified_at = datetime.utcnow()
        db.commit()
        
        # Clear verification code
        cache_manager.delete(f"email_verify_code_{email}")
        
        return {
            "message": "Email verified successfully",
            "email": email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify email: {str(e)}"
        )

@router.post("/send-password-reset-code")
async def send_password_reset_code(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Send password reset code to verified email
    """
    try:
        email = request.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
        
        # Check if user exists and email is verified
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not user.email_verified_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email must be verified before password reset"
            )
        
        # Check rate limit
        rate_limit_key = f"password_reset_{email}"
        if cache_manager.get(rate_limit_key):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Password reset request too frequent. Please wait 5 minutes."
            )
        
        # Generate 6-digit reset code
        reset_code = f"{secrets.randbelow(900000) + 100000:06d}"
        
        # Store reset code in cache (10 minutes TTL)
        cache_manager.set(f"password_reset_code_{email}", reset_code, ttl=600)
        cache_manager.set(rate_limit_key, True, ttl=300)  # Rate limit
        
        # TODO: Send actual email with reset code
        # For now, we'll just return success
        print(f"Password reset code for {email}: {reset_code}")
        
        return {
            "message": "Password reset code sent to email",
            "email": email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send password reset code: {str(e)}"
        )
