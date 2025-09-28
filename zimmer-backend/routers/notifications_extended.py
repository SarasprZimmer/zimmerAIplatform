"""
Extended notifications endpoints for Zimmer AI Platform
Handles unread count, streaming, and advanced notification features
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
import json
import asyncio

from database import get_db
from models.user import User
from models.notification import Notification
from utils.auth import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications-extended"])

@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get unread notifications count for current user"""
    try:
        unread_count = db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.read_at.is_(None)
        ).count()
        
        return {
            "unread_count": unread_count,
            "user_id": current_user.id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get unread count: {str(e)}"
        )

@router.get("/stream")
async def stream_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stream notifications using Server-Sent Events (SSE)"""
    
    async def event_generator():
        """Generate SSE events for notifications"""
        try:
            # Send initial connection event
            yield f"data: {json.dumps({'type': 'connected', 'message': 'Connected to notification stream'})}\n\n"
            
            last_notification_id = 0
            
            while True:
                # Check for new notifications
                new_notifications = db.query(Notification).filter(
                    Notification.user_id == current_user.id,
                    Notification.id > last_notification_id,
                    Notification.read_at.is_(None)
                ).order_by(Notification.created_at.desc()).limit(10).all()
                
                for notification in new_notifications:
                    notification_data = {
                        "type": "notification",
                        "id": notification.id,
                        "title": notification.title,
                        "message": notification.message,
                        "type": notification.type,
                        "created_at": notification.created_at.isoformat(),
                        "read_at": notification.read_at.isoformat() if notification.read_at else None
                    }
                    
                    yield f"data: {json.dumps(notification_data)}\n\n"
                    last_notification_id = notification.id
                
                # Send heartbeat every 30 seconds
                yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.utcnow().isoformat()})}\n\n"
                
                # Wait 5 seconds before checking again
                await asyncio.sleep(5)
                
        except Exception as e:
            error_data = {
                "type": "error",
                "message": f"Stream error: {str(e)}"
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "https://panel.zimmerai.com",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

@router.get("/recent")
async def get_recent_notifications(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent notifications for current user"""
    try:
        notifications = db.query(Notification).filter(
            Notification.user_id == current_user.id
        ).order_by(Notification.created_at.desc()).limit(limit).all()
        
        notification_list = []
        for notification in notifications:
            notification_list.append({
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "type": notification.type,
                "read_at": notification.read_at.isoformat() if notification.read_at else None,
                "created_at": notification.created_at.isoformat()
            })
        
        return {
            "notifications": notification_list,
            "total": len(notification_list),
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent notifications: {str(e)}"
        )

@router.post("/mark-read/{notification_id}")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a specific notification as read"""
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        if notification.read_at is None:
            notification.read_at = datetime.utcnow()
            db.commit()
        
        return {
            "message": "Notification marked as read",
            "notification_id": notification_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}"
        )

@router.post("/mark-all-read")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read for current user"""
    try:
        updated_count = db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.read_at.is_(None)
        ).update({
            "read_at": datetime.utcnow()
        })
        
        db.commit()
        
        return {
            "message": f"Marked {updated_count} notifications as read",
            "updated_count": updated_count
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark all notifications as read: {str(e)}"
        )

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific notification"""
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        db.delete(notification)
        db.commit()
        
        return {
            "message": "Notification deleted successfully",
            "notification_id": notification_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete notification: {str(e)}"
        )

@router.get("/stats")
async def get_notification_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notification statistics for current user"""
    try:
        total_notifications = db.query(Notification).filter(
            Notification.user_id == current_user.id
        ).count()
        
        unread_notifications = db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.read_at.is_(None)
        ).count()
        
        read_notifications = total_notifications - unread_notifications
        
        # Get notifications by type
        notifications_by_type = db.query(
            Notification.type,
            db.func.count(Notification.id).label('count')
        ).filter(
            Notification.user_id == current_user.id
        ).group_by(Notification.type).all()
        
        type_stats = {item.type: item.count for item in notifications_by_type}
        
        return {
            "total_notifications": total_notifications,
            "unread_notifications": unread_notifications,
            "read_notifications": read_notifications,
            "notifications_by_type": type_stats,
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notification stats: {str(e)}"
        )
