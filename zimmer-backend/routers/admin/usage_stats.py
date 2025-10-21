"""
Usage Statistics Admin Endpoints
Handles system-wide and user-specific usage statistics
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from database import get_db
from models.user import User
from models.automation import Automation
from models.user_automation import UserAutomation
from models.token_usage import TokenUsage
from models.payment import Payment
from utils.auth_dependency import get_current_admin_user

router = APIRouter(prefix="/api/admin", tags=["admin-usage-stats"])

class UsageStatsResponse(BaseModel):
    period: str
    total_users: int
    active_users: int
    total_automations: int
    active_automations: int
    total_tokens_used: int
    total_payments: int
    total_revenue: float
    average_tokens_per_user: float
    top_automations: List[Dict[str, Any]]

@router.get("/usage/stats")
async def get_usage_statistics(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get system-wide usage statistics
    """
    try:
        # Calculate date range
        if period == "7d":
            days = 7
        elif period == "30d":
            days = 30
        elif period == "90d":
            days = 90
        elif period == "1y":
            days = 365
        else:
            days = 30
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get user statistics
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        new_users = db.query(User).filter(User.created_at >= start_date).count()
        
        # Get automation statistics
        total_automations = db.query(Automation).count()
        active_automations = db.query(Automation).filter(Automation.status == True).count()
        
        # Get token usage statistics
        total_tokens_used = db.query(func.sum(TokenUsage.tokens_used)).filter(
            TokenUsage.created_at >= start_date
        ).scalar() or 0
        
        # Get payment statistics
        total_payments = db.query(Payment).filter(
            Payment.created_at >= start_date
        ).count()
        
        successful_payments = db.query(Payment).filter(
            and_(
                Payment.created_at >= start_date,
                Payment.status == "completed"
            )
        ).count()
        
        total_revenue = db.query(func.sum(Payment.amount)).filter(
            and_(
                Payment.created_at >= start_date,
                Payment.status == "completed"
            )
        ).scalar() or 0
        
        # Get top automations by usage
        top_automations = db.query(
            Automation.id,
            Automation.name,
            func.sum(TokenUsage.tokens_used).label('total_tokens'),
            func.count(TokenUsage.id).label('usage_count')
        ).join(TokenUsage, Automation.id == TokenUsage.automation_id).filter(
            TokenUsage.created_at >= start_date
        ).group_by(Automation.id, Automation.name).order_by(
            desc('total_tokens')
        ).limit(10).all()
        
        # Calculate averages
        average_tokens_per_user = total_tokens_used / active_users if active_users > 0 else 0
        
        return {
            "status": "success",
            "data": {
                "period": period,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": datetime.utcnow().isoformat()
                },
                "users": {
                    "total": total_users,
                    "active": active_users,
                    "new_in_period": new_users
                },
                "automations": {
                    "total": total_automations,
                    "active": active_automations
                },
                "usage": {
                    "total_tokens_used": total_tokens_used,
                    "average_tokens_per_user": round(average_tokens_per_user, 2)
                },
                "payments": {
                    "total": total_payments,
                    "successful": successful_payments,
                    "success_rate": round((successful_payments / total_payments * 100) if total_payments > 0 else 0, 2),
                    "total_revenue": total_revenue
                },
                "top_automations": [
                    {
                        "id": auto.id,
                        "name": auto.name,
                        "total_tokens": auto.total_tokens,
                        "usage_count": auto.usage_count
                    }
                    for auto in top_automations
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve usage statistics: {str(e)}"
        )

@router.get("/usage/{user_id}")
async def get_user_usage_details(
    user_id: int,
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get specific user usage data
    """
    try:
        # Validate user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Calculate date range
        if period == "7d":
            days = 7
        elif period == "30d":
            days = 30
        elif period == "90d":
            days = 90
        elif period == "1y":
            days = 365
        else:
            days = 30
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get user's token usage
        token_usage = db.query(TokenUsage).filter(
            and_(
                TokenUsage.user_id == user_id,
                TokenUsage.created_at >= start_date
            )
        ).all()
        
        total_tokens_used = sum(usage.tokens_used for usage in token_usage)
        
        # Get user's automations
        user_automations = db.query(UserAutomation).filter(
            UserAutomation.user_id == user_id
        ).all()
        
        total_tokens_remaining = sum(ua.tokens_remaining for ua in user_automations)
        
        # Get user's payments
        user_payments = db.query(Payment).filter(
            and_(
                Payment.user_id == user_id,
                Payment.created_at >= start_date
            )
        ).all()
        
        total_paid = sum(payment.amount for payment in user_payments if payment.status == "completed")
        
        # Get usage by automation
        usage_by_automation = db.query(
            Automation.id,
            Automation.name,
            func.sum(TokenUsage.tokens_used).label('tokens_used'),
            func.count(TokenUsage.id).label('usage_count')
        ).join(TokenUsage, Automation.id == TokenUsage.automation_id).filter(
            and_(
                TokenUsage.user_id == user_id,
                TokenUsage.created_at >= start_date
            )
        ).group_by(Automation.id, Automation.name).all()
        
        # Get recent activity
        recent_usage = db.query(TokenUsage).filter(
            TokenUsage.user_id == user_id
        ).order_by(desc(TokenUsage.created_at)).limit(10).all()
        
        return {
            "status": "success",
            "data": {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat()
                },
                "period": period,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": datetime.utcnow().isoformat()
                },
                "tokens": {
                    "used_in_period": total_tokens_used,
                    "remaining": total_tokens_remaining,
                    "total_automations": len(user_automations)
                },
                "payments": {
                    "total_in_period": len(user_payments),
                    "successful": len([p for p in user_payments if p.status == "completed"]),
                    "total_amount": total_paid
                },
                "usage_by_automation": [
                    {
                        "automation_id": auto.id,
                        "automation_name": auto.name,
                        "tokens_used": auto.tokens_used,
                        "usage_count": auto.usage_count
                    }
                    for auto in usage_by_automation
                ],
                "recent_activity": [
                    {
                        "id": usage.id,
                        "automation_id": usage.automation_id,
                        "tokens_used": usage.tokens_used,
                        "created_at": usage.created_at.isoformat()
                    }
                    for usage in recent_usage
                ]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user usage details: {str(e)}"
        )

@router.get("/usage/automation/{automation_id}")
async def get_automation_usage_stats(
    automation_id: int,
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get usage statistics for a specific automation
    """
    try:
        # Validate automation exists
        automation = db.query(Automation).filter(Automation.id == automation_id).first()
        if not automation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation not found"
            )
        
        # Calculate date range
        if period == "7d":
            days = 7
        elif period == "30d":
            days = 30
        elif period == "90d":
            days = 90
        elif period == "1y":
            days = 365
        else:
            days = 30
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get usage statistics for this automation
        usage_stats = db.query(
            func.sum(TokenUsage.tokens_used).label('total_tokens'),
            func.count(TokenUsage.id).label('total_usage'),
            func.count(func.distinct(TokenUsage.user_id)).label('unique_users')
        ).filter(
            and_(
                TokenUsage.automation_id == automation_id,
                TokenUsage.created_at >= start_date
            )
        ).first()
        
        # Get top users for this automation
        top_users = db.query(
            User.id,
            User.email,
            User.name,
            func.sum(TokenUsage.tokens_used).label('tokens_used')
        ).join(TokenUsage, User.id == TokenUsage.user_id).filter(
            and_(
                TokenUsage.automation_id == automation_id,
                TokenUsage.created_at >= start_date
            )
        ).group_by(User.id, User.email, User.name).order_by(
            desc('tokens_used')
        ).limit(10).all()
        
        return {
            "status": "success",
            "data": {
                "automation": {
                    "id": automation.id,
                    "name": automation.name,
                    "status": automation.status,
                    "created_at": automation.created_at.isoformat()
                },
                "period": period,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": datetime.utcnow().isoformat()
                },
                "usage": {
                    "total_tokens": usage_stats.total_tokens or 0,
                    "total_usage_count": usage_stats.total_usage or 0,
                    "unique_users": usage_stats.unique_users or 0,
                    "average_tokens_per_use": round(
                        (usage_stats.total_tokens / usage_stats.total_usage) 
                        if usage_stats.total_usage and usage_stats.total_usage > 0 else 0, 2
                    )
                },
                "top_users": [
                    {
                        "user_id": user.id,
                        "email": user.email,
                        "name": user.name,
                        "tokens_used": user.tokens_used
                    }
                    for user in top_users
                ]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve automation usage stats: {str(e)}"
        )
