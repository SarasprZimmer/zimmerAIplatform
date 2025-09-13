from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    automation_id = Column(Integer, ForeignKey("automations.id"), nullable=False)
    amount = Column(Integer, nullable=False)  # Amount in Rial (integer)
    tokens_purchased = Column(Integer, nullable=False)
    method = Column(String, nullable=False)
    gateway = Column(String, default="zarinpal", nullable=False)  # Payment gateway
    transaction_id = Column(String, unique=True, nullable=False)
    authority = Column(Text, nullable=True, index=True)  # Zarinpal authority
    ref_id = Column(Text, nullable=True)  # Zarinpal reference ID
    status = Column(String, default="pending")  # pending, succeeded, failed, canceled
    discount_code = Column(String(64), nullable=True)
    discount_percent = Column(Integer, nullable=True)
    meta = Column(Text, nullable=True)  # JSON string for additional data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    token_adjustments = relationship("TokenAdjustment", back_populates="related_payment") 