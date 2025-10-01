"""
Optimized Endpoints for Zimmer AI Platform
High-performance versions of critical endpoints with caching and query optimization
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
from typing import Optional, List
from datetime import datetime, timedelta

from database import get_db
from models.user import User
from models.automation import Automation
from models.user_automation import UserAutomation
from models.token_usage import TokenUsage
from models.payment import Payment
from models.ticket import Ticket
from utils.auth_dependency import get_current_user
from utils.auth import get_current_admin_user
from cache_manager import (
    cached, cache_user_data, get_cached_user_data, invalidate_user_cache,
    cache_dashboard_data, get_cached_dashboard_data,
    cache_marketplace_data, get_cached_marketplace_data,
    cache_admin_stats, get_cached_admin_stats
)

router = APIRouter(prefix="/api/optimized", tags=["optimized"])

@router.get("/me")
@cached(ttl=300, key_prefix="user_me:")
async def get_current_user_optimized(
    current_user: User = Depends(get_current_user)
):
    """Optimized current user endpoint with caching"""
    try:
        # Return cached user data if available
        cached_data = get_cached_user_data(current_user.id)
        if cached_data:
            return cached_data

        # Cache the user data
        user_data = {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "phone_number": current_user.phone_number,
            "role": current_user.role,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at,
            "email_verified_at": current_user.email_verified_at,
            "twofa_enabled": current_user.twofa_enabled
        }

        cache_user_data(current_user.id, user_data, ttl=300)
        return user_data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve user info: {str(e)}"
        )

@router.get("/user/dashboard")
async def get_user_dashboard_optimized(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Optimized user dashboard with caching and efficient queries"""
    try:
        # Check cache first
        cached_data = get_cached_dashboard_data(current_user.id)
        if cached_data:
            return cached_data

        # Single optimized query with proper joins
        user_automations = db.query(
            UserAutomation,
            Automation.name,
            Automation.description,
            Automation.pricing_type,
            Automation.price_per_token,
            Automation.status
        ).join(
            Automation, UserAutomation.automation_id == Automation.id
        ).filter(
            UserAutomation.user_id == current_user.id
        ).options(
            joinedload(UserAutomation.automation)
        ).all()

        # Calculate totals efficiently
        total_demo_tokens = sum(ua.demo_tokens for ua, _, _, _, _, _ in user_automations)
        total_paid_tokens = sum(ua.tokens_remaining or 0 for ua, _, _, _, _, _ in user_automations)
        has_active_demo = any(ua.is_demo_active for ua, _, _, _, _, _ in user_automations)
        has_expired_demo = any(ua.demo_expired for ua, _, _, _, _, _ in user_automations)

        # Format automations
        automations = []
        for ua, name, description, pricing_type, price_per_token, status in user_automations:
            automations.append({
                "id": ua.id,
                "automation_id": ua.automation_id,
                "automation_name": name,
                "tokens_remaining": ua.tokens_remaining or 0,
                "demo_tokens": ua.demo_tokens,
                "is_demo_active": ua.is_demo_active,
                "demo_expired": ua.demo_expired,
                "status": ua.status,
                "created_at": ua.created_at
            })

        # Build response
        dashboard_data = {
            "user": {
                "id": current_user.id,
                "name": current_user.name,
                "email": current_user.email,
                "phone_number": current_user.phone_number,
                "role": current_user.role,
                "is_active": current_user.is_active,
                "created_at": current_user.created_at
            },
            "automations": automations,
            "total_demo_tokens": total_demo_tokens,
            "total_paid_tokens": total_paid_tokens,
            "has_active_demo": has_active_demo,
            "has_expired_demo": has_expired_demo
        }

        # Cache the result
        cache_dashboard_data(current_user.id, dashboard_data, ttl=120)

        return dashboard_data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve dashboard data: {str(e)}"
        )

@router.get("/automations/marketplace")
async def get_marketplace_automations_optimized(
    db: Session = Depends(get_db)
):
    """Optimized marketplace endpoint with caching (public endpoint)"""
    try:
        # Check cache first
        cached_data = get_cached_marketplace_data()
        if cached_data:
            return cached_data

        # Optimized query with proper indexing - use string comparisons
        automations = db.query(Automation).filter(
            and_(
                Automation.status == "active",  # Changed from True to "active"
                Automation.is_listed == "true",  # Changed from True to "true"
                Automation.health_status == "healthy"
            )
        ).order_by(Automation.created_at.desc()).all()

        marketplace_data = []
        for automation in automations:
            marketplace_data.append({
                "id": automation.id,
                "name": automation.name,
                "description": automation.description,
                "pricing_type": automation.pricing_type,
                "price_per_token": automation.price_per_token,
                "health_status": automation.health_status,
                "last_health_at": automation.last_health_at,
                "created_at": automation.created_at
            })

        response_data = {
            "automations": marketplace_data,
            "total": len(marketplace_data),
            "message": "Available automations in marketplace"
        }

        # Cache the result
        cache_marketplace_data(response_data, ttl=600)

        return response_data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve marketplace data: {str(e)}"
        )

@router.get("/user/usage")
async def get_user_usage_optimized(
    range: str = Query("7d", pattern="^(7d|6m)$"),
    automation_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Optimized usage endpoint with efficient date queries"""
    try:
        if range == "7d":
            # Last 7 days with optimized date query
            six_days_ago = datetime.utcnow() - timedelta(days=6)

            query = db.query(
                func.date(TokenUsage.created_at).label('day'),
                func.sum(TokenUsage.tokens_used).label('tokens'),
                func.count(TokenUsage.id).label('sessions')
            ).filter(
                and_(
                    TokenUsage.user_id == current_user.id,
                    TokenUsage.created_at >= six_days_ago
                )
            )

            if automation_id:
                query = query.filter(TokenUsage.automation_id == automation_id)

            results = query.group_by(
                func.date(TokenUsage.created_at)
            ).order_by('day').all()

            return [
                {
                    "day": str(result.day),
                    "tokens": int(result.tokens or 0),
                    "sessions": int(result.sessions or 0)
                }
                for result in results
            ]

        elif range == "6m":
            # Last 6 months with optimized month grouping
            six_months_ago = datetime.utcnow() - timedelta(days=180)

            query = db.query(
                func.strftime('%Y-%m', TokenUsage.created_at).label('month'),
                func.sum(TokenUsage.tokens_used).label('value')
            ).filter(
                and_(
                    TokenUsage.user_id == current_user.id,
                    TokenUsage.created_at >= six_months_ago
                )
            )

            if automation_id:
                query = query.filter(TokenUsage.automation_id == automation_id)

            results = query.group_by(
                func.strftime('%Y-%m', TokenUsage.created_at)
            ).order_by('month').all()

            return [
                {"month": result.month, "value": int(result.value or 0)}
                for result in results
            ]

        raise HTTPException(status_code=400, detail="Invalid range parameter")

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve usage data: {str(e)}"
        )

@router.get("/admin/dashboard")
async def get_admin_dashboard_optimized(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Optimized admin dashboard with caching and efficient queries"""
    try:
        # Check cache first
        cached_data = get_cached_admin_stats()
        if cached_data:
            return cached_data

        # Single query to get all statistics
        stats = db.query(
            func.count(User.id).label('total_users'),
            func.count(Automation.id).label('total_automations'),
            func.count(Ticket.id).label('total_tickets'),
            func.count(UserAutomation.id).label('active_automations'),
            func.count(Payment.id).label('total_payments'),
            func.sum(Payment.amount).label('total_revenue')
        ).first()

        # Get recent activity counts
        last_24h = datetime.utcnow() - timedelta(hours=24)
        recent_stats = db.query(
            func.count(User.id).label('new_users_24h'),
            func.count(Ticket.id).label('new_tickets_24h'),
            func.count(Payment.id).label('new_payments_24h')
        ).filter(
            or_(
                User.created_at >= last_24h,
                Ticket.created_at >= last_24h,
                Payment.created_at >= last_24h
            )
        ).first()

        dashboard_data = {
            "status": "success",
            "data": {
                "total_users": stats.total_users or 0,
                "total_automations": stats.total_automations or 0,
                "total_tickets": stats.total_tickets or 0,
                "active_automations": stats.active_automations or 0,
                "total_payments": stats.total_payments or 0,
                "total_revenue": int(stats.total_revenue or 0),
                "new_users_24h": recent_stats.new_users_24h or 0,
                "new_tickets_24h": recent_stats.new_tickets_24h or 0,
                "new_payments_24h": recent_stats.new_payments_24h or 0,
                "system_status": "healthy"
            }
        }

        # Cache the result
        cache_admin_stats(dashboard_data, ttl=120)

        return dashboard_data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get dashboard data: {str(e)}"
        )

@router.get("/cache/stats")
async def get_cache_statistics():
    """Get cache statistics for monitoring"""
    from cache_manager import get_cache_stats
    return get_cache_stats()

@router.post("/cache/clear")
async def clear_cache(
    current_admin: User = Depends(get_current_admin_user)
):
    """Clear all cache entries (admin only)"""
    from cache_manager import cache
    cache.clear()
    return {"message": "Cache cleared successfully"}

@router.post("/cache/cleanup")
async def cleanup_cache():
    """Cleanup expired cache entries"""
    from cache_manager import cleanup_cache
    removed_count = cleanup_cache()
    return {"message": f"Cleaned up {removed_count} expired entries"}
