from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import enum

class UserRole(str, enum.Enum):
    manager = "manager"
    technical_team = "technical_team"
    support_staff = "support_staff"
    customer = "customer"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.support_staff)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    twofa_enabled = Column(Boolean, nullable=False, default=False, server_default='0')
    twofa_secret = Column(String(64), nullable=True)
    
    # Relationships
    knowledge_entries = relationship("KnowledgeEntry", back_populates="client")
    tickets = relationship("Ticket", foreign_keys="Ticket.user_id", back_populates="user")
    ticket_messages = relationship("TicketMessage", back_populates="user")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user")
    kb_status_history = relationship("KBStatusHistory", back_populates="user")
    
    # Token adjustment relationships
    token_adjustments = relationship("TokenAdjustment", foreign_keys="TokenAdjustment.user_id", back_populates="user")
    admin_token_adjustments = relationship("TokenAdjustment", foreign_keys="TokenAdjustment.admin_id", back_populates="admin")
    
    # Session relationships
    sessions = relationship("Session", back_populates="user")
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges based on role"""
        return self.role in [UserRole.manager, UserRole.technical_team, UserRole.support_staff] 