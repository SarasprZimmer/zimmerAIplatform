from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

class NotificationOut(BaseModel):
    id: int
    type: str
    title: str
    body: Optional[str] = None
    data: Optional[Any] = None
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MarkReadIn(BaseModel):
    ids: List[int] = Field(default_factory=list)
