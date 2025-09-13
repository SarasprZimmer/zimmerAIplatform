from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, literal, case
from sqlalchemy.sql import label, text
from models.token_usage import TokenUsage
from models.automation import Automation

def _date_floor_day(dialect_name: str, column):
    if dialect_name == "sqlite":
        return func.strftime("%Y-%m-%d", column)
    # postgres & others support date_trunc
    return func.to_char(func.date_trunc("day", column), "YYYY-MM-DD")

def _date_floor_month(dialect_name: str, column):
    if dialect_name == "sqlite":
        return func.strftime("%Y-%m", column)
    return func.to_char(func.date_trunc("month", column), "YYYY-MM")

def get_weekly_usage(db: Session, user_id: int, automation_id: Optional[int] = None):
    """Last 7 full days (including today). Returns list of dicts with day, tokens, sessions."""
    now = datetime.utcnow()
    start = now - timedelta(days=6)  # 7-day window
    dialect = db.bind.dialect.name

    q = db.query(
        label("day", _date_floor_day(dialect, TokenUsage.created_at)),
        func.coalesce(func.sum(TokenUsage.tokens_used), 0).label("tokens"),
        func.count(TokenUsage.id).label("sessions"),
    ).filter(TokenUsage.user_id == user_id, TokenUsage.created_at >= start)

    if automation_id:
        q = q.filter(TokenUsage.automation_id == automation_id)

    q = q.group_by("day").order_by("day")
    rows = q.all()

    # Fill missing days with zeros
    by_day = {r.day: {"day": r.day, "tokens": int(r.tokens or 0), "sessions": int(r.sessions or 0)} for r in rows}
    res = []
    for i in range(7):
        d = (start + timedelta(days=i)).strftime("%Y-%m-%d")
        res.append(by_day.get(d, {"day": d, "tokens": 0, "sessions": 0}))
    return res

def get_six_months_usage(db: Session, user_id: int):
    """Last 6 full months (including current month). Returns month + total tokens."""
    now = datetime.utcnow()
    # Consider last 6 months including current
    six_months_ago = (now.replace(day=1) - timedelta(days=150))  # approx 5 months back
    dialect = db.bind.dialect.name

    q = db.query(
        label("month", _date_floor_month(dialect, TokenUsage.created_at)),
        func.coalesce(func.sum(TokenUsage.tokens_used), 0).label("value"),
    ).filter(TokenUsage.user_id == user_id, TokenUsage.created_at >= six_months_ago
    ).group_by("month").order_by("month")

    rows = q.all()
    # No strict zero-fill for months; return existing months in order
    return [{"month": r.month, "value": int(r.value or 0)} for r in rows]

def get_distribution(db: Session, user_id: int):
    """Tokens grouped by automation for the user's usages."""
    q = db.query(
        Automation.name.label("name"),
        func.coalesce(func.sum(TokenUsage.tokens_used), 0).label("value"),
    ).join(Automation, Automation.id == TokenUsage.automation_id, isouter=True
    ).filter(TokenUsage.user_id == user_id
    ).group_by(Automation.name
    ).order_by(func.sum(TokenUsage.tokens_used).desc())

    rows = q.all()
    return [{"name": r.name or "Unknown", "value": int(r.value or 0)} for r in rows]
