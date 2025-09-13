from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import SessionLocal
from models.user import User
from models.fallback_log import FallbackLog
from models.user_automation import UserAutomation
from models.automation import Automation
from schemas.fallback import FallbacksResponse
from utils.auth import require_admin

router = APIRouter()

def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/fallbacks", response_model=FallbacksResponse)
async def get_fallbacks(
    client_id: Optional[int] = Query(None, description="Filter by client ID"),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get fallback logs with optional client filtering (admin only)
    """
    try:
        # Build base query with joins
        query = db.query(
            FallbackLog,
            User.name.label('client_name'),
            Automation.name.label('automation_name')
        ).join(
            UserAutomation, FallbackLog.user_automation_id == UserAutomation.id
        ).join(
            User, UserAutomation.user_id == User.id
        ).join(
            Automation, UserAutomation.automation_id == Automation.id
        )
        
        # Apply client filter if provided
        if client_id is not None:
            query = query.filter(User.id == client_id)
        
        # Get total count
        total_count = query.count()
        
        # Get fallbacks ordered by newest first
        fallback_records = query.order_by(
            FallbackLog.created_at.desc()
        ).all()
        
        # Format response
        formatted_fallbacks = []
        for record, client_name, automation_name in fallback_records:
            formatted_fallbacks.append({
                "id": record.id,
                "client_name": client_name,
                "automation_name": automation_name,
                "message": record.message,
                "error_type": record.error_type,
                "timestamp": record.created_at,
                "user_automation_id": record.user_automation_id
            })
        
        return FallbacksResponse(
            total_count=total_count,
            fallbacks=formatted_fallbacks
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve fallback logs: {str(e)}"
        ) 