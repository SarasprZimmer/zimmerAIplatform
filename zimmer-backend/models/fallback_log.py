from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class FallbackLog(Base):
    __tablename__ = "fallback_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_automation_id = Column(Integer, ForeignKey("user_automations.id"), nullable=False)
    message = Column(String, nullable=False)
    error_type = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 