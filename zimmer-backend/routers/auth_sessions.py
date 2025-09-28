"""
Authentication sessions router with access/refresh token support
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from database import get_db
from models.user import User, UserRole
from settings import settings
from models.session import Session as UserSession
from schemas.auth_session import (
    SignupRequest,
    LoginRequest, 
    LoginResponse, 
    RefreshResponse, 
    LogoutResponse
)
from utils.jwt import (
    create_access_token, 
    create_refresh_token, 
    hash_refresh_token,
    verify_refresh_token,
    ACCESS_TOKEN_TTL_MIN,
    REFRESH_TOKEN_TTL_DAYS,
    SESSION_IDLE_TIMEOUT_MIN
)
from utils.security import verify_password, hash_password
from utils.csrf import get_csrf_token, set_csrf_cookie

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Security scheme for Bearer token (for logout validation)
security = HTTPBearer(auto_error=False)


@router.get("/csrf")
async def get_csrf_token_endpoint(response: Response):
    """
    Get CSRF token for form submissions
    """
    token_data = get_csrf_token()
    set_csrf_cookie(response, token_data["cookie_value"])
    
    return {
        "csrf_token": token_data["csrf_token"],
        "message": "CSRF token generated successfully"
    }


def get_client_info(request: Request) -> tuple[str, str]:
    """Extract user agent and IP address from request"""
    user_agent = request.headers.get("user-agent", "")
    
    # Get IP address (considering proxies)
    ip_address = request.client.host
    if "x-forwarded-for" in request.headers:
        ip_address = request.headers["x-forwarded-for"].split(",")[0].strip()
    elif "x-real-ip" in request.headers:
        ip_address = request.headers["x-real-ip"]
    
    return user_agent, ip_address


def cleanup_expired_sessions(db: Session):
    """Clean up expired and revoked sessions"""
    try:
        now = datetime.utcnow()
        
        # Delete expired sessions
        expired_count = db.query(UserSession).filter(
            UserSession.expires_at < now
        ).delete()
        
        # Delete revoked sessions older than 24 hours
        revoked_threshold = now - timedelta(hours=24)
        revoked_count = db.query(UserSession).filter(
            and_(
                UserSession.revoked_at.isnot(None),
                UserSession.revoked_at < revoked_threshold
            )
        ).delete()
        
        if expired_count > 0 or revoked_count > 0:
            logger.info(f"Cleaned up {expired_count} expired and {revoked_count} revoked sessions")
            
        db.commit()
        
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {str(e)}")
        db.rollback()


@router.post("/signup", response_model=LoginResponse)
async def signup(
    request: SignupRequest,
    http_request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    User signup with automatic login
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="کاربری با این ایمیل قبلاً وجود دارد"
            )
        
        # Create new user
        new_user = User(
            name=request.name,
            email=request.email,
            password_hash=hash_password(request.password),
            is_active=True,
            role=UserRole.customer  # Default role for new users
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Get client information
        user_agent, ip_address = get_client_info(http_request)
        
        # Create access token
        access_token = create_access_token(
            user_id=new_user.id,
            is_admin=new_user.is_admin
        )
        
        # Create refresh token
        refresh_token = create_refresh_token()
        refresh_token_hash = hash_refresh_token(refresh_token)
        
        # Calculate expiration times
        now = datetime.utcnow()
        expires_at = now + timedelta(days=REFRESH_TOKEN_TTL_DAYS)
        
        # Create session record
        session = UserSession(
            user_id=new_user.id,
            refresh_token_hash=refresh_token_hash,
            user_agent=user_agent,
            ip_address=ip_address,
            last_used_at=now,
            expires_at=expires_at
        )
        
        db.add(session)
        db.commit()
        
        # Set secure HTTP-only cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=REFRESH_TOKEN_TTL_DAYS * 24 * 60 * 60,  # Convert days to seconds
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",  # Use 'strict' in production if no cross-site issues
            path="/api/auth"
        )
        
        # Log successful signup
        logger.info(
            f"New user {new_user.id} ({new_user.email}) signed up successfully from {ip_address}"
        )
        
        return LoginResponse(
            access_token=access_token,
            user={
                "id": new_user.id,
                "name": new_user.name,
                "email": new_user.email,
                "is_admin": new_user.is_admin
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="خطای داخلی در ثبت نام"
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    http_request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    User login with session creation
    """
    try:
        # Clean up expired sessions
        cleanup_expired_sessions(db)
        
        # Verify user credentials
        user = db.query(User).filter(
            and_(
                User.email == request.email,
                User.is_active == True
            )
        ).first()
        
        if not user or not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="ایمیل یا رمز عبور اشتباه است"
            )
        
        # Check email verification if required
        if settings.REQUIRE_VERIFIED_EMAIL_FOR_LOGIN and not user.email_verified_at:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="email_not_verified"
            )
        
        # Check if 2FA is enabled
        if getattr(user, "twofa_enabled", False):
            from routers.twofa import create_otp_challenge_token
            challenge = create_otp_challenge_token(user.id, user.password_hash)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail={"error":"otp_required","challenge_token":challenge}
            )
        
        # Get client information
        user_agent, ip_address = get_client_info(http_request)
        
        # Create access token
        access_token = create_access_token(
            user_id=user.id,
            is_admin=user.is_admin
        )
        
        # Create refresh token
        refresh_token = create_refresh_token()
        refresh_token_hash = hash_refresh_token(refresh_token)
        
        # Calculate expiration times
        now = datetime.utcnow()
        expires_at = now + timedelta(days=REFRESH_TOKEN_TTL_DAYS)
        
        # Create session record
        session = UserSession(
            user_id=user.id,
            refresh_token_hash=refresh_token_hash,
            user_agent=user_agent,
            ip_address=ip_address,
            last_used_at=now,
            expires_at=expires_at
        )
        
        db.add(session)
        db.commit()
        
        # Set secure HTTP-only cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=REFRESH_TOKEN_TTL_DAYS * 24 * 60 * 60,  # Convert days to seconds
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",  # Use 'strict' in production if no cross-site issues
            path="/api/auth"
        )
        
        # Log successful login
        logger.info(
            f"User {user.id} ({user.email}) logged in successfully from {ip_address}"
        )
        
        return LoginResponse(
            access_token=access_token,
            user={
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "is_admin": user.is_admin
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="خطای داخلی در ورود به سیستم"
        )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    http_request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token from cookie
    """
    try:
        # Clean up expired sessions
        cleanup_expired_sessions(db)
        
        # Get refresh token from cookie
        refresh_token = http_request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="توکن تازه‌سازی یافت نشد"
            )
        
        # Find active session by refresh token hash
        # We'll use a more efficient approach by limiting the search scope
        sessions = db.query(UserSession).filter(
            and_(
                UserSession.revoked_at.is_(None),
                UserSession.expires_at > datetime.utcnow()
            )
        ).limit(100).all()  # Limit to prevent excessive memory usage
        
        logger.debug(f"Searching through {len(sessions)} active sessions for refresh token")
        
        matching_session = None
        for session in sessions:
            if verify_refresh_token(refresh_token, session.refresh_token_hash):
                matching_session = session
                logger.debug(f"Found matching session for user {session.user_id}")
                break
        
        if not matching_session:
            logger.warning(f"Refresh token not found in {len(sessions)} active sessions")
            # Log some session details for debugging
            if sessions:
                logger.debug(f"Active sessions: {[(s.user_id, s.last_used_at) for s in sessions[:5]]}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="توکن تازه‌سازی نامعتبر است"
            )
        

        
        # Check idle timeout
        now = datetime.utcnow()
        idle_threshold = now - timedelta(minutes=SESSION_IDLE_TIMEOUT_MIN)
        if matching_session.last_used_at < idle_threshold:
            # Revoke session due to idle timeout
            matching_session.revoked_at = now
            db.commit()
            
            # Clear cookie
            response.delete_cookie(
                key="refresh_token",
                path="/api/auth"
            )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="جلسه به دلیل عدم فعالیت منقضی شده است"
            )
        
        # Get user information
        user = db.query(User).filter(User.id == matching_session.user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="کاربر یافت نشد یا غیرفعال است"
            )
        
        # Create new access token
        access_token = create_access_token(
            user_id=user.id,
            is_admin=user.is_admin
        )
        
        # Update session timestamp (don't rotate refresh token to avoid cookie issues)
        try:
            # Refresh the session object to ensure we have the latest data
            db.refresh(matching_session)
            
            # Double-check the session is still valid
            if matching_session.revoked_at is not None or matching_session.expires_at <= now:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="جلسه منقضی شده است"
                )
            
            # Update session timestamp only (keep same refresh token)
            matching_session.last_used_at = now
            db.commit()
            
        except Exception as e:
            db.rollback()
            logger.error(f"Session update failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="خطا در به‌روزرسانی جلسه"
            )
        
        # Log token refresh
        logger.info(
            f"Access token refreshed for user {user.id} ({user.email})"
        )
        
        return RefreshResponse(access_token=access_token)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="خطای داخلی در تازه‌سازی توکن"
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    http_request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Logout user and revoke session
    """
    try:
        # Get refresh token from cookie
        refresh_token = http_request.cookies.get("refresh_token")
        
        if refresh_token:
            # Find and revoke session
            try:
                sessions = db.query(UserSession).filter(
                    and_(
                        UserSession.revoked_at.is_(None),
                        UserSession.expires_at > datetime.utcnow()
                    )
                ).limit(100).all()
                
                for session in sessions:
                    if verify_refresh_token(refresh_token, session.refresh_token_hash):
                        session.revoked_at = datetime.utcnow()
                        logger.debug(f"Revoked session for user {session.user_id}")
                        break
                        
            except Exception as e:
                logger.error(f"Error during logout session lookup: {str(e)}")
                # Continue with logout even if session lookup fails
            
            db.commit()
        
        # Clear cookie
        response.delete_cookie(
            key="refresh_token",
            path="/api/auth"
        )
        
        logger.info("User logged out successfully")
        
        return LogoutResponse(
            ok=True,
            message="خروج موفقیت‌آمیز بود"
        )
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        # Even if there's an error, try to clear the cookie
        response.delete_cookie(
            key="refresh_token",
            path="/api/auth"
        )
        
        return LogoutResponse(
            ok=True,
            message="خروج انجام شد"
        )


@router.post("/logout-all", response_model=LogoutResponse)
async def logout_all_sessions(
    credentials: Optional[HTTPBearer] = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Logout from all sessions (requires valid access token)
    """
    try:
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="توکن دسترسی مورد نیاز است"
            )
        
        # Verify access token and get user ID
        from utils.jwt import get_user_id_from_access_token
        user_id = get_user_id_from_access_token(credentials.credentials)
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="توکن دسترسی نامعتبر است"
            )
        
        # Revoke all active sessions for this user
        now = datetime.utcnow()
        revoked_count = db.query(UserSession).filter(
            and_(
                UserSession.user_id == user_id,
                UserSession.revoked_at.is_(None)
            )
        ).update({
            UserSession.revoked_at: now
        })
        
        db.commit()
        
        logger.info(f"All {revoked_count} sessions revoked for user {user_id}")
        
        return LogoutResponse(
            ok=True,
            message=f"از تمام جلسه‌ها خارج شدید ({revoked_count} جلسه)"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout all sessions error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="خطای داخلی در خروج از تمام جلسه‌ها"
        )
