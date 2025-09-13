from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import enum

class UsageStatus(str, enum.Enum):
    OK = "ok"
    FAIL = "fail"

class OpenAIKeyUsage(Base):
    __tablename__ = "openai_key_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    openai_key_id = Column(Integer, ForeignKey("openai_keys.id"), nullable=False)
    automation_id = Column(Integer, ForeignKey("automations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    model = Column(String(100), nullable=False)
    prompt_tokens = Column(Integer, nullable=False)
    completion_tokens = Column(Integer, nullable=False)
    total_tokens = Column(Integer, nullable=False)
    status = Column(Enum(UsageStatus), nullable=False)
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    openai_key = relationship("OpenAIKey", back_populates="usage_records")
    automation = relationship("Automation")
    user = relationship("User")
