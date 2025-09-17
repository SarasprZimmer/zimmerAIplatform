from pydantic import BaseModel, ConfigDict
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from models.automation import PricingType

class AutomationBase(BaseModel):
    name: str
    description: str
    pricing_type: PricingType
    price_per_token: float
    api_endpoint: Optional[str] = None
    api_base_url: Optional[str] = None
    api_provision_url: Optional[str] = None
    api_usage_url: Optional[str] = None
    api_kb_status_url: Optional[str] = None
    api_kb_reset_url: Optional[str] = None

class AutomationCreate(AutomationBase):
    pass

class AutomationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    pricing_type: Optional[PricingType] = None
    price_per_token: Optional[float] = None
    api_endpoint: Optional[str] = None
    api_base_url: Optional[str] = None
    api_provision_url: Optional[str] = None
    api_usage_url: Optional[str] = None
    api_kb_status_url: Optional[str] = None
    api_kb_reset_url: Optional[str] = None
    status: Optional[bool] = None

class AutomationResponse(AutomationBase):
    id: int
    status: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AutomationIntegrationResponse(BaseModel):
    id: int
    name: str
    api_base_url: Optional[str] = None
    api_provision_url: Optional[str] = None
    api_usage_url: Optional[str] = None
    api_kb_status_url: Optional[str] = None
    api_kb_reset_url: Optional[str] = None
    service_token_masked: Optional[str] = None
    has_service_token: bool = False

    model_config = ConfigDict(from_attributes=True)

class TokenRotationResponse(BaseModel):
    automation_id: int
    new_token: str
    masked_token: str
    rotated_at: datetime
    message: str = "Service token rotated successfully"

class ProvisionRequest(BaseModel):
    user_automation_id: int
    bot_token: Optional[str] = None

class ProvisionResponse(BaseModel):
    success: bool
    message: str
    provisioned_at: Optional[datetime] = None
    integration_status: Optional[str] = None

class UsageConsumeRequest(BaseModel):
    user_automation_id: int
    units: int
    usage_type: str
    meta: Optional[dict] = None

class UsageConsumeResponse(BaseModel):
    accepted: bool
    remaining_demo_tokens: int
    remaining_paid_tokens: int
    message: str 