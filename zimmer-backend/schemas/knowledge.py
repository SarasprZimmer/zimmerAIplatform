from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime
from utils.sanitize import validate_string_field, validate_text_field

class KnowledgeCreate(BaseModel):
    client_id: int
    category: str
    answer: str

    @validator('category')
    def validate_category(cls, v):
        return validate_string_field(v, max_length=64)

    @validator('answer')
    def validate_answer(cls, v):
        return validate_text_field(v, max_length=20000)

class KnowledgeOut(BaseModel):
    id: int
    category: str
    answer: str
    created_at: datetime
    client_name: str

    class Config:
        from_attributes = True

class KnowledgeListResponse(BaseModel):
    total_count: int
    knowledge_entries: List[KnowledgeOut] 