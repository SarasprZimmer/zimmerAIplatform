from pydantic import ConfigDict
from pydantic import BaseModel, Field, conint
from typing import List, Optional
from datetime import datetime

class DiscountCodeCreateIn(BaseModel):
    code: str = Field(..., min_length=2, max_length=64)
    percent_off: conint(ge=0, le=100)
    active: bool = True
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    max_redemptions: Optional[int] = None
    per_user_limit: Optional[int] = None
    automation_ids: List[int] = []

class DiscountCodeOut(BaseModel):
    id: int
    code: str
    percent_off: int
    active: bool
    starts_at: Optional[datetime]
    ends_at: Optional[datetime]
    max_redemptions: Optional[int]
    per_user_limit: Optional[int]
    automation_ids: List[int]
    model_config = ConfigDict(from_attributes=True)

class DiscountValidateIn(BaseModel):
    code: str
    automation_id: int
    amount: int  # Rial, computed client-side for display (server will recompute in payment)

class DiscountValidateOut(BaseModel):
    valid: bool
    code: Optional[str] = None
    percent_off: Optional[int] = None
    amount_before: Optional[int] = None
    amount_discount: Optional[int] = None
    amount_after: Optional[int] = None
    reason: Optional[str] = None
