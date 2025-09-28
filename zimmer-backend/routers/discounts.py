from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from utils.auth_dependency import get_current_user
from models.user import User
from schemas.discounts import DiscountValidateIn, DiscountValidateOut
from services.discounts import validate_code

router = APIRouter(prefix="/discounts", tags=["discounts"])

async def get_current_user_optional(db: Session = Depends(get_db)):
    """Get current user if authenticated, otherwise return None"""
    try:
        from utils.auth_dependency import get_current_user
        return await get_current_user()
    except:
        return None

@router.post("/validate", response_model=DiscountValidateOut)
async def validate(payload: DiscountValidateIn, db: Session = Depends(get_db), user=Depends(get_current_user_optional)):
    uid = user.id if user else None
    ok, reason, pack = validate_code(db, payload.code, payload.automation_id, uid, payload.amount)
    if not ok:
        return DiscountValidateOut(valid=False, reason=reason)
    dc, before, disc, after = pack
    return DiscountValidateOut(valid=True, code=dc.code, percent_off=dc.percent_off,
                               amount_before=before, amount_discount=disc, amount_after=after)
