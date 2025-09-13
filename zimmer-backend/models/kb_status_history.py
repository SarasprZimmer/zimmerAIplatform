from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class KBStatusHistory(Base):
    __tablename__ = "kb_status_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_automation_id = Column(Integer, ForeignKey("user_automations.id"), nullable=False)
    automation_id = Column(Integer, ForeignKey("automations.id"), nullable=False)
    kb_health = Column(String, nullable=False)  # "healthy", "warning", "problematic"
    backup_status = Column(Boolean, nullable=False)
    error_logs = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="kb_status_history")
    user_automation = relationship("UserAutomation", back_populates="kb_status_history")
    automation = relationship("Automation", back_populates="kb_status_history") 