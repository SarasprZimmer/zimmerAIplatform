# Import Base first
from database import Base

# Import all models to ensure they're registered with SQLAlchemy Base
# Import order matters for relationships

# First, import models without relationships
from .user import User, UserRole
from .automation import Automation
from .user_automation import UserAutomation
from .payment import Payment
from .fallback_log import FallbackLog
from .token_usage import TokenUsage
from .knowledge import KnowledgeEntry
from .kb_template import KBTemplate
from .ticket import Ticket
from .ticket_message import TicketMessage
from .password_reset_token import PasswordResetToken
from .kb_status_history import KBStatusHistory
from .backup import BackupLog
from .openai_key import OpenAIKey, OpenAIKeyStatus
from .openai_key_usage import OpenAIKeyUsage, UsageStatus
from .token_adjustment import TokenAdjustment
from .session import Session
from .notification import Notification
from .email_verification import EmailVerificationToken
from .twofa import TwoFactorRecoveryCode
from .discount import DiscountCode, DiscountCodeAutomation, DiscountRedemption

# Export all models
__all__ = [
    'User',
    'UserRole',
    'Automation', 
    'UserAutomation',
    'Payment',
    'FallbackLog',
    'TokenUsage',
    'KnowledgeEntry',
    'KBTemplate',
    'Ticket',
    'TicketMessage',
    'PasswordResetToken',
    'KBStatusHistory',
    'BackupLog',
    'OpenAIKey',
    'OpenAIKeyStatus',
    'OpenAIKeyUsage',
    'UsageStatus',
    'TokenAdjustment',
    'Session',
    'Notification',
    'EmailVerificationToken',
    'TwoFactorRecoveryCode',
    'DiscountCode',
    'DiscountCodeAutomation',
    'DiscountRedemption'
] 