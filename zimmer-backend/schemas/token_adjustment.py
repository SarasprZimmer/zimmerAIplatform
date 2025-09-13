from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TokenAdjustmentCreate(BaseModel):
    """Schema for creating a new token adjustment"""
    user_automation_id: int = Field(..., description="ID of the user automation to adjust")
    delta_tokens: int = Field(..., description="Token adjustment amount (positive=add, negative=deduct)")
    reason: str = Field(..., max_length=255, description="Short reason for adjustment")
    note: Optional[str] = Field(None, description="Free-form Persian explanation")
    related_payment_id: Optional[int] = Field(None, description="Related payment ID if applicable")
    idempotency_key: Optional[str] = Field(None, max_length=64, description="Idempotency key for duplicate prevention")


class TokenAdjustmentOut(BaseModel):
    """Schema for token adjustment output"""
    id: int
    user_id: int
    user_automation_id: int
    admin_id: int
    delta_tokens: int
    reason: str
    note: Optional[str]
    related_payment_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class TokenAdjustmentListResponse(BaseModel):
    """Schema for paginated list of token adjustments"""
    total: int
    items: list[TokenAdjustmentOut]


class TokenBalanceResponse(BaseModel):
    """Schema for user automation token balance"""
    user_automation_id: int
    tokens_remaining: int
    user_id: int
    automation_id: int
