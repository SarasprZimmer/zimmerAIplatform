from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class ConstructionEmail(Base):
    __tablename__ = "construction_emails"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
