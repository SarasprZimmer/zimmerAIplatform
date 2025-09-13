from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

from database import Base

class PricingType(str, enum.Enum):
    token_per_session = 'token_per_session'
    token_per_step = 'token_per_step'
    flat_fee = 'flat_fee'

class Automation(Base):
    __tablename__ = 'automations'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String, nullable=False)
    pricing_type = Column(Enum(PricingType), nullable=False)
    price_per_token = Column(Float, nullable=False)
    status = Column(Boolean, default=True, nullable=False)
    api_endpoint = Column(String, nullable=True)
    api_base_url = Column(String, nullable=True)
    api_provision_url = Column(String, nullable=True)
    api_usage_url = Column(String, nullable=True)
    api_kb_status_url = Column(String, nullable=True)
    api_kb_reset_url = Column(String, nullable=True)
    service_token_hash = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Health check fields
    health_check_url = Column(String(500), nullable=True)
    health_status = Column(String(16), nullable=False, default="unknown", index=True)
    last_health_at = Column(DateTime(timezone=True), nullable=True)
    health_details = Column(JSON, nullable=True)
    is_listed = Column(Boolean, nullable=False, default=False, index=True)
    
    # Relationships
    kb_status_history = relationship("KBStatusHistory", back_populates="automation")
    kb_templates = relationship("KBTemplate", back_populates="automation")
    openai_keys = relationship("OpenAIKey", back_populates="automation") 