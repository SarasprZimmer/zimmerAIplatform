"""
System Monitoring Admin Endpoints
Handles system health status and dashboard statistics
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Dict, Any, List
from datetime import datetime, timedelta
import psutil
import os

from database import get_db
from models.user import User
from models.automation import Automation
from models.user_automation import UserAutomation
from models.token_usage import TokenUsage
from models.payment import Payment
from utils.auth_dependency import get_current_admin_user

router = APIRouter(prefix="/api/admin", tags=["admin-system-monitoring"])

@router.get("/system/status")
async def get_system_status(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get system health status
    """
    try:
        # Check database connectivity
        db_status = "healthy"
        db_response_time = 0
        try:
            start_time = datetime.utcnow()
            db.execute(text("SELECT 1"))
            db_response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get application metrics
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        total_automations = db.query(Automation).count()
        active_automations = db.query(Automation).filter(Automation.status == True).count()
        
        # Get recent activity (last hour)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_usage = db.query(TokenUsage).filter(
            TokenUsage.created_at >= one_hour_ago
        ).count()
        
        recent_payments = db.query(Payment).filter(
            Payment.created_at >= one_hour_ago
        ).count()
        
        # Determine overall system health
        overall_status = "healthy"
        if cpu_percent > 80 or memory.percent > 80 or disk.percent > 90:
            overall_status = "warning"
        if db_status != "healthy" or cpu_percent > 95 or memory.percent > 95:
            overall_status = "critical"
        
        return {
            "status": "success",
            "data": {
                "overall_status": overall_status,
                "timestamp": datetime.utcnow().isoformat(),
                "database": {
                    "status": db_status,
                    "response_time_ms": round(db_response_time, 2)
                },
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": round(memory.available / (1024**3), 2),
                    "disk_percent": disk.percent,
                    "disk_free_gb": round(disk.free / (1024**3), 2)
                },
                "application": {
                    "total_users": total_users,
                    "active_users": active_users,
                    "total_automations": total_automations,
                    "active_automations": active_automations,
                    "recent_usage_count": recent_usage,
                    "recent_payments_count": recent_payments
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system status: {str(e)}"
        )

@router.get("/dashboard/stats")
async def get_dashboard_statistics(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get admin dashboard statistics
    """
    try:
        # Get current date and time ranges
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        week_start = today_start - timedelta(days=7)
        month_start = today_start - timedelta(days=30)
        
        # User statistics
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        new_users_today = db.query(User).filter(User.created_at >= today_start).count()
        new_users_week = db.query(User).filter(User.created_at >= week_start).count()
        new_users_month = db.query(User).filter(User.created_at >= month_start).count()
        
        # Automation statistics
        total_automations = db.query(Automation).count()
        active_automations = db.query(Automation).filter(Automation.status == True).count()
        listed_automations = db.query(Automation).filter(Automation.is_listed == True).count()
        
        # Token usage statistics
        total_tokens_used_today = db.query(func.sum(TokenUsage.tokens_used)).filter(
            TokenUsage.created_at >= today_start
        ).scalar() or 0
        
        total_tokens_used_week = db.query(func.sum(TokenUsage.tokens_used)).filter(
            TokenUsage.created_at >= week_start
        ).scalar() or 0
        
        total_tokens_used_month = db.query(func.sum(TokenUsage.tokens_used)).filter(
            TokenUsage.created_at >= month_start
        ).scalar() or 0
        
        # Payment statistics
        total_payments_today = db.query(Payment).filter(
            Payment.created_at >= today_start
        ).count()
        
        total_payments_week = db.query(Payment).filter(
            Payment.created_at >= week_start
        ).count()
        
        total_payments_month = db.query(Payment).filter(
            Payment.created_at >= month_start
        ).count()
        
        successful_payments_today = db.query(Payment).filter(
            Payment.created_at >= today_start,
            Payment.status == "completed"
        ).count()
        
        successful_payments_week = db.query(Payment).filter(
            Payment.created_at >= week_start,
            Payment.status == "completed"
        ).count()
        
        successful_payments_month = db.query(Payment).filter(
            Payment.created_at >= month_start,
            Payment.status == "completed"
        ).count()
        
        # Revenue statistics
        revenue_today = db.query(func.sum(Payment.amount)).filter(
            Payment.created_at >= today_start,
            Payment.status == "completed"
        ).scalar() or 0
        
        revenue_week = db.query(func.sum(Payment.amount)).filter(
            Payment.created_at >= week_start,
            Payment.status == "completed"
        ).scalar() or 0
        
        revenue_month = db.query(func.sum(Payment.amount)).filter(
            Payment.created_at >= month_start,
            Payment.status == "completed"
        ).scalar() or 0
        
        # Top performing automations (by usage)
        top_automations = db.query(
            Automation.id,
            Automation.name,
            func.sum(TokenUsage.tokens_used).label('total_tokens')
        ).join(TokenUsage, Automation.id == TokenUsage.automation_id).filter(
            TokenUsage.created_at >= week_start
        ).group_by(Automation.id, Automation.name).order_by(
            func.sum(TokenUsage.tokens_used).desc()
        ).limit(5).all()
        
        # Recent activity
        recent_users = db.query(User).order_by(User.created_at.desc()).limit(5).all()
        recent_payments = db.query(Payment).order_by(Payment.created_at.desc()).limit(5).all()
        
        return {
            "status": "success",
            "data": {
                "timestamp": now.isoformat(),
                "users": {
                    "total": total_users,
                    "active": active_users,
                    "new_today": new_users_today,
                    "new_week": new_users_week,
                    "new_month": new_users_month
                },
                "automations": {
                    "total": total_automations,
                    "active": active_automations,
                    "listed": listed_automations
                },
                "token_usage": {
                    "today": total_tokens_used_today,
                    "week": total_tokens_used_week,
                    "month": total_tokens_used_month
                },
                "payments": {
                    "today": {
                        "total": total_payments_today,
                        "successful": successful_payments_today,
                        "success_rate": round((successful_payments_today / total_payments_today * 100) if total_payments_today > 0 else 0, 2)
                    },
                    "week": {
                        "total": total_payments_week,
                        "successful": successful_payments_week,
                        "success_rate": round((successful_payments_week / total_payments_week * 100) if total_payments_week > 0 else 0, 2)
                    },
                    "month": {
                        "total": total_payments_month,
                        "successful": successful_payments_month,
                        "success_rate": round((successful_payments_month / total_payments_month * 100) if total_payments_month > 0 else 0, 2)
                    }
                },
                "revenue": {
                    "today": revenue_today,
                    "week": revenue_week,
                    "month": revenue_month
                },
                "top_automations": [
                    {
                        "id": auto.id,
                        "name": auto.name,
                        "total_tokens": auto.total_tokens
                    }
                    for auto in top_automations
                ],
                "recent_activity": {
                    "new_users": [
                        {
                            "id": user.id,
                            "email": user.email,
                            "name": user.name,
                            "created_at": user.created_at.isoformat()
                        }
                        for user in recent_users
                    ],
                    "recent_payments": [
                        {
                            "id": payment.id,
                            "user_id": payment.user_id,
                            "amount": payment.amount,
                            "status": payment.status,
                            "created_at": payment.created_at.isoformat()
                        }
                        for payment in recent_payments
                    ]
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard statistics: {str(e)}"
        )

@router.get("/system/health")
async def get_system_health_check(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Simple health check endpoint for monitoring
    """
    try:
        # Quick database check
        db.execute(text("SELECT 1"))
        
        # Basic system metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_percent = psutil.virtual_memory().percent
        
        # Determine health status
        if cpu_percent > 90 or memory_percent > 90:
            status_code = 503  # Service Unavailable
            health_status = "unhealthy"
        elif cpu_percent > 80 or memory_percent > 80:
            status_code = 200
            health_status = "degraded"
        else:
            status_code = 200
            health_status = "healthy"
        
        return {
            "status": health_status,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )
