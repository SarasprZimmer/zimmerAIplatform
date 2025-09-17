from pydantic import BaseModel, ConfigDict
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class FallbackLogResponse(BaseModel):
    id: int
    client_name: str
    automation_name: str
    message: str
    error_type: Optional[str]
    timestamp: datetime
    user_automation_id: int

    model_config = ConfigDict(from_attributes=True)

class FallbacksResponse(BaseModel):
    total_count: int
    fallbacks: List[FallbackLogResponse] 