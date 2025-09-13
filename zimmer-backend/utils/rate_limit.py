import os
import time
from typing import Dict, Tuple, Optional
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.rate_limits = {}  # In production, use Redis
        # Get environment to adjust limits
        is_development = os.getenv("ENVIRONMENT", "development") == "development"
        
        if is_development:
            # More relaxed limits for development
            self.limits = {
                "POST /api/auth/login": {"max_requests": 50, "window": 60},  # 50/min per IP
                "POST /api/auth/refresh": {"max_requests": 300, "window": 3600},  # 300/hour per IP
                "POST /api/payments/zarinpal/init": {"max_requests": 50, "window": 60},  # 50/min per user
            }
        else:
            # Production limits
            self.limits = {
                "POST /api/auth/login": {"max_requests": 5, "window": 60},  # 5/min per IP
                "POST /api/auth/refresh": {"max_requests": 60, "window": 3600},  # 60/hour per IP
                "POST /api/payments/zarinpal/init": {"max_requests": 10, "window": 60},  # 10/min per user
            }

    async def dispatch(self, request: Request, call_next):
        # Get client identifier
        client_id = self.get_client_id(request)
        
        # Check rate limit
        if not self.check_rate_limit(request, client_id):
            raise HTTPException(
                status_code=429,
                detail="تعداد درخواست‌های شما بیش از حد مجاز است. لطفاً کمی صبر کنید."
            )

        return await call_next(request)

    def get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # For user-specific limits, use user ID if available
        if "POST /api/payments/zarinpal/init" in str(request.url):
            # Try to get user ID from request
            try:
                # This would need to be implemented based on your auth system
                user_id = self.get_user_id_from_request(request)
                return f"user:{user_id}"
            except:
                pass
        
        # Default to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        return request.client.host if request.client else "unknown"

    def get_user_id_from_request(self, request: Request) -> Optional[int]:
        """Extract user ID from request (implement based on your auth system)"""
        # This is a placeholder - implement based on your authentication
        # You might get this from JWT token, session, etc.
        return None

    def check_rate_limit(self, request: Request, client_id: str) -> bool:
        """Check if request is within rate limit"""
        method = request.method
        path = request.url.path
        endpoint = f"{method} {path}"
        
        # Check if endpoint has rate limiting
        if endpoint not in self.limits:
            return True
        
        limit_config = self.limits[endpoint]
        max_requests = limit_config["max_requests"]
        window = limit_config["window"]
        
        # Get current timestamp
        now = time.time()
        
        # Initialize client tracking if not exists
        if client_id not in self.rate_limits:
            self.rate_limits[client_id] = {}
        
        if endpoint not in self.rate_limits[client_id]:
            self.rate_limits[client_id][endpoint] = []
        
        # Clean old requests outside the window
        requests = self.rate_limits[client_id][endpoint]
        requests = [req_time for req_time in requests if now - req_time < window]
        self.rate_limits[client_id][endpoint] = requests
        
        # Check if limit exceeded
        if len(requests) >= max_requests:
            return False
        
        # Add current request
        requests.append(now)
        self.rate_limits[client_id][endpoint] = requests
        
        return True

    def cleanup_old_entries(self):
        """Clean up old rate limit entries (call periodically)"""
        now = time.time()
        for client_id in list(self.rate_limits.keys()):
            for endpoint in list(self.rate_limits[client_id].keys()):
                window = self.limits.get(endpoint, {}).get("window", 3600)
                requests = self.rate_limits[client_id][endpoint]
                requests = [req_time for req_time in requests if now - req_time < window]
                
                if not requests:
                    del self.rate_limits[client_id][endpoint]
            
            if not self.rate_limits[client_id]:
                del self.rate_limits[client_id]

# Rate limit decorator for specific endpoints
def rate_limit(max_requests: int, window: int, key_func=None):
    """
    Decorator for rate limiting specific endpoints
    
    Args:
        max_requests: Maximum requests allowed
        window: Time window in seconds
        key_func: Function to extract client identifier
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This would need to be implemented based on your specific needs
            # For now, we'll rely on the middleware
            return await func(*args, **kwargs)
        return wrapper
    return decorator
