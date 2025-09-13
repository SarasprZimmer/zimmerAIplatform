from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, func
from sqlalchemy.orm import relationship
from database import Base

class DiscountCode(Base):
    __tablename__ = "discount_codes"
    id = Column(Integer, primary_key=True)
    code = Column(String(64), nullable=False, unique=True, index=True)  # store uppercase
    percent_off = Column(Integer, nullable=False)  # 0..100
    active = Column(Boolean, nullable=False, default=True)
    starts_at = Column(DateTime(timezone=True), nullable=True)
    ends_at = Column(DateTime(timezone=True), nullable=True)
    max_redemptions = Column(Integer, nullable=True)     # total global limit
    per_user_limit = Column(Integer, nullable=True)      # per user limit
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # many-to-many via join
    automations = relationship("DiscountCodeAutomation", back_populates="discount", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("percent_off >= 0 AND percent_off <= 100", name="ck_discount_percent_range"),
    )

class DiscountCodeAutomation(Base):
    __tablename__ = "discount_code_automations"
    id = Column(Integer, primary_key=True)
    discount_id = Column(Integer, ForeignKey("discount_codes.id", ondelete="CASCADE"), nullable=False, index=True)
    automation_id = Column(Integer, ForeignKey("automations.id", ondelete="CASCADE"), nullable=False, index=True)
    discount = relationship("DiscountCode", back_populates="automations")

    __table_args__ = (UniqueConstraint("discount_id", "automation_id", name="uq_discount_automation"),)

class DiscountRedemption(Base):
    __tablename__ = "discount_redemptions"
    id = Column(Integer, primary_key=True)
    discount_id = Column(Integer, ForeignKey("discount_codes.id", ondelete="SET NULL"), index=True, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    automation_id = Column(Integer, ForeignKey("automations.id", ondelete="SET NULL"), index=True, nullable=True)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="SET NULL"), index=True, nullable=True)
    code = Column(String(64), nullable=False)  # denormalized for audit
    amount_before = Column(Integer, nullable=False)   # Rial
    amount_discount = Column(Integer, nullable=False) # Rial
    amount_after = Column(Integer, nullable=False)    # Rial
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
