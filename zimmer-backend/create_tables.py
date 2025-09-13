#!/usr/bin/env python3
"""
Create database tables for Zimmer Platform
"""

from database import Base, engine
from models.user import User
from models.automation import Automation
from models.ticket import Ticket
from models.ticket_message import TicketMessage
from models.payment import Payment
from models.knowledge import KnowledgeEntry
from models.kb_template import KBTemplate
from models.kb_status_history import KBStatusHistory
from models.openai_key import OpenAIKey
from models.openai_key_usage import OpenAIKeyUsage
from models.password_reset_token import PasswordResetToken
from models.backup import BackupLog
from models.fallback_log import FallbackLog
from models.token_usage import TokenUsage
from models.user_automation import UserAutomation
from models.token_adjustment import TokenAdjustment
from models.session import Session
from models.notification import Notification
from models.discount import DiscountCode, DiscountCodeAutomation, DiscountRedemption
from models.twofa import TwoFactorRecoveryCode
from models.email_verification import EmailVerificationToken

def create_all_tables():
    """Create all database tables"""
    try:
        print("🔧 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Test the connection
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Try to query users table
        users = db.query(User).limit(1).all()
        print(f"✅ Users table accessible - Found {len(users)} users")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    create_all_tables()
