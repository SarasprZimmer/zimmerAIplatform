import secrets
import hashlib
from typing import Optional
from fastapi import Request, HTTPException, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.csrf_tokens = {}  # In production, use Redis or database

    async def dispatch(self, request: Request, call_next):
        # Skip CSRF check for safe methods
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return await call_next(request)

        # Skip CSRF check for authentication endpoints
        if request.url.path.startswith("/api/auth/login") or \
           request.url.path.startswith("/api/auth/signup") or \
           request.url.path.startswith("/api/auth/refresh") or \
           request.url.path.startswith("/api/auth/logout") or \
           request.url.path.startswith("/api/auth/csrf") or \
           request.url.path.startswith("/api/auth/request-email-verify") or \
           request.url.path.startswith("/api/auth/verify-email"):
            return await call_next(request)

        # Skip CSRF check if no cookies (API-only requests)
        if not request.cookies:
            return await call_next(request)

        # Skip CSRF check if Authorization header is present (token-based auth)
        if "Authorization" in request.headers:
            return await call_next(request)

        # For unsafe methods with cookies, require CSRF token
        csrf_token = request.headers.get("X-CSRF-Token")
        csrf_cookie = request.cookies.get("XSRF-TOKEN")

        if not csrf_token or not csrf_cookie:
            raise HTTPException(
                status_code=403,
                detail="CSRF token required for this request"
            )

        if not verify_csrf_token(csrf_token, csrf_cookie):
            raise HTTPException(
                status_code=403,
                detail="Invalid CSRF token"
            )

        return await call_next(request)

    def generate_csrf_token(self) -> str:
        """Generate a new CSRF token"""
        return secrets.token_urlsafe(32)

def verify_csrf_token(token: str, cookie: str) -> bool:
    """Verify CSRF token using double-submit pattern"""
    try:
        # The token should match the cookie value directly
        return secrets.compare_digest(token, cookie)
    except Exception:
        return False

def get_csrf_token() -> dict:
    """Generate CSRF token for frontend"""
    token = secrets.token_urlsafe(32)
    return {
        "csrf_token": token,  # Return the token directly, not hashed
        "cookie_value": token
    }

def set_csrf_cookie(response: Response, token: str):
    """Set CSRF cookie in response"""
    response.set_cookie(
        key="XSRF-TOKEN",
        value=token,
        httponly=False,  # Frontend needs access
        secure=False,     # Set to True in production with HTTPS
        samesite="lax",   # Use 'strict' in production if no cross-site issues
        max_age=3600      # 1 hour
    )
