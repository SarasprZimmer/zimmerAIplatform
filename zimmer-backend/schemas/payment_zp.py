from pydantic import ConfigDict
"""
Payment schemas for Zarinpal integration
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from utils.sanitize import validate_string_field


class PaymentInitRequest(BaseModel):
    """Request to initialize a payment"""
    automation_id: int = Field(..., description="ID of the automation to purchase")
    tokens: int = Field(..., ge=1, le=100000, description="Number of tokens to purchase")
    return_path: str = Field(..., description="Client route appended to PAYMENTS_RETURN_BASE")
    discount_code: Optional[str] = Field(None, description="Optional discount code to apply")

    @validator('return_path')
    def validate_return_path(cls, v):
        return validate_string_field(v, max_length=200)


class PaymentInitResponse(BaseModel):
    """Response after payment initialization"""
    payment_id: int = Field(..., description="ID of the created payment record")
    authority: str = Field(..., description="Zarinpal payment authority")
    redirect_url: str = Field(..., description="URL to redirect user for payment")
    amount: int = Field(..., description="Final amount after discount (in Rial)")


class PaymentVerifyResponse(BaseModel):
    """Response after payment verification"""
    payment_id: int = Field(..., description="ID of the payment record")
    status: str = Field(..., description="Payment status: succeeded, failed, canceled")
    ref_id: Optional[str] = Field(None, description="Zarinpal reference ID if successful")
    message: str = Field(..., description="Status message or error description")


class PaymentCallbackRequest(BaseModel):
    """Request parameters for payment callback"""
    payment_id: int = Field(..., description="ID of the payment record")
    Authority: str = Field(..., description="Zarinpal authority parameter")
    Status: str = Field(..., description="Zarinpal status: OK or NOK")

    @validator('Authority')
    def validate_authority(cls, v):
        return validate_string_field(v, max_length=255)

    @validator('Status')
    def validate_status(cls, v):
        return validate_string_field(v, max_length=10)


class PaymentOut(BaseModel):
    """Payment record output"""
    id: int
    amount: int
    tokens_purchased: int
    status: str
    discount_code: Optional[str] = None
    discount_percent: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)
