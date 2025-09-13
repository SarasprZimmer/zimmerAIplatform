"""
Payment schemas for Zimmer AI Platform
"""

from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime

class CreatePaymentRequest(BaseModel):
    automation_id: int
    tokens: int
    payment_method: str = "zarinpal"
    discount_code: Optional[str] = None
    discount_percent: Optional[int] = None
    meta: Optional[Dict[str, Any]] = None
    
    @validator('tokens')
    def validate_tokens(cls, v):
        if v <= 0:
            raise ValueError("Tokens must be greater than 0")
        if v > 100000:
            raise ValueError("Tokens cannot exceed 100,000")
        return v
    
    @validator('payment_method')
    def validate_payment_method(cls, v):
        allowed_methods = ['zarinpal', 'paypal', 'stripe']
        if v not in allowed_methods:
            raise ValueError(f"Payment method must be one of: {allowed_methods}")
        return v

class VerifyPaymentRequest(BaseModel):
    transaction_id: str
    gateway_response: Dict[str, Any]
    
    @validator('transaction_id')
    def validate_transaction_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Transaction ID is required")
        return v.strip()

class PaymentResponse(BaseModel):
    id: int
    transaction_id: str
    automation_id: int
    amount: int
    tokens_purchased: int
    method: str
    gateway: str
    status: str
    created_at: datetime
    ref_id: Optional[str] = None
    discount_code: Optional[str] = None
    discount_percent: Optional[int] = None
    
    class Config:
        from_attributes = True

class PaymentHistoryResponse(BaseModel):
    payments: list[PaymentResponse]
    total: int
    limit: int
    offset: int
