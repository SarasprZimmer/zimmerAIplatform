from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, List
from datetime import datetime, timedelta
from database import SessionLocal
from models.user import User
from models.payment import Payment
from models.token_usage import TokenUsage
from models.user_automation import UserAutomation
from models.automation import Automation
from models.ticket import Ticket
from models.kb_status_history import KBStatusHistory
from models.kb_template import KBTemplate
from schemas.admin import UserListResponse, PaymentListResponse, UserTokenUsageResponse, UserAutomationAdminResponse, PaymentResponse, UsageStatsResponse, PeriodInfo
from utils.auth_dependency import get_current_admin_user, get_db
from cache_manager import cache as cache_manager

router = APIRouter()

@router.get("/users", response_model=UserListResponse)
async def get_users(
    is_admin: Optional[bool] = Query(None, description="Filter by admin status"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Get list of all users/clients (admin only) - Main endpoint
    """
    # Check cache first
    cache_key = f"admin_users_{is_admin}"
    cached_data = cache_manager.get(cache_key)
    
    if cached_data:
        return UserListResponse(**cached_data)
    
    try:
        # Build base query
        query = db.query(User)
        
        # Apply filters if provided
        if is_admin is not None:
            query = query.filter(User.is_admin == is_admin)
        
        # Get total count
        total_count = query.count()
        
        # Get users
        users = query.all()
        
        # Format response
        formatted_users = []
        for user in users:
            formatted_users.append({
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "phone_number": user.phone_number,
                "role": user.role.value if user.role else None,
                "is_admin": user.is_admin,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None
            })
        
        result = UserListResponse(
            total_count=total_count,
            users=formatted_users
        )
        
        # Cache the result for 3 minutes
        cache_manager.set(cache_key, result.dict(), ttl=180)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}"
        )

@router.get("/users-legacy", response_model=UserListResponse)
async def get_users_legacy(
    is_admin: Optional[bool] = Query(None, description="Filter by admin status"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Get list of all users/clients (admin only)
    """
    # Check cache first
    cache_key = f"admin_users_{is_admin}"
    cached_data = cache_manager.get(cache_key)
    
    if cached_data:
        return UserListResponse(**cached_data)
    
    try:
        # Build base query
        query = db.query(User)
        
        # Apply filters if provided
        if is_admin is not None:
            query = query.filter(User.is_admin == is_admin)
        
        # Get total count
        total_count = query.count()
        
        # Get users ordered by newest first
        users = query.order_by(User.created_at.desc()).all()
        
        # Format response (exclude password_hash for security)
        formatted_users = []
        for user in users:
            formatted_users.append({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone_number": user.phone_number,
                "is_admin": user.is_admin,
                "created_at": user.created_at
            })
        
        result = UserListResponse(
            total_count=total_count,
            users=formatted_users
        )
        
        # Cache the result for 3 minutes
        cache_manager.set(cache_key, result.dict(), ttl=180)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}"
        )

@router.get("/payments", response_model=PaymentListResponse)
async def get_payments(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    payment_status: Optional[str] = Query(None, description="Filter by payment status"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Get payment history (admin only)
    """
    try:
        # Build base query with user join
        query = db.query(
            Payment,
            User.name.label('user_name')
        ).join(
            User, Payment.user_id == User.id
        )
        
        # Apply filters if provided
        if user_id is not None:
            query = query.filter(Payment.user_id == user_id)
        
        if payment_status is not None:
            query = query.filter(Payment.status == payment_status)
        
        # Get total count
        total_count = query.count()
        
        # Get payments ordered by newest first
        payment_records = query.order_by(Payment.created_at.desc()).all()
        
        # Format response
        formatted_payments = []
        for payment, user_name in payment_records:
            formatted_payments.append(PaymentResponse(
                id=payment.id,
                user_id=payment.user_id,
                user_name=user_name,
                amount=payment.amount,
                tokens_purchased=payment.tokens_purchased,
                method=payment.method,
                transaction_id=payment.transaction_id,
                status=payment.status,
                created_at=payment.created_at
            ))
        
        return PaymentListResponse(
            total_count=total_count,
            payments=formatted_payments
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve payments: {str(e)}"
        )

# MOVED: This route is now defined after /usage/stats to fix route ordering
# @router.get("/usage/{user_id}", response_model=UserTokenUsageResponse)
# async def get_user_token_usage(
#     user_id: int = Path(..., description="User ID to get token usage for"),
#     db: Session = Depends(get_db),
#     current_admin: User = Depends(get_current_admin_user)
# ):
#     """
#     Get token usage for a specific user (admin only)
#     """
#     try:
#         # Verify user exists
#         user = db.query(User).filter(User.id == user_id).first()
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="User not found"
#             )
#         
#         # Build query to get token usage with automation names
#         query = db.query(
#             TokenUsage,
#             Automation.name.label('automation_name')
#         ).join(
#             UserAutomation, TokenUsage.user_automation_id == UserAutomation.id
#         ).join(
#             Automation, UserAutomation.automation_id == Automation.id
#         ).filter(
#             UserAutomation.user_id == user_id
#         )
#         
#         # Get usage records ordered by newest first
#         usage_records = query.order_by(TokenUsage.created_at.desc()).all()
#         
#         # Calculate totals
#         total_tokens_used = sum(record.tokens_used for record, _ in usage_records)
#         
#         # Estimate cost (assuming $0.002 per 1K tokens - adjust as needed)
#         total_cost = (total_tokens_used / 1000) * 0.002
#         
#         # Format usage entries
#         usage_entries = []
#         for usage, automation_name in usage_records:
#             usage_entries.append(TokenUsageResponse(
#                 id=usage.id,
#                 user_automation_id=usage.user_automation_id,
#                 automation_name=automation_name,
#                 tokens_used=usage.tokens_used,
#                 usage_type=usage.usage_type,
#                 description=usage.description,
#                 created_at=usage.created_at
#             ))
#         
#         return UserTokenUsageResponse(
#             user_id=user_id,
#             user_name=user.name,
#             total_tokens_used=total_tokens_used,
#             total_cost=total_cost,
#             usage_entries=usage_entries
#         )
#         
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to retrieve user token usage: {str(e)}"
#         )

@router.get("/user-automations", response_model=List[UserAutomationAdminResponse])
async def get_user_automations_admin(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    demo_only: Optional[bool] = Query(None, description="Show only demo users"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Get all user automations with demo token information (admin only)
    """
    try:
        # Build base query with joins
        query = db.query(
            UserAutomation,
            User.name.label('user_name'),
            Automation.name.label('automation_name')
        ).join(
            User, UserAutomation.user_id == User.id
        ).join(
            Automation, UserAutomation.automation_id == Automation.id
        )
        
        # Apply filters
        if user_id is not None:
            query = query.filter(UserAutomation.user_id == user_id)
        
        if demo_only:
            query = query.filter(UserAutomation.is_demo_active == True)
        
        # Get records ordered by newest first
        records = query.order_by(UserAutomation.created_at.desc()).all()
        
        # Format response
        formatted_automations = []
        for ua, user_name, automation_name in records:
            formatted_automations.append({
                "id": ua.id,
                "user_id": ua.user_id,
                "user_name": user_name,
                "automation_id": ua.automation_id,
                "automation_name": automation_name,
                "tokens_remaining": ua.tokens_remaining or 0,
                "demo_tokens": ua.demo_tokens or 0,
                "is_demo_active": ua.is_demo_active or False,
                "demo_expired": ua.demo_expired or False,
                "status": ua.status or "active",
                "created_at": ua.created_at
            })
        
        return formatted_automations
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user automations: {str(e)}"
        )

@router.get("/tickets")
async def get_tickets(
    ticket_status: Optional[str] = Query(None, description="Filter by ticket status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Get all support tickets (admin only)
    """
    try:
        # Build base query with user join
        query = db.query(
            Ticket,
            User.name.label('user_name')
        ).join(
            User, Ticket.user_id == User.id
        )
        
        # Apply filters if provided
        if ticket_status is not None:
            query = query.filter(Ticket.status == ticket_status)
        
        if priority is not None:
            query = query.filter(Ticket.importance == priority)
        
        # Get total count
        total_count = query.count()
        
        # Get tickets ordered by newest first
        ticket_records = query.order_by(Ticket.created_at.desc()).all()
        
        # Format response
        formatted_tickets = []
        for ticket, user_name in ticket_records:
            formatted_tickets.append({
                "id": ticket.id,
                "user_id": ticket.user_id,
                "user_name": user_name,
                "subject": ticket.subject,
                "description": ticket.message,
                "description": ticket.message,
                "status": ticket.status,
                "importance": ticket.importance,
                "assigned_to": ticket.assigned_to,
                "created_at": ticket.created_at,
                "updated_at": ticket.updated_at,
                "assigned_admin_name": None,  # Will be populated if needed
                "attachment_path": ticket.attachment_path
            })
        
        return {
            "total_count": total_count,
            "tickets": formatted_tickets
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tickets: {str(e)}"
        )

@router.get("/automations")
async def get_automations(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Get all available automations (admin only)
    """
    try:
        # Get all automations with only the columns we need
        automations = db.query(
            Automation.id,
            Automation.name,
            Automation.description,
            Automation.status,
            Automation.created_at
        ).order_by(Automation.name).all()
        
        # Format response
        formatted_automations = []
        for automation in automations:
            formatted_automations.append({
                "id": automation.id,
                "name": automation.name,
                "description": automation.description,
                "is_active": automation.status,
                "created_at": automation.created_at
            })
        
        return {
            "total_count": len(formatted_automations),
            "automations": formatted_automations
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve automations: {str(e)}"
        ) 

@router.get("/usage")
async def get_usage_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Get usage statistics (admin only)
    """
    try:
        from sqlalchemy import func
        from datetime import datetime, timedelta
        from models.token_usage import TokenUsage
        
        # Get tokens used in the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        tokens_used = db.query(func.sum(TokenUsage.tokens_used)).filter(
            TokenUsage.created_at >= thirty_days_ago
        ).scalar() or 0
        
        return {
            "tokens_used": int(tokens_used),
            "period_days": 30
        }
            
    except Exception as e:
        return {
            "tokens_used": 0,
            "period_days": 30,
            "error": str(e)
        }

@router.get("/usage/stats")
async def get_usage_stats_detailed(
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Get detailed usage statistics (admin only) - DEBUG VERSION
    """
    try:
        # Always return the same response for debugging
        return UsageStatsResponse(
            type="general_overview",
            total_tokens_used=0,
            total_users=0,
            active_automations=0,
            estimated_cost_usd=0,
            message="Debug: Usage stats endpoint working"
        )
            
    except Exception as e:
        return UsageStatsResponse(
            type="error",
            error=f"Exception occurred: {str(e)}"
        )

@router.get("/test-usage-stats", response_model=UsageStatsResponse)
async def test_usage_stats(
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Test endpoint for usage stats validation
    """
    return UsageStatsResponse(
        type="test",
        total_tokens_used=0,
        total_requests=0,
        average_tokens_per_request=0,
        estimated_cost_usd=0,
        message="Test response"
    )

@router.get("/test")
async def test_endpoint():
    """
    Simple test endpoint to verify server is working
    """
    return {"message": "Admin router is working", "status": "ok"}

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Get dashboard statistics for admin panel
    """
    try:
        from sqlalchemy import func
        from datetime import datetime, timedelta
        from models.ticket import Ticket
        from models.payment import Payment
        from models.token_usage import TokenUsage
        
        # Get total users
        total_users = db.query(User).count()
        
        # Get active tickets (open status)
        active_tickets = db.query(Ticket).filter(Ticket.status == "open").count()
        
        # Get tokens used in the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        tokens_used = db.query(func.sum(TokenUsage.tokens_used)).filter(
            TokenUsage.created_at >= thirty_days_ago
        ).scalar() or 0
        
        # Get monthly revenue (current month)
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_revenue = db.query(func.sum(Payment.amount)).filter(
            Payment.status == "completed",
            Payment.created_at >= current_month_start
        ).scalar() or 0
        
        return {
            "total_users": total_users,
            "active_tickets": active_tickets,
            "tokens_used": int(tokens_used),
            "monthly_revenue": float(monthly_revenue)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve dashboard stats: {str(e)}"
        )

@router.get("/dashboard/activity")
async def get_dashboard_activity(
    limit: int = Query(10, le=50, description="Number of activities to return"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Get recent dashboard activities
    """
    try:
        from models.ticket import Ticket
        from models.payment import Payment
        
        activities = []
        
        # Get recent tickets
        recent_tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).limit(5).all()
        for ticket in recent_tickets:
            activities.append({
                "id": f"ticket_{ticket.id}",
                "type": "ticket",
                "message": f"تیکت جدید از {ticket.user_id}: {ticket.subject[:50]}...",
                "created_at": ticket.created_at.isoformat()
            })
        
        # Get recent payments
        recent_payments = db.query(Payment).filter(
            Payment.status == "completed"
        ).order_by(Payment.created_at.desc()).limit(5).all()
        
        for payment in recent_payments:
            activities.append({
                "id": f"payment_{payment.id}",
                "type": "payment",
                "message": f"پرداخت جدید: {payment.amount} ریال",
                "created_at": payment.created_at.isoformat()
            })
        
        # Sort by created_at and limit
        activities.sort(key=lambda x: x["created_at"], reverse=True)
        return activities[:limit]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve dashboard activity: {str(e)}"
        )

@router.get("/kb-monitoring")
async def get_kb_monitoring(
    automation_id: Optional[int] = Query(None, description="Filter by automation ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    kb_health_status: Optional[str] = Query(None, description="Filter by health status"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Get KB monitoring status (admin only)
    """
    try:
        # Check if KBStatusHistory table has any records first
        total_records = db.query(KBStatusHistory).count()
        
        if total_records == 0:
            return {
                "total_records": 0,
                "health_summary": {},
                "statuses": [],
                "message": "No KB monitoring data available"
            }
        
        # Build base query with joins
        query = db.query(
            KBStatusHistory,
            User.name.label('user_name'),
            Automation.name.label('automation_name')
        ).join(
            User, KBStatusHistory.user_id == User.id
        ).join(
            Automation, KBStatusHistory.automation_id == Automation.id
        )
        
        # Apply filters
        if automation_id:
            query = query.filter(KBStatusHistory.automation_id == automation_id)
        
        if user_id:
            query = query.filter(KBStatusHistory.user_id == user_id)
        
        if health_status:
            query = query.filter(KBStatusHistory.kb_health == health_status)
        
        # Get latest status for each user-automation combination
        latest_statuses = []
        seen_combinations = set()
        
        # Order by timestamp (newest first) and get unique combinations
        results = query.order_by(KBStatusHistory.timestamp.desc()).all()
        
        for kb_status, user_name, automation_name in results:
            combination = (kb_status.user_id, kb_status.automation_id)
            if combination not in seen_combinations:
                seen_combinations.add(combination)
                latest_statuses.append({
                    "id": kb_status.id,
                    "user_id": kb_status.user_id,
                    "user_name": user_name,
                    "automation_id": kb_status.automation_id,
                    "automation_name": automation_name,
                    "kb_health": kb_status.kb_health,
                    "backup_status": kb_status.backup_status,
                    "error_logs": kb_status.error_logs,
                    "timestamp": kb_status.timestamp
                })
        
        # Calculate summary statistics
        health_counts = {}
        for status in latest_statuses:
            health = status["kb_health"]
            health_counts[health] = health_counts.get(health, 0) + 1
        
        return {
            "total_records": len(latest_statuses),
            "health_summary": health_counts,
            "statuses": latest_statuses
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve KB monitoring data: {str(e)}"
        ) 