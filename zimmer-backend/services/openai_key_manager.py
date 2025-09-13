from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from models.openai_key import OpenAIKey, OpenAIKeyStatus
from models.openai_key_usage import OpenAIKeyUsage, UsageStatus
from utils.crypto import decrypt_secret
from datetime import datetime, timedelta
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class OpenAIKeyManager:
    def __init__(self, db: Session):
        self.db = db
    
    def get_pool(self, automation_id: int) -> List[OpenAIKey]:
        """Get all active keys for an automation"""
        return self.db.query(OpenAIKey).filter(
            and_(
                OpenAIKey.automation_id == automation_id,
                OpenAIKey.status == OpenAIKeyStatus.ACTIVE
            )
        ).all()
    
    def select_key(self, automation_id: int) -> Optional[OpenAIKey]:
        """Select the best available key for an automation"""
        now = datetime.utcnow()
        
        # Get all active keys for this automation
        keys = self.get_pool(automation_id)
        if not keys:
            logger.warning(f"No active OpenAI keys found for automation {automation_id}")
            return None
        
        eligible_keys = []
        
        for key in keys:
            # Reset minute window if needed
            if (key.last_minute_window is None or 
                (now - key.last_minute_window) >= timedelta(minutes=1)):
                key.used_requests_minute = 0
                key.last_minute_window = now
                self.db.commit()
            
            # Check if key is eligible (not exceeding limits)
            is_eligible = True
            
            # Check RPM limit
            if key.rpm_limit and key.used_requests_minute >= key.rpm_limit:
                is_eligible = False
            
            # Check daily token limit
            if key.daily_token_limit and key.used_tokens_today >= key.daily_token_limit:
                # Mark as exhausted
                key.status = OpenAIKeyStatus.EXHAUSTED
                self.db.commit()
                is_eligible = False
            
            if is_eligible:
                eligible_keys.append(key)
        
        if not eligible_keys:
            logger.warning(f"No eligible OpenAI keys found for automation {automation_id}")
            return None
        
        # Select the best key based on priority:
        # 1. Lowest used_requests_minute
        # 2. Lowest used_tokens_today
        # 3. Least recently used
        selected_key = min(eligible_keys, key=lambda k: (
            k.used_requests_minute,
            k.used_tokens_today,
            k.last_used_at or datetime.min
        ))
        
        return selected_key
    
    def record_usage(self, key_id: int, tokens_used: int, ok: bool = True, 
                    error_code: Optional[str] = None, error_message: Optional[str] = None,
                    model: str = "unknown", prompt_tokens: int = 0, completion_tokens: int = 0,
                    automation_id: Optional[int] = None, user_id: Optional[int] = None) -> None:
        """Record usage for a key"""
        key = self.db.query(OpenAIKey).filter(OpenAIKey.id == key_id).first()
        if not key:
            logger.error(f"OpenAI key {key_id} not found for usage recording")
            return
        
        now = datetime.utcnow()
        
        # Update key usage
        key.used_requests_minute += 1
        key.used_tokens_today += tokens_used
        key.last_used_at = now
        
        # Check if daily limit exceeded
        if key.daily_token_limit and key.used_tokens_today >= key.daily_token_limit:
            key.status = OpenAIKeyStatus.EXHAUSTED
        
        # Create usage record
        usage_record = OpenAIKeyUsage(
            openai_key_id=key_id,
            automation_id=automation_id or key.automation_id,
            user_id=user_id,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=tokens_used,
            status=UsageStatus.OK if ok else UsageStatus.FAIL,
            error_code=error_code,
            error_message=error_message
        )
        
        self.db.add(usage_record)
        self.db.commit()
        
        logger.info(f"Recorded usage for key {key_id}: {tokens_used} tokens, status={'OK' if ok else 'FAIL'}")
    
    def handle_failure(self, key_id: int, error_code: Optional[str] = None) -> bool:
        """Handle key failure and return whether to retry with next key"""
        key = self.db.query(OpenAIKey).filter(OpenAIKey.id == key_id).first()
        if not key:
            logger.error(f"OpenAI key {key_id} not found for failure handling")
            return False
        
        key.failure_count += 1
        
        # Handle specific error codes
        if error_code in ["401", "403"]:
            # Authentication errors - disable the key
            key.status = OpenAIKeyStatus.DISABLED
            logger.warning(f"Disabling OpenAI key {key_id} due to auth error {error_code}")
            self.db.commit()
            return True  # Retry with next key
        
        elif error_code == "429":
            # Rate limit - temporary issue, keep key active but log
            logger.warning(f"Rate limit hit for OpenAI key {key_id}")
            self.db.commit()
            return True  # Retry with next key
        
        elif error_code in ["500", "502", "503", "504"]:
            # Server errors - temporary, retry
            logger.warning(f"Server error {error_code} for OpenAI key {key_id}")
            self.db.commit()
            return True  # Retry with next key
        
        else:
            # Other errors - log but keep key active
            logger.error(f"Error {error_code} for OpenAI key {key_id}")
            self.db.commit()
            return False  # Don't retry for unknown errors
    
    def reset_daily_usage(self) -> int:
        """Reset daily token usage for all keys (called by scheduler)"""
        result = self.db.query(OpenAIKey).update({
            OpenAIKey.used_tokens_today: 0
        })
        self.db.commit()
        logger.info(f"Reset daily usage for {result} OpenAI keys")
        return result
    
    def get_key_with_decrypted(self, key_id: int) -> Optional[tuple[OpenAIKey, str]]:
        """Get key with decrypted API key (for internal use only)"""
        key = self.db.query(OpenAIKey).filter(OpenAIKey.id == key_id).first()
        if not key:
            return None
        
        try:
            decrypted_key = decrypt_secret(key.key_encrypted)
            return key, decrypted_key
        except Exception as e:
            logger.error(f"Failed to decrypt key {key_id}: {e}")
            return None
