from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class UserAutomation(Base):
    __tablename__ = "user_automations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    automation_id = Column(Integer, ForeignKey("automations.id"), nullable=False)
    telegram_bot_token = Column(String, nullable=True)
    tokens_remaining = Column(Integer, default=5)  # Default 5 tokens for testing
    demo_tokens = Column(Integer, default=5)
    is_demo_active = Column(Boolean, default=True)
    demo_expired = Column(Boolean, default=False)
    status = Column(String, default="active")
    provisioned_at = Column(DateTime(timezone=True), nullable=True)
    integration_status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Add unique constraint for bot token
    __table_args__ = (
        UniqueConstraint('telegram_bot_token', name='uq_telegram_bot_token'),
    )
    
    # Relationships
    kb_status_history = relationship("KBStatusHistory", back_populates="user_automation")
    token_adjustments = relationship("TokenAdjustment", back_populates="user_automation") 