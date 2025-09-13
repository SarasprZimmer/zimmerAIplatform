from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class KBTemplateBase(BaseModel):
    automation_id: int
    category: Optional[str] = None
    question: str
    answer: str

class KBTemplateCreate(KBTemplateBase):
    pass

class KBTemplateUpdate(BaseModel):
    automation_id: Optional[int] = None
    category: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None

class KBTemplateResponse(KBTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime
    automation_name: str

    model_config = ConfigDict(from_attributes=True)

class KBTemplateListResponse(BaseModel):
    total_count: int
    templates: List[KBTemplateResponse] 