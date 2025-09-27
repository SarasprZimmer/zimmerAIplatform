from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from database import SessionLocal
from models.user import User, UserRole
from utils.jwt import get_user_id_from_access_token

# Security scheme for JWT tokens
security = HTTPBearer(auto_error=False)

def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: JWT token from Authorization header
        db: Database session
        
    Returns:
        User object if authentication successful
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        # Check if credentials are provided
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract user ID from token using new session-based validation
        user_id = get_user_id_from_access_token(credentials.credentials)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired access token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_manager_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current authenticated manager user
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object if user is manager
        
    Raises:
        HTTPException: If user is not manager
    """
    if current_user.role != UserRole.manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )
    
    return current_user

def get_current_technical_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current authenticated technical team user
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object if user is technical team or manager
        
    Raises:
        HTTPException: If user is not technical team or manager
    """
    if current_user.role not in [UserRole.manager, UserRole.technical_team, UserRole.support_staff]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Technical team access required"
        )
    
    return current_user

def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current authenticated admin user (manager or technical team)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object if user is manager or technical team
        
    Raises:
        HTTPException: If user is not manager or technical team
    """
    if current_user.role not in [UserRole.manager, UserRole.technical_team, UserRole.support_staff]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user 