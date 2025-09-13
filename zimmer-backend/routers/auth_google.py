"""
Google OAuth Authentication Router for Zimmer AI Platform
Implements backend-centric OAuth flow with in-memory access token handoff
"""

from fastapi import APIRouter, Depends, Request, Response, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session
from datetime import datetime
import secrets
import urllib.parse

from settings import settings
from database import get_db
from models.user import User
from utils.jwt import create_access_token
from utils.security import hash_password

router = APIRouter(prefix="/api/auth/google", tags=["auth-google"])

# Single OAuth client
oauth = OAuth()
if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
    oauth.register(
        name="google",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

def _frontend_redirect_url(token: str, error: str | None = None):
    """Redirect user back to panel with token in URL fragment so it won't hit server logs"""
    base = settings.FRONTEND_BASE_URL.rstrip("/")
    if error:
        return f"{base}/auth/google/done#error={urllib.parse.quote(error)}"
    return f"{base}/auth/google/done#access_token={urllib.parse.quote(token)}"

@router.get("/login")
async def google_login(request: Request):
    """Initiate Google OAuth login flow"""
    if "google" not in oauth._clients:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")
    
    # CSRF state
    request.session.setdefault("oauth_state", secrets.token_urlsafe(16))
    redirect_uri = settings.GOOGLE_REDIRECT_URL
    return await oauth.google.authorize_redirect(request, redirect_uri, state=request.session["oauth_state"])

@router.get("/callback")
async def google_callback(request: Request, response: Response, db: Session = Depends(get_db)):
    """Handle Google OAuth callback and create/login user"""
    if "google" not in oauth._clients:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")

    # Exchange code
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        return RedirectResponse(_frontend_redirect_url("", error="oauth_exchange_failed"))

    # Grab claims (email, email_verified, sub, name, picture)
    userinfo = token.get("userinfo") or {}
    if not userinfo:
        # Fallback: call userinfo endpoint
        try:
            resp = await oauth.google.get("userinfo", token=token)
            userinfo = resp.json()
        except Exception:
            return RedirectResponse(_frontend_redirect_url("", error="userinfo_failed"))

    email = userinfo.get("email")
    if not email:
        return RedirectResponse(_frontend_redirect_url("", error="email_missing"))

    # Find or create user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Create minimal user; you may map name/picture if model supports it
        user = User(
            email=email,
            name=userinfo.get("name") or email.split("@")[0],
            password_hash=hash_password(secrets.token_urlsafe(32)),  # Random password for OAuth users
            is_active=True,
            created_at=datetime.utcnow()
        )
        # mark verified if Google verified this email
        if userinfo.get("email_verified") is True:
            user.email_verified_at = datetime.utcnow()
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # If Google says verified and we haven't set it, set it
        if userinfo.get("email_verified") is True and user.email_verified_at is None:
            user.email_verified_at = datetime.utcnow()
            db.commit()

    # Issue tokens
    access_token = create_access_token(user.id, user.is_admin if hasattr(user, 'is_admin') else False)
    
    # Set refresh cookie (using existing pattern)
    from utils.jwt import create_refresh_token
    refresh_token = create_refresh_token()
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

    # Redirect with access token to User Panel
    return RedirectResponse(_frontend_redirect_url(access_token))

# Optional: simple health check
@router.get("/configured")
def google_configured():
    """Check if Google OAuth is properly configured"""
    return {
        "configured": bool(
            settings.GOOGLE_CLIENT_ID and 
            settings.GOOGLE_CLIENT_SECRET and 
            settings.GOOGLE_REDIRECT_URL
        )
    }
