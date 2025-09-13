from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlalchemy.orm import Session
from typing import Optional
from utils.auth import get_current_user
from database import get_db
from schemas.billing_user import ActiveAutomationOut, PaymentListOut, MonthlyExpensesOut, PaymentReceiptOut
from services.billing_user import get_active_automations, get_user_payments, get_monthly_expenses, get_payment_receipt

router = APIRouter(prefix="/api/user", tags=["User Billing"])

@router.get("/automations/active", response_model=list[ActiveAutomationOut])
def active_automations(
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    return get_active_automations(db, user.id)

@router.get("/payments", response_model=PaymentListOut)
def payments(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    total, items = get_user_payments(db, user.id, limit=limit, offset=offset, order=order)
    return { "total": total, "items": items }

@router.get("/payments/summary", response_model=MonthlyExpensesOut)
def payments_summary(
    months: int = Query(6, ge=1, le=12),
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    points = get_monthly_expenses(db, user.id, months=months)
    return { "points": points }

@router.get("/payments/{payment_id}", response_model=PaymentReceiptOut)
def payment_receipt(
    payment_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    p = get_payment_receipt(db, user.id, payment_id)
    if not p:
        raise HTTPException(status_code=404, detail="payment_not_found")
    return {
        "id": p.id,
        "amount": int(p.amount or 0),
        "tokens_purchased": int(p.tokens_purchased or 0),
        "status": p.status or "",
        "gateway": p.gateway or "",
        "method": p.method,
        "transaction_id": p.transaction_id,
        "ref_id": p.ref_id,
        "automation_id": p.automation_id,
        "created_at": p.created_at,
    }
