from pydantic import BaseModel, ConfigDict
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from models.ticket import TicketStatus, TicketImportance
from utils.sanitize import validate_string_field, validate_text_field

class TicketCreate(BaseModel):
    user_id: int
    subject: str
    message: str
    importance: TicketImportance = TicketImportance.MEDIUM
    attachment_path: Optional[str] = None

    @validator('subject')
    def validate_subject(cls, v):
        return validate_string_field(v, max_length=200)

    @validator('message')
    def validate_message(cls, v):
        return validate_text_field(v, max_length=10000)

    @validator('attachment_path')
    def validate_attachment_path(cls, v):
        if v is None:
            return v
        return validate_string_field(v, max_length=500)

class TicketUpdate(BaseModel):
    status: Optional[TicketStatus] = None
    assigned_to: Optional[int] = None
    message: Optional[str] = None

    @validator('message')
    def validate_message(cls, v):
        if v is None:
            return v
        return validate_text_field(v, max_length=10000)

class TicketOut(BaseModel):
    id: int
    user_id: int
    subject: str
    message: str
    status: TicketStatus
    importance: TicketImportance
    attachment_path: Optional[str] = None
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    user_name: Optional[str] = None
    assigned_admin_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class TicketListResponse(BaseModel):
    total_count: int
    tickets: List[TicketOut] 