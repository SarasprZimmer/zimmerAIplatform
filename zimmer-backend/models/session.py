from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class Session(Base):
    """Model for managing user sessions and refresh tokens"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    refresh_token_hash = Column(Text, nullable=False, index=True)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(Text, nullable=True)
    last_used_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    # Composite indexes for efficient querying
    __table_args__ = (
        Index('idx_user_active_sessions', 'user_id', 'revoked_at'),
        Index('idx_session_expiry', 'expires_at', 'revoked_at'),
    )
    
    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"
    
    @property
    def is_active(self) -> bool:
        """Check if session is active (not revoked and not expired)"""
        from datetime import datetime
        now = datetime.utcnow()
        return (
            self.revoked_at is None and 
            self.expires_at > now
        )
    
    @property
    def is_idle_timeout(self, idle_timeout_minutes: int = 120) -> bool:
        """Check if session has exceeded idle timeout"""
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        idle_threshold = now - timedelta(minutes=idle_timeout_minutes)
        return self.last_used_at < idle_threshold
