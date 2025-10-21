"""
Token Management Admin Endpoints
Handles token adjustments, history, and user token overview
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from database import get_db
from models.user import User
from models.user_automation import UserAutomation
from models.token_usage import TokenUsage
from models.token_adjustment import TokenAdjustment
from utils.auth_dependency import get_current_admin_user

router = APIRouter(prefix="/api/admin", tags=["admin-token-management"])

# Pydantic models for request/response
class TokenAdjustmentRequest(BaseModel):
    user_id: int
    tokens: int
    reason: str

class TokenAdjustmentResponse(BaseModel):
    id: int
    user_id: int
    tokens: int
    reason: str
    admin_id: int
    created_at: datetime
    user_email: Optional[str] = None

class UserTokenOverview(BaseModel):
    user_id: int
    email: str
    name: str
    total_tokens: int
    automations_count: int
    last_activity: Optional[datetime] = None

@router.post("/tokens/adjust")
async def adjust_user_tokens(
    request: TokenAdjustmentRequest,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Adjust user token balance
    """
    try:
        # Validate user exists
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Validate token amount
        if request.tokens == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token adjustment cannot be zero"
            )
        
        # Create adjustment record
        adjustment = TokenAdjustment(
            user_id=request.user_id,
            tokens=request.tokens,
            reason=request.reason,
            admin_id=current_admin.id,
            created_at=datetime.utcnow()
        )
        db.add(adjustment)
        
        # Update user's total tokens in user_automations
        user_automations = db.query(UserAutomation).filter(
            UserAutomation.user_id == request.user_id
        ).all()
        
        for user_auto in user_automations:
            if request.tokens > 0:
                user_auto.tokens_remaining += request.tokens
            else:
                # Don't allow negative balance
                user_auto.tokens_remaining = max(0, user_auto.tokens_remaining + request.tokens)
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Successfully adjusted {request.tokens} tokens for user {user.email}",
            "adjustment": {
                "id": adjustment.id,
                "user_id": request.user_id,
                "tokens": request.tokens,
                "reason": request.reason,
                "admin_id": current_admin.id,
                "created_at": adjustment.created_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to adjust tokens: {str(e)}"
        )

@router.get("/tokens/history")
async def get_token_adjustment_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    user_id: Optional[int] = Query(None),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get token adjustment history with pagination
    """
    try:
        # Build query
        query = db.query(TokenAdjustment).join(User, TokenAdjustment.user_id == User.id)
        
        if user_id:
            query = query.filter(TokenAdjustment.user_id == user_id)
        
        # Get total count
        total_count = query.count()
        
        # Get paginated results
        adjustments = query.order_by(desc(TokenAdjustment.created_at)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        # Format response
        formatted_adjustments = []
        for adj in adjustments:
            user = db.query(User).filter(User.id == adj.user_id).first()
            formatted_adjustments.append({
                "id": adj.id,
                "user_id": adj.user_id,
                "user_email": user.email if user else "Unknown",
                "user_name": user.name if user else "Unknown",
                "tokens": adj.tokens,
                "reason": adj.reason,
                "admin_id": adj.admin_id,
                "created_at": adj.created_at.isoformat()
            })
        
        return {
            "status": "success",
            "data": {
                "adjustments": formatted_adjustments,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "total_pages": (total_count + page_size - 1) // page_size
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve token history: {str(e)}"
        )

@router.get("/user-tokens")
async def get_user_tokens_overview(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all user token balances with filtering
    """
    try:
        # Build query
        query = db.query(User).join(UserAutomation, User.id == UserAutomation.user_id)
        
        if search:
            query = query.filter(
                (User.email.ilike(f"%{search}%")) | 
                (User.name.ilike(f"%{search}%"))
            )
        
        # Get total count
        total_count = query.distinct().count()
        
        # Get paginated results
        users = query.distinct().offset((page - 1) * page_size).limit(page_size).all()
        
        # Format response with token aggregation
        formatted_users = []
        for user in users:
            # Get user's total tokens across all automations
            user_automations = db.query(UserAutomation).filter(
                UserAutomation.user_id == user.id
            ).all()
            
            total_tokens = sum(ua.tokens_remaining for ua in user_automations)
            automations_count = len(user_automations)
            
            # Get last activity
            last_usage = db.query(TokenUsage).filter(
                TokenUsage.user_id == user.id
            ).order_by(desc(TokenUsage.created_at)).first()
            
            formatted_users.append({
                "user_id": user.id,
                "email": user.email,
                "name": user.name,
                "total_tokens": total_tokens,
                "automations_count": automations_count,
                "last_activity": last_usage.created_at.isoformat() if last_usage else None,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat()
            })
        
        return {
            "status": "success",
            "data": {
                "users": formatted_users,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "total_pages": (total_count + page_size - 1) // page_size
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user tokens: {str(e)}"
        )

@router.get("/tokens/stats")
async def get_token_statistics(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get token usage statistics
    """
    try:
        # Get total tokens in system
        total_tokens = db.query(func.sum(UserAutomation.tokens_remaining)).scalar() or 0
        
        # Get total users with tokens
        users_with_tokens = db.query(UserAutomation.user_id).distinct().count()
        
        # Get total adjustments made
        total_adjustments = db.query(TokenAdjustment).count()
        
        # Get recent adjustments (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_adjustments = db.query(TokenAdjustment).filter(
            TokenAdjustment.created_at >= thirty_days_ago
        ).count()
        
        # Get top users by token balance
        top_users = db.query(
            User.id,
            User.email,
            User.name,
            func.sum(UserAutomation.tokens_remaining).label('total_tokens')
        ).join(UserAutomation, User.id == UserAutomation.user_id).group_by(
            User.id, User.email, User.name
        ).order_by(desc('total_tokens')).limit(10).all()
        
        return {
            "status": "success",
            "data": {
                "total_tokens": total_tokens,
                "users_with_tokens": users_with_tokens,
                "total_adjustments": total_adjustments,
                "recent_adjustments": recent_adjustments,
                "top_users": [
                    {
                        "user_id": user.id,
                        "email": user.email,
                        "name": user.name,
                        "total_tokens": user.total_tokens
                    }
                    for user in top_users
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve token statistics: {str(e)}"
        )
