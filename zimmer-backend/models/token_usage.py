from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class TokenUsage(Base):
    __tablename__ = "token_usages"
    id = Column(Integer, primary_key=True, index=True)
    user_automation_id = Column(Integer, ForeignKey("user_automations.id"), nullable=False)
    tokens_used = Column(Integer, nullable=False)
    usage_type = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 