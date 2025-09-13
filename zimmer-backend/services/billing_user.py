from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, label
from models.user_automation import UserAutomation
from models.automation import Automation
from models.payment import Payment

def get_active_automations(db: Session, user_id: int):
    q = (
        db.query(
            UserAutomation.id.label("id"),
            UserAutomation.automation_id.label("automation_id"),
            Automation.name.label("name"),
            Automation.description.label("description"),
            UserAutomation.tokens_remaining.label("tokens_remaining"),
            UserAutomation.demo_tokens.label("demo_tokens"),
            UserAutomation.integration_status.label("integration_status"),
            UserAutomation.provisioned_at.label("created_at"),
        )
        .join(Automation, Automation.id == UserAutomation.automation_id)
        .filter(UserAutomation.user_id == user_id)
        .order_by(UserAutomation.provisioned_at.desc())
    )
    rows = q.all()
    res = []
    for r in rows:
        res.append({
            "id": r.id,
            "automation_id": r.automation_id,
            "name": r.name,
            "description": r.description,
            "tokens_remaining": int(r.tokens_remaining or 0),
            "demo_tokens": int(r.demo_tokens or 0),
            "integration_status": r.integration_status,
            "created_at": r.created_at or datetime.utcnow(),
        })
    return res

def get_user_payments(db: Session, user_id: int, limit: int = 20, offset: int = 0, order: str = "desc"):
    base = db.query(Payment).filter(Payment.user_id == user_id)
    total = base.count()
    q = base
    q = q.order_by(Payment.created_at.desc() if order.lower() == "desc" else Payment.created_at.asc())
    q = q.limit(limit).offset(offset)
    rows = q.all()
    items = []
    for p in rows:
        items.append({
            "id": p.id,
            "automation_id": p.automation_id,
            "amount": int(p.amount or 0),
            "tokens_purchased": int(p.tokens_purchased or 0),
            "gateway": p.gateway or "",
            "method": p.method,
            "transaction_id": p.transaction_id,
            "ref_id": p.ref_id,
            "status": p.status or "",
            "created_at": p.created_at,
        })
    return total, items

def get_monthly_expenses(db: Session, user_id: int, months: int = 6):
    # last N months including current month; sum successful payments only
    now = datetime.utcnow()
    rough_back = now.replace(day=1) - timedelta(days=32*(months-1))
    dialect = db.bind.dialect.name
    if dialect == "sqlite":
        month_expr = func.strftime("%Y-%m", Payment.created_at)
    else:
        month_expr = func.to_char(func.date_trunc("month", Payment.created_at), "YYYY-MM")
    q = (
        db.query(
            label("month", month_expr),
            func.coalesce(func.sum(Payment.amount), 0).label("amount")
        )
        .filter(Payment.user_id == user_id, Payment.created_at >= rough_back, Payment.status == "success")
        .group_by("month")
        .order_by("month")
    )
    rows = q.all()
    return [{ "month": r.month, "amount": int(r.amount or 0) } for r in rows]

def get_payment_receipt(db: Session, user_id: int, pid: int):
    p = db.query(Payment).filter(Payment.user_id == user_id, Payment.id == pid).first()
    return p
