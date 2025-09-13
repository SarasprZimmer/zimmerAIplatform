from sqlalchemy import Column, Integer, String, Text, BigInteger, DateTime, ForeignKey, Enum, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import enum

class OpenAIKeyStatus(str, enum.Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    EXHAUSTED = "exhausted"
    ERROR = "error"

class OpenAIKey(Base):
    __tablename__ = "openai_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    automation_id = Column(Integer, ForeignKey("automations.id"), nullable=False)
    alias = Column(String(100), nullable=False)
    key_encrypted = Column(Text, nullable=False)
    status = Column(Enum(OpenAIKeyStatus), default=OpenAIKeyStatus.ACTIVE, nullable=False)
    rpm_limit = Column(Integer, nullable=True)  # requests per minute (soft)
    daily_token_limit = Column(BigInteger, nullable=True)
    used_requests_minute = Column(Integer, default=0)
    used_tokens_today = Column(BigInteger, default=0)
    last_minute_window = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    failure_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    automation = relationship("Automation", back_populates="openai_keys")
    usage_records = relationship("OpenAIKeyUsage", back_populates="openai_key")
    
    # Indexes
    __table_args__ = (
        Index('idx_openai_keys_automation_status', 'automation_id', 'status'),
    )
