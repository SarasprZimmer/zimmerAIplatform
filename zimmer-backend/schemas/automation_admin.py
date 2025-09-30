from pydantic import BaseModel, Field, validator
from typing import Optional
from models.automation import PricingType

class AutomationCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Automation name")
    description: str = Field(..., min_length=1, description="Automation description")
    price_per_token: float = Field(..., gt=0, description="Price per token")
    pricing_type: PricingType = Field(..., description="Pricing type")
    status: bool = Field(default=True, description="Automation status")
    api_base_url: Optional[str] = Field(None, description="Base API URL")
    api_provision_url: Optional[str] = Field(None, description="Provision API URL")
    api_usage_url: Optional[str] = Field(None, description="Usage API URL")
    api_kb_status_url: Optional[str] = Field(None, description="KB Status API URL")
    api_kb_reset_url: Optional[str] = Field(None, description="KB Reset API URL")
    health_check_url: Optional[str] = Field(None, description="Health check URL")

    @validator('api_base_url', 'api_provision_url', 'api_usage_url', 'api_kb_status_url', 'api_kb_reset_url', 'health_check_url')
    def validate_urls(cls, v):
        if v is not None and v.strip() == "":
            return None
        return v

class AutomationUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Automation name")
    description: Optional[str] = Field(None, min_length=1, description="Automation description")
    price_per_token: Optional[float] = Field(None, gt=0, description="Price per token")
    pricing_type: Optional[PricingType] = Field(None, description="Pricing type")
    status: Optional[bool] = Field(None, description="Automation status")
    api_base_url: Optional[str] = Field(None, description="Base API URL")
    api_provision_url: Optional[str] = Field(None, description="Provision API URL")
    api_usage_url: Optional[str] = Field(None, description="Usage API URL")
    api_kb_status_url: Optional[str] = Field(None, description="KB Status API URL")
    api_kb_reset_url: Optional[str] = Field(None, description="KB Reset API URL")
    health_check_url: Optional[str] = Field(None, description="Health check URL")

    @validator('api_base_url', 'api_provision_url', 'api_usage_url', 'api_kb_status_url', 'api_kb_reset_url', 'health_check_url')
    def validate_urls(cls, v):
        if v is not None and v.strip() == "":
            return None
        return v

class AutomationResponse(BaseModel):
    id: int
    name: str
    description: str
    price_per_token: float
    pricing_type: PricingType
    status: bool
    api_base_url: Optional[str]
    api_provision_url: Optional[str]
    api_usage_url: Optional[str]
    api_kb_status_url: Optional[str]
    api_kb_reset_url: Optional[str]
    has_service_token: bool
    service_token_masked: Optional[str]
    health_check_url: Optional[str]
    health_status: str
    last_health_at: Optional[str]
    is_listed: bool
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True
