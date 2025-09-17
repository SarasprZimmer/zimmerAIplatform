from pydantic import BaseModel, ConfigDict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
from datetime import datetime, timedelta
from database import get_db
from models.kb_status_history import KBStatusHistory
from models.user import User
from models.automation import Automation
from utils.auth_dependency import get_current_admin_user
from pydantic import BaseModel

router = APIRouter()

class KBHistoryResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    automation_id: int
    automation_name: str
    kb_health: str
    backup_status: bool
    error_logs: Optional[List[str]]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class KBHistoryStats(BaseModel):
    total_records: int
    healthy_count: int
    warning_count: int
    problematic_count: int
    backup_count: int

@router.get("/kb-history", response_model=List[KBHistoryResponse])
async def get_kb_history(
    automation_id: Optional[int] = Query(None, description="Filter by automation ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    from_date: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Records per page"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get paginated KB status history with filters"""
    
    # Build query
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
    
    if from_date:
        try:
            from_datetime = datetime.strptime(from_date, "%Y-%m-%d")
            query = query.filter(KBStatusHistory.timestamp >= from_datetime)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid from_date format. Use YYYY-MM-DD"
            )
    
    if to_date:
        try:
            to_datetime = datetime.strptime(to_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(KBStatusHistory.timestamp < to_datetime)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid to_date format. Use YYYY-MM-DD"
            )
    
    # Order by timestamp (newest first)
    query = query.order_by(desc(KBStatusHistory.timestamp))
    
    # Apply pagination
    offset = (page - 1) * limit
    total_count = query.count()
    
    # Get paginated results
    results = query.offset(offset).limit(limit).all()
    
    # Format response
    history_records = []
    for kb_history, user_name, automation_name in results:
        history_records.append({
            "id": kb_history.id,
            "user_id": kb_history.user_id,
            "user_name": user_name,
            "automation_id": kb_history.automation_id,
            "automation_name": automation_name,
            "kb_health": kb_history.kb_health,
            "backup_status": kb_history.backup_status,
            "error_logs": kb_history.error_logs,
            "timestamp": kb_history.timestamp
        })
    
    return history_records

@router.get("/kb-history/stats", response_model=KBHistoryStats)
async def get_kb_history_stats(
    automation_id: Optional[int] = Query(None, description="Filter by automation ID"),
    from_date: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get KB history statistics"""
    
    # Build query
    query = db.query(KBStatusHistory)
    
    # Apply filters
    if automation_id:
        query = query.filter(KBStatusHistory.automation_id == automation_id)
    
    if from_date:
        try:
            from_datetime = datetime.strptime(from_date, "%Y-%m-%d")
            query = query.filter(KBStatusHistory.timestamp >= from_datetime)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid from_date format. Use YYYY-MM-DD"
            )
    
    if to_date:
        try:
            to_datetime = datetime.strptime(to_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(KBStatusHistory.timestamp < to_datetime)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid to_date format. Use YYYY-MM-DD"
            )
    
    # Get counts
    total_records = query.count()
    healthy_count = query.filter(KBStatusHistory.kb_health == "healthy").count()
    warning_count = query.filter(KBStatusHistory.kb_health == "warning").count()
    problematic_count = query.filter(KBStatusHistory.kb_health == "problematic").count()
    backup_count = query.filter(KBStatusHistory.backup_status == True).count()
    
    return {
        "total_records": total_records,
        "healthy_count": healthy_count,
        "warning_count": warning_count,
        "problematic_count": problematic_count,
        "backup_count": backup_count
    }

@router.get("/kb-history/chart-data")
async def get_kb_history_chart_data(
    automation_id: Optional[int] = Query(None, description="Filter by automation ID"),
    days: int = Query(7, ge=1, le=30, description="Number of days to include"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get chart data for KB history (last N days)"""
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Build query
    query = db.query(KBStatusHistory)
    
    if automation_id:
        query = query.filter(KBStatusHistory.automation_id == automation_id)
    
    query = query.filter(
        and_(
            KBStatusHistory.timestamp >= start_date,
            KBStatusHistory.timestamp <= end_date
        )
    )
    
    # Get all records in date range
    records = query.all()
    
    # Group by date
    daily_stats = {}
    for record in records:
        date_key = record.timestamp.strftime("%Y-%m-%d")
        if date_key not in daily_stats:
            daily_stats[date_key] = {
                "healthy": 0,
                "warning": 0,
                "problematic": 0,
                "total": 0
            }
        
        daily_stats[date_key]["total"] += 1
        if record.kb_health == "healthy":
            daily_stats[date_key]["healthy"] += 1
        elif record.kb_health == "warning":
            daily_stats[date_key]["warning"] += 1
        elif record.kb_health == "problematic":
            daily_stats[date_key]["problematic"] += 1
    
    # Fill missing dates with zeros
    chart_data = []
    for i in range(days):
        date = (end_date - timedelta(days=i)).strftime("%Y-%m-%d")
        stats = daily_stats.get(date, {
            "healthy": 0,
            "warning": 0,
            "problematic": 0,
            "total": 0
        })
        chart_data.append({
            "date": date,
            "healthy": stats["healthy"],
            "warning": stats["warning"],
            "problematic": stats["problematic"],
            "total": stats["total"]
        })
    
    # Reverse to show oldest first
    chart_data.reverse()
    
    return {
        "chart_data": chart_data,
        "date_range": {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
    } 