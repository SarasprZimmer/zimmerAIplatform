"""
Optimized Authentication System for Zimmer AI Platform
Implements caching and performance optimizations to fix timeout issues
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import time
from functools import lru_cache

from database import SessionLocal
from models.user import User
from utils.jwt import (
    verify_jwt_token, 
    get_current_user_id,
    decode_access_token,
    get_user_id_from_access_token,
    is_admin_from_access_token
)
from cache_manager import cache_manager

# Security scheme for Bearer token
security = HTTPBearer(auto_error=False)

# Cache TTL for user data (5 minutes)
USER_CACHE_TTL = 300

def get_db():
    """Database session dependency with connection pooling optimization"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@lru_cache(maxsize=1000)
def get_cached_user_by_id(user_id: int) -> Optional[dict]:
    """Get user data from cache with LRU caching"""
    cache_key = f"user_data_{user_id}"
    cached_user = cache_manager.get(cache_key)
    
    if cached_user:
        return cached_user
    
    # If not in cache, fetch from database
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user_data = {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            cache_manager.set(cache_key, user_data, ttl=USER_CACHE_TTL)
            return user_data
    finally:
        db.close()
    
    return None

def invalidate_user_cache(user_id: int):
    """Invalidate user cache when user data changes"""
    cache_key = f"user_data_{user_id}"
    cache_manager.delete(cache_key)
    # Also clear LRU cache
    get_cached_user_by_id.cache_clear()

async def get_current_user_optimized(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Optimized get current user with caching and performance improvements
    """
    try:
        # Require credentials - no development mode bypass
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Parse JWT token
        token = credentials.credentials
        
        # Verify JWT access token using optimized system
        try:
            user_id = get_user_id_from_access_token(token)
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired access token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Try to get user from cache first
            user_data = get_cached_user_by_id(user_id)
            if user_data:
                # Create User object from cached data
                user = User()
                user.id = user_data["id"]
                user.email = user_data["email"]
                user.name = user_data["name"]
                user.role = user_data["role"]
                user.is_active = user_data["is_active"]
                user.is_admin = user_data["is_admin"]
                user.created_at = user_data["created_at"]
                return user
            
            # Fallback to database if not in cache
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive"
                )
            
            # Cache the user data for future requests
            user_data = {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            cache_key = f"user_data_{user_id}"
            cache_manager.set(cache_key, user_data, ttl=USER_CACHE_TTL)
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )

async def require_admin_optimized(current_user: User = Depends(get_current_user_optimized)) -> User:
    """
    Optimized dependency to require admin privileges
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

async def get_current_admin_user_optimized(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Optimized get current admin user with caching
    """
    try:
        # Require credentials
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Parse JWT token
        token = credentials.credentials
        
        # Verify JWT access token
        try:
            user_id = get_user_id_from_access_token(token)
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired access token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Try to get user from cache first
            user_data = get_cached_user_by_id(user_id)
            if user_data:
                # Check if user is admin
                if not user_data.get("is_admin", False):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Admin privileges required"
                    )
                
                # Create User object from cached data
                user = User()
                user.id = user_data["id"]
                user.email = user_data["email"]
                user.name = user_data["name"]
                user.role = user_data["role"]
                user.is_active = user_data["is_active"]
                user.is_admin = user_data["is_admin"]
                user.created_at = user_data["created_at"]
                return user
            
            # Fallback to database if not in cache
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive"
                )
            
            if not user.is_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin privileges required"
                )
            
            # Cache the user data for future requests
            user_data = {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            cache_key = f"user_data_{user_id}"
            cache_manager.set(cache_key, user_data, ttl=USER_CACHE_TTL)
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )

# Rate limiting for authentication endpoints
from collections import defaultdict
import time

# Simple in-memory rate limiter
rate_limit_storage = defaultdict(list)

def check_rate_limit(identifier: str, max_requests: int = 10, window_seconds: int = 60) -> bool:
    """
    Check if request is within rate limit
    """
    current_time = time.time()
    window_start = current_time - window_seconds
    
    # Clean old requests
    rate_limit_storage[identifier] = [
        req_time for req_time in rate_limit_storage[identifier] 
        if req_time > window_start
    ]
    
    # Check if under limit
    if len(rate_limit_storage[identifier]) >= max_requests:
        return False
    
    # Add current request
    rate_limit_storage[identifier].append(current_time)
    return True

def rate_limit_dependency(identifier: str = None):
    """
    Dependency for rate limiting
    """
    def _rate_limit(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
        if identifier:
            if not check_rate_limit(identifier):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
        return credentials
    return _rate_limit
