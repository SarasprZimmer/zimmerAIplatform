from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from datetime import datetime
from database import SessionLocal
from models.user import User, UserRole
from schemas.user import UserCreateRequest, UserUpdateRoleRequest, UserUpdateRequest, UserListResponse
from utils.auth_dependency import get_current_manager_user, get_db
from utils.security import hash_password
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/users/managers", response_model=List[UserListResponse])
async def list_users(
    search: Optional[str] = Query(None, description="Search by name or email"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(50, ge=1, le=100, description="Number of users to return"),
    offset: int = Query(0, ge=0, description="Number of users to skip"),
    db: Session = Depends(get_db),
    current_manager: User = Depends(get_current_manager_user)
):
    """
    List users with search and filtering (manager only)
    """
    query = db.query(User)
    
    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.name.ilike(search_term),
                User.email.ilike(search_term)
            )
        )
    
    # Apply role filter
    if role:
        query = query.filter(User.role == role)
    
    # Apply active status filter
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # Apply pagination
    users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()
    
    # Convert to response format with is_admin field
    user_responses = []
    for user in users:
        user_dict = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone_number": user.phone_number,
            "role": user.role,
            "is_active": user.is_active,
            "is_admin": user.is_admin,  # Include the computed property
            "created_at": user.created_at
        }
        user_responses.append(user_dict)
    
    logger.info(f"Returning {len(user_responses)} users with is_admin fields")
    return user_responses

@router.post("/users/managers", response_model=UserListResponse)
async def create_user(
    user_data: UserCreateRequest,
    db: Session = Depends(get_db),
    current_manager: User = Depends(get_current_manager_user)
):
    """
    Create a new user (manager only)
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Hash the password
    hashed_password = hash_password(user_data.password)
    
    # Create new user
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        phone_number=user_data.phone_number,
        password_hash=hashed_password,
        role=user_data.role,
        is_active=True,
        email_verified_at=datetime.utcnow()  # Auto-verify staff emails since they're created by managers
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"Manager {current_manager.email} created user {new_user.email} with role {new_user.role}")
    
    # Return user with is_admin field
    return {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "phone_number": new_user.phone_number,
        "role": new_user.role,
        "is_active": new_user.is_active,
        "is_admin": new_user.is_admin,
        "created_at": new_user.created_at
    }

@router.put("/users/managers/{user_id}/role", response_model=UserListResponse)
async def update_user_role(
    user_id: int = Path(...),
    role_data: UserUpdateRoleRequest = None,
    db: Session = Depends(get_db),
    current_manager: User = Depends(get_current_manager_user)
):
    """
    Update user role (manager only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent manager from changing their own role
    if user.id == current_manager.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )
    
    # Prevent manager from creating another manager (only existing managers can)
    if role_data.role == UserRole.manager and current_manager.role != UserRole.manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can create other managers"
        )
    
    user.role = role_data.role
    if role_data.is_active is not None:
        user.is_active = role_data.is_active
    
    db.commit()
    db.refresh(user)
    
    logger.info(f"Manager {current_manager.email} updated user {user.email} role to {user.role}")
    
    # Return user with is_admin field
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone_number": user.phone_number,
        "role": user.role,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "created_at": user.created_at
    }

@router.get("/users/managers/stats")
async def get_user_stats(
    db: Session = Depends(get_db),
    current_manager: User = Depends(get_current_manager_user)
):
    """
    Get user statistics (manager only)
    """
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    inactive_users = total_users - active_users
    
    # Count by role
    manager_count = db.query(User).filter(User.role == UserRole.manager).count()
    technical_team_count = db.query(User).filter(User.role == UserRole.technical_team).count()
    support_staff_count = db.query(User).filter(User.role == UserRole.support_staff).count()
    customer_count = db.query(User).filter(User.role == UserRole.customer).count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "by_role": {
            "managers": manager_count,
            "technical_team": technical_team_count,
            "support_staff": support_staff_count,
            "customers": customer_count
        }
    }

@router.get("/users/managers/{user_id}", response_model=UserListResponse)
async def get_user(
    user_id: int = Path(...),
    db: Session = Depends(get_db),
    current_manager: User = Depends(get_current_manager_user)
):
    """
    Get a specific user by ID (manager only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return user with is_admin field
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone_number": user.phone_number,
        "role": user.role,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "created_at": user.created_at
    }

@router.put("/users/managers/{user_id}", response_model=UserListResponse)
async def update_user(
    user_id: int = Path(...),
    user_data: UserUpdateRequest = None,
    db: Session = Depends(get_db),
    current_manager: User = Depends(get_current_manager_user)
):
    """
    Update user information (manager only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent manager from changing their own role or deactivating themselves
    if user.id == current_manager.id:
        if user_data.role is not None and user_data.role != user.role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change your own role"
            )
        if user_data.is_active is not None and not user_data.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate your own account"
            )
    
    # Check if email is being changed and if it already exists
    if user_data.email is not None and user_data.email != user.email:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
    
    # Prevent manager from creating another manager (only existing managers can)
    if user_data.role == UserRole.manager and current_manager.role != UserRole.manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can create other managers"
        )
    
    # Update user fields if provided
    if user_data.name is not None:
        user.name = user_data.name
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.phone_number is not None:
        user.phone_number = user_data.phone_number
    if user_data.role is not None:
        user.role = user_data.role
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    if user_data.is_admin is not None:
        # Update role based on is_admin status
        if user_data.is_admin:
            # If making admin, set to manager role
            user.role = UserRole.manager
        else:
            # If removing admin, set to support_staff role
            user.role = UserRole.support_staff
    if user_data.password is not None:
        user.password_hash = hash_password(user_data.password)
    
    db.commit()
    db.refresh(user)
    
    logger.info(f"Manager {current_manager.email} updated user {user.email}")
    
    # Return user with is_admin field
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone_number": user.phone_number,
        "role": user.role,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "created_at": user.created_at
    }

@router.delete("/users/managers/{user_id}")
async def deactivate_user(
    user_id: int = Path(...),
    db: Session = Depends(get_db),
    current_manager: User = Depends(get_current_manager_user)
):
    """
    Deactivate user (manager only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent manager from deactivating themselves
    if user.id == current_manager.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    # Prevent manager from deactivating other managers
    if user.role == UserRole.manager and current_manager.role != UserRole.manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot deactivate manager accounts"
        )
    
    user.is_active = False
    db.commit()
    
    logger.info(f"Manager {current_manager.email} deactivated user {user.email}")
    
    return {"message": "User deactivated successfully"}

@router.put("/users/managers/{user_id}/activate")
async def activate_user(
    user_id: int = Path(...),
    db: Session = Depends(get_db),
    current_manager: User = Depends(get_current_manager_user)
):
    """
    Activate user (manager only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = True
    db.commit()
    
    logger.info(f"Manager {current_manager.email} activated user {user.email}")
    
    return {"message": "User activated successfully"}

@router.post("/users/managers/bulk-deactivate")
async def bulk_deactivate_users(
    user_ids: List[int],
    db: Session = Depends(get_db),
    current_manager: User = Depends(get_current_manager_user)
):
    """
    Bulk deactivate users (manager only)
    """
    # Prevent deactivating self
    if current_manager.id in user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    # Get users to deactivate
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    
    # Prevent deactivating other managers
    manager_users = [u for u in users if u.role == UserRole.manager]
    if manager_users and current_manager.role != UserRole.manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot deactivate manager accounts"
        )
    
    # Deactivate users
    deactivated_count = 0
    for user in users:
        if user.is_active:
            user.is_active = False
            deactivated_count += 1
    
    db.commit()
    
    logger.info(f"Manager {current_manager.email} bulk deactivated {deactivated_count} users")
    
    return {
        "message": f"Successfully deactivated {deactivated_count} users",
        "deactivated_count": deactivated_count
    }
