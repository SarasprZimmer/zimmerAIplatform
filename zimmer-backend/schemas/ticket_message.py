from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from utils.sanitize import validate_string_field, validate_text_field

class TicketMessageCreate(BaseModel):
    ticket_id: int
    message: str
    attachment_path: Optional[str] = None
    is_internal: bool = False

    @validator('message')
    def validate_message(cls, v):
        return validate_text_field(v, max_length=10000)

    @validator('attachment_path')
    def validate_attachment_path(cls, v):
        if v is None:
            return v
        return validate_string_field(v, max_length=500)

class TicketMessageUpdate(BaseModel):
    message: Optional[str] = None
    attachment_path: Optional[str] = None

    @validator('message')
    def validate_message(cls, v):
        if v is None:
            return v
        return validate_text_field(v, max_length=10000)

    @validator('attachment_path')
    def validate_attachment_path(cls, v):
        if v is None:
            return v
        return validate_string_field(v, max_length=500)

class TicketMessageOut(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    message: str
    attachment_path: Optional[str] = None
    is_internal: bool
    created_at: datetime
    user_name: Optional[str] = None
    user_email: Optional[str] = None

    class Config:
        from_attributes = True

class TicketMessageListResponse(BaseModel):
    total_count: int
    messages: List[TicketMessageOut] 