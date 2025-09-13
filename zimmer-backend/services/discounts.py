from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from models.discount import DiscountCode, DiscountCodeAutomation, DiscountRedemption
from models.user import User

UTC = timezone.utc
def now_utc(): return datetime.now(UTC)

def normalize(code: str) -> str:
    return (code or "").strip().upper()

def is_code_active(dc: DiscountCode) -> bool:
    if not dc.active: return False
    n = now_utc()
    if dc.starts_at and n < dc.starts_at: return False
    if dc.ends_at and n > dc.ends_at: return False
    return True

def user_redemption_count(db: Session, dc_id: int, user_id: int) -> int:
    return db.query(DiscountRedemption).filter(
        DiscountRedemption.discount_id==dc_id,
        DiscountRedemption.user_id==user_id
    ).count()

def total_redemption_count(db: Session, dc_id: int) -> int:
    return db.query(DiscountRedemption).filter(
        DiscountRedemption.discount_id==dc_id
    ).count()

def code_applicable_to_automation(db: Session, dc: DiscountCode, automation_id: int) -> bool:
    # If no mappings, treat as "all automations"
    if not dc.automations:
        return True
    return db.query(DiscountCodeAutomation).filter_by(discount_id=dc.id, automation_id=automation_id).first() is not None

def compute_discount(percent_off: int, amount: int) -> tuple[int,int,int]:
    disc = (amount * percent_off) // 100
    new_amount = max(0, amount - disc)
    return amount, disc, new_amount

def validate_code(db: Session, code: str, automation_id: int, user_id: Optional[int], amount: int):
    codeN = normalize(code)
    dc = db.query(DiscountCode).filter(func.upper(DiscountCode.code) == codeN).first()
    if not dc: return False, "not_found", None
    if not is_code_active(dc): return False, "inactive_or_window", None
    if not code_applicable_to_automation(db, dc, automation_id): return False, "not_applicable", None
    if dc.max_redemptions is not None and total_redemption_count(db, dc.id) >= dc.max_redemptions:
        return False, "max_redeemed", None
    if user_id and dc.per_user_limit is not None and user_redemption_count(db, dc.id, user_id) >= dc.per_user_limit:
        return False, "per_user_limit", None
    before, disc, after = compute_discount(dc.percent_off, amount)
    return True, None, (dc, before, disc, after)

def record_redemption(db: Session, dc: DiscountCode, user_id: int, automation_id: int,
                      before: int, disc: int, after: int, payment_id: int | None):
    r = DiscountRedemption(
        discount_id=dc.id, user_id=user_id, automation_id=automation_id, payment_id=payment_id,
        code=dc.code, amount_before=before, amount_discount=disc, amount_after=after
    )
    db.add(r); db.commit(); db.refresh(r)
    return r
