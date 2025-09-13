import jwt
import os
import secrets
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY or JWT_SECRET_KEY == "your-secret-key-change-in-production":
    raise ValueError(
        "JWT_SECRET_KEY environment variable must be set to a strong secret key. "
        "Generate a secure random key and set it in your .env file."
    )

# Session Configuration
ACCESS_TOKEN_TTL_MIN = int(os.getenv("ACCESS_TOKEN_TTL_MIN", "15"))
REFRESH_TOKEN_TTL_DAYS = int(os.getenv("REFRESH_TOKEN_TTL_DAYS", "7"))
SESSION_IDLE_TIMEOUT_MIN = int(os.getenv("SESSION_IDLE_TIMEOUT_MIN", "120"))
JWT_ALGORITHM = os.getenv("JWT_ALG", "HS256")

# Legacy support
JWT_EXPIRY_DAYS = 7

def create_jwt_token(user_id: int, user_name: str = None, user_email: str = None, user_role: str = None) -> str:
    """
    Create a JWT token for a user with nested user object
    
    Args:
        user_id: User ID to include in token
        user_name: User name to include in token
        user_email: User email to include in token
        user_role: User role to include in token
        
    Returns:
        JWT token string
    """
    # Create payload with nested user object
    payload = {
        "user": {
            "id": user_id,
            "name": user_name,
            "email": user_email,
            "role": user_role
        },
        "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRY_DAYS),
        "iat": datetime.utcnow()
    }
    
    # Create token
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload if valid, None if invalid
    """
    try:
        # Decode token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Token is invalid
        return None

def get_current_user_id(token: str) -> int:
    """
    Get user ID from JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        User ID from token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    payload = verify_jwt_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user_id from nested user object
    user = payload.get("user")
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = user.get("id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


# New session-based token functions
def create_access_token(user_id: int, is_admin: bool, ttl_minutes: Optional[int] = None) -> str:
    """
    Create a short-lived access token
    
    Args:
        user_id: User ID to include in token
        is_admin: Whether user has admin privileges
        ttl_minutes: Token TTL in minutes (defaults to ACCESS_TOKEN_TTL_MIN)
        
    Returns:
        JWT access token string
    """
    if ttl_minutes is None:
        ttl_minutes = ACCESS_TOKEN_TTL_MIN
    
    payload = {
        "sub": str(user_id),  # Standard JWT subject claim
        "type": "access",
        "is_admin": is_admin,
        "exp": datetime.utcnow() + timedelta(minutes=ttl_minutes),
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def create_refresh_token() -> str:
    """
    Create a cryptographically secure refresh token
    
    Returns:
        Random 256-bit base64-encoded refresh token
    """
    # Generate 32 bytes (256 bits) of random data
    random_bytes = secrets.token_bytes(32)
    # Encode as base64 for safe storage in cookies
    return secrets.token_urlsafe(32)


def hash_refresh_token(plain_token: str) -> str:
    """
    Hash a refresh token using bcrypt for secure storage
    
    Args:
        plain_token: Plain refresh token
        
    Returns:
        Bcrypt hash of the token
    """
    # Convert string to bytes for bcrypt
    token_bytes = plain_token.encode('utf-8')
    # Hash with bcrypt (cost factor 12)
    hashed = bcrypt.hashpw(token_bytes, bcrypt.gensalt(12))
    return hashed.decode('utf-8')


def verify_refresh_token(plain_token: str, hashed_token: str) -> bool:
    """
    Verify a refresh token against its hash (constant-time comparison)
    
    Args:
        plain_token: Plain refresh token
        hashed_token: Bcrypt hash of the token
        
    Returns:
        True if token matches hash, False otherwise
    """
    try:
        # Convert strings to bytes for bcrypt
        plain_bytes = plain_token.encode('utf-8')
        hashed_bytes = hashed_token.encode('utf-8')
        # Use bcrypt's constant-time comparison
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception:
        # If any error occurs during verification, return False
        return False





def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate an access token
    
    Args:
        token: JWT access token string
        
    Returns:
        Decoded payload if valid, None if invalid/expired
    """
    try:
        # Decode token with all validations
        payload = jwt.decode(
            token, 
            JWT_SECRET_KEY, 
            algorithms=[JWT_ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "require": ["exp", "iat", "sub", "type"]
            }
        )
        
        # Additional validation
        if payload.get("type") != "access":
            return None
            
        return payload
        
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Token is invalid
        return None
    except Exception:
        # Any other error
        return None


def get_user_id_from_access_token(token: str) -> Optional[int]:
    """
    Extract user ID from access token
    
    Args:
        token: JWT access token string
        
    Returns:
        User ID if token is valid, None otherwise
    """
    # Try new format first (with sub field)
    payload = decode_access_token(token)
    if payload is not None:
        try:
            user_id = int(payload.get("sub", ""))
            return user_id if user_id > 0 else None
        except (ValueError, TypeError):
            pass
    
    # Try legacy format (with nested user object)
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user = payload.get("user")
        if user and "id" in user:
            user_id = int(user["id"])
            return user_id if user_id > 0 else None
    except (jwt.InvalidTokenError, ValueError, TypeError):
        pass
    
    return None


def is_admin_from_access_token(token: str) -> bool:
    """
    Check if user has admin privileges from access token
    
    Args:
        token: JWT access token string
        
    Returns:
        True if user is admin, False otherwise
    """
    # Try new format first (with sub field)
    payload = decode_access_token(token)
    if payload is not None:
        return payload.get("is_admin", False)
    
    # Try legacy format (with nested user object)
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user = payload.get("user")
        if user and "role" in user:
            role = user["role"]
            # Admin roles are manager and technical_team
            return role in ["manager", "technical_team"]
    except (jwt.InvalidTokenError, ValueError, TypeError):
        pass
    
    return False 