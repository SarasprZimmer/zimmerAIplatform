from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from utils.auth import get_current_user
from database import get_db
from schemas.usage import UsageWeeklyOut, UsageMonthlyOut, UsageDistributionOut
from services.usage import get_weekly_usage, get_six_months_usage, get_distribution

router = APIRouter(prefix="/api/user/usage", tags=["User Usage"])

@router.get("", response_model=list)
def usage(
    range: str = Query("7d", pattern="^(7d|6m)$"),
    automation_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    if range == "7d":
        data = get_weekly_usage(db, user.id, automation_id)
        return data
    elif range == "6m":
        data = get_six_months_usage(db, user.id)
        return data
    raise HTTPException(status_code=400, detail="invalid range")

@router.get("/distribution", response_model=list)
def usage_distribution(
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    data = get_distribution(db, user.id)
    return data
