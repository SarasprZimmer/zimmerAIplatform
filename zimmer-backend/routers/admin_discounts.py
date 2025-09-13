from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas.discounts import DiscountCodeCreateIn, DiscountCodeOut
from models.discount import DiscountCode, DiscountCodeAutomation
from utils.auth import get_current_user
from models.user import User, UserRole

router = APIRouter(prefix="/discounts", tags=["admin"])

def require_admin(current_user: User = Depends(get_current_user)):
    """Ensure current user is an admin"""
    if current_user.role != UserRole.manager:
        raise HTTPException(status_code=403, detail="Manager access required")
    return current_user

@router.get("", response_model=List[DiscountCodeOut])
def list_discounts(db: Session = Depends(get_db), _: str = Depends(require_admin)):
    items = db.query(DiscountCode).all()
    out = []
    for it in items:
        out.append({
            "id": it.id, "code": it.code, "percent_off": it.percent_off, "active": it.active,
            "starts_at": it.starts_at, "ends_at": it.ends_at, "max_redemptions": it.max_redemptions,
            "per_user_limit": it.per_user_limit, "automation_ids": [m.automation_id for m in it.automations],
        })
    return out

@router.post("", response_model=DiscountCodeOut)
def create_discount(payload: DiscountCodeCreateIn, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    code = payload.code.strip().upper()
    if db.query(DiscountCode).filter(DiscountCode.code==code).first():
        raise HTTPException(status_code=400, detail="code_exists")
    dc = DiscountCode(
        code=code, percent_off=payload.percent_off, active=payload.active,
        starts_at=payload.starts_at, ends_at=payload.ends_at,
        max_redemptions=payload.max_redemptions, per_user_limit=payload.per_user_limit
    )
    db.add(dc); db.commit(); db.refresh(dc)
    if payload.automation_ids:
        links = [DiscountCodeAutomation(discount_id=dc.id, automation_id=a) for a in payload.automation_ids]
        db.add_all(links); db.commit()
    return {
        "id": dc.id, "code": dc.code, "percent_off": dc.percent_off, "active": dc.active,
        "starts_at": dc.starts_at, "ends_at": dc.ends_at, "max_redemptions": dc.max_redemptions,
        "per_user_limit": dc.per_user_limit, "automation_ids": payload.automation_ids
    }

@router.put("/{id}", response_model=DiscountCodeOut)
def update_discount(id: int, payload: DiscountCodeCreateIn, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    dc = db.query(DiscountCode).get(id)
    if not dc: raise HTTPException(status_code=404, detail="not_found")
    code = payload.code.strip().upper()
    # ensure unique code
    other = db.query(DiscountCode).filter(DiscountCode.code==code, DiscountCode.id!=id).first()
    if other: raise HTTPException(status_code=400, detail="code_exists")
    dc.code = code
    dc.percent_off = payload.percent_off
    dc.active = payload.active
    dc.starts_at = payload.starts_at
    dc.ends_at = payload.ends_at
    dc.max_redemptions = payload.max_redemptions
    dc.per_user_limit = payload.per_user_limit
    # remap automations
    db.query(DiscountCodeAutomation).filter_by(discount_id=dc.id).delete()
    if payload.automation_ids:
        links = [DiscountCodeAutomation(discount_id=dc.id, automation_id=a) for a in payload.automation_ids]
        db.add_all(links)
    db.commit(); db.refresh(dc)
    return {
        "id": dc.id, "code": dc.code, "percent_off": dc.percent_off, "active": dc.active,
        "starts_at": dc.starts_at, "ends_at": dc.ends_at, "max_redemptions": dc.max_redemptions,
        "per_user_limit": dc.per_user_limit, "automation_ids": payload.automation_ids
    }

@router.get("/{id}/redemptions")
def list_redemptions(id: int, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    from models.discount import DiscountRedemption
    rows = db.query(DiscountRedemption).filter_by(discount_id=id).order_by(DiscountRedemption.created_at.desc()).all()
    return [{
        "id": r.id, "user_id": r.user_id, "automation_id": r.automation_id,
        "payment_id": r.payment_id, "code": r.code,
        "amount_before": r.amount_before, "amount_discount": r.amount_discount, "amount_after": r.amount_after,
        "created_at": r.created_at,
    } for r in rows]
