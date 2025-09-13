from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class KnowledgeEntry(Base):
    __tablename__ = "knowledge_entries"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=False)
    answer = Column(Text, nullable=False)  # Long text field
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to User
    client = relationship("User", back_populates="knowledge_entries") 