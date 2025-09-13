from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.openai_key import OpenAIKeyStatus
from models.openai_key_usage import UsageStatus

class OpenAIKeyBase(BaseModel):
    alias: str = Field(..., min_length=1, max_length=100, description="Key alias (e.g., 'travel-key-1')")
    rpm_limit: Optional[int] = Field(None, ge=1, description="Requests per minute limit")
    daily_token_limit: Optional[int] = Field(None, ge=1, description="Daily token limit")
    status: Optional[OpenAIKeyStatus] = Field(OpenAIKeyStatus.ACTIVE, description="Key status")

class OpenAIKeyCreate(OpenAIKeyBase):
    automation_id: int = Field(..., description="Automation ID this key belongs to")
    api_key: str = Field(..., min_length=1, description="Plain OpenAI API key")

class OpenAIKeyUpdate(BaseModel):
    alias: Optional[str] = Field(None, min_length=1, max_length=100)
    api_key: Optional[str] = Field(None, min_length=1, description="Plain OpenAI API key for rotation")
    rpm_limit: Optional[int] = Field(None, ge=1)
    daily_token_limit: Optional[int] = Field(None, ge=1)
    status: Optional[OpenAIKeyStatus] = None

class OpenAIKeyOut(BaseModel):
    id: int
    automation_id: int
    alias: str
    status: OpenAIKeyStatus
    rpm_limit: Optional[int]
    daily_token_limit: Optional[int]
    used_requests_minute: int
    used_tokens_today: int
    last_used_at: Optional[datetime]
    failure_count: int
    created_at: datetime
    updated_at: datetime
    masked_key: str = Field(..., description="Masked API key for display")

    class Config:
        from_attributes = True

class OpenAIKeyUsageOut(BaseModel):
    id: int
    openai_key_id: int
    automation_id: int
    user_id: Optional[int]
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    status: UsageStatus
    error_code: Optional[str]
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class OpenAIKeyTestResponse(BaseModel):
    success: bool
    latency_ms: Optional[int] = None
    model: Optional[str] = None
    error_message: Optional[str] = None

class OpenAIKeyStatusUpdate(BaseModel):
    status: OpenAIKeyStatus
