from fastapi import APIRouter, Depends, HTTPException, Body, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Any
from sqlalchemy.orm import Session
from utils.auth_dependency import get_current_admin_user
from models.user import User
from models.notification import Notification
from database import get_db
from datetime import datetime

router = APIRouter(prefix="/api/admin/notifications", tags=["admin:notifications"])

class CreateNotificationIn(BaseModel):
    user_ids: Optional[List[int]] = Field(default=None, description="Send to these users. If omitted, must use broadcast endpoint.")
    type: str = Field(..., max_length=64, description="e.g., payment|ticket|system|automation")
    title: str = Field(..., max_length=200)
    body: Optional[str] = Field(default=None, max_length=2000)
    data: Optional[Any] = None

class BroadcastIn(BaseModel):
    type: str
    title: str
    body: Optional[str] = None
    data: Optional[Any] = None
    role: Optional[str] = Field(default=None, description="If set, broadcast only to users with this role")

@router.post("")
def create_notifications(
    payload: CreateNotificationIn,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin_user),
):
    if not payload.user_ids:
        raise HTTPException(status_code=400, detail="user_ids is required; use /broadcast for all users")
    users = db.query(User.id).filter(User.id.in_(payload.user_ids)).all()
    if not users:
        return {"created": 0}
    ctr = 0
    now = datetime.utcnow()
    for (uid,) in users:
        n = Notification(
            user_id=uid,
            type=payload.type,
            title=payload.title,
            body=payload.body,
            data=payload.data,
            created_at=now
        )
        db.add(n)
        ctr += 1
    db.commit()
    return {"created": ctr}

@router.post("/broadcast")
def broadcast_notifications(
    payload: BroadcastIn,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin_user),
):
    q = db.query(User.id)
    if payload.role:
        q = q.filter(User.role == payload.role)
    user_ids = [row.id for row in q.all()]
    if not user_ids:
        return {"created": 0}

    now = datetime.utcnow()
    batch = []
    for uid in user_ids:
        batch.append(Notification(
            user_id=uid,
            type=payload.type,
            title=payload.title,
            body=payload.body,
            data=payload.data,
            created_at=now
        ))
    db.bulk_save_objects(batch)
    db.commit()
    return {"created": len(batch)}
