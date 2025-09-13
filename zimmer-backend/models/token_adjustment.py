from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class TokenAdjustment(Base):
    """Model for tracking manual token adjustments by administrators"""
    __tablename__ = "token_adjustments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user_automation_id = Column(Integer, ForeignKey("user_automations.id"), nullable=False, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    delta_tokens = Column(Integer, nullable=False)  # positive=add, negative=deduct
    reason = Column(String(255), nullable=False)  # short reason, e.g. 'payment_correction', 'promo', 'support_fix'
    note = Column(Text, nullable=True)  # free-form Persian explanation
    related_payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True, index=True)
    idempotency_key = Column(String(64), nullable=True, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="token_adjustments")
    admin = relationship("User", foreign_keys=[admin_id], back_populates="admin_token_adjustments")
    user_automation = relationship("UserAutomation", back_populates="token_adjustments")
    related_payment = relationship("Payment", back_populates="token_adjustments")

    # Composite index for efficient querying
    __table_args__ = (
        Index('idx_user_automation_created', 'user_id', 'user_automation_id', 'created_at'),
        UniqueConstraint('idempotency_key', name='uq_idempotency_key'),
    )

    def __repr__(self):
        return f"<TokenAdjustment(id={self.id}, user_id={self.user_id}, delta={self.delta_tokens}, reason='{self.reason}')>"
