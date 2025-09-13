from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from schemas.notification import NotificationOut, MarkReadIn
from models.notification import Notification
from utils.auth_dependency import get_current_user
from database import get_db

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

@router.get("", response_model=List[NotificationOut])
def list_notifications(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.is_read.asc(), Notification.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return q.all()

@router.post("/mark-read")
def mark_read(
    payload: MarkReadIn,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not payload.ids:
        return {"updated": 0}
    rows = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id, Notification.id.in_(payload.ids))
        .update(
            {
                Notification.is_read: True,
                Notification.read_at: datetime.utcnow(),
            },
            synchronize_session=False,
        )
    )
    db.commit()
    return {"updated": rows}

@router.post("/mark-all-read")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    rows = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id, Notification.is_read == False)  # noqa: E712
        .update(
            {
                Notification.is_read: True,
                Notification.read_at: datetime.utcnow(),
            },
            synchronize_session=False,
        )
    )
    db.commit()
    return {"updated": rows}

# (Optional) Admin-only create endpoint — only if your admin auth is ready:
# from app.deps import admin_required
# @router.post("/admin/create", dependencies=[Depends(admin_required)], response_model=NotificationOut)
# def admin_create_notification(...)
