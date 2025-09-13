from sqlalchemy.orm import Session
from models.user_automation import UserAutomation
from models.token_usage import TokenUsage
from typing import Dict, Any, Optional

def deduct_tokens(db: Session, user_automation_id: int, amount: int = 1, usage_type: str = "message", meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Deduct tokens from a user's automation. Prioritize demo tokens if available.
    Args:
        db (Session): SQLAlchemy DB session
        user_automation_id (int): UserAutomation record ID
        amount (int): Number of tokens to deduct (default 1)
    Returns:
        Dict[str, Any]: Result with success status and message
    """
    ua = db.query(UserAutomation).filter(UserAutomation.id == user_automation_id).first()
    if not ua:
        return {"success": False, "message": "User automation not found"}
    
    # Check if demo is active and has tokens
    if ua.is_demo_active and ua.demo_tokens > 0:
        if ua.demo_tokens >= amount:
            ua.demo_tokens -= amount
            
            # If demo tokens are exhausted, mark demo as expired
            if ua.demo_tokens == 0:
                ua.is_demo_active = False
                ua.demo_expired = True
            
            usage = TokenUsage(
                user_automation_id=user_automation_id,
                tokens_used=amount,
                usage_type=usage_type,
                description=f"Used {amount} demo token(s) for {usage_type}"
            )
            db.add(usage)
            db.commit()
            return {"success": True, "message": "demo mode used", "demo_tokens_remaining": ua.demo_tokens}
        else:
            return {"success": False, "message": "Insufficient demo tokens"}
    
    # Check if demo has expired and no paid tokens
    if ua.demo_expired and (ua.tokens_remaining is None or ua.tokens_remaining <= 0):
        return {"success": False, "message": "دوره آزمایشی شما به پایان رسیده است. لطفا بسته توکن خریداری کنید."}
    
    # Fall back to regular token deduction
    if ua.tokens_remaining is None or ua.tokens_remaining < amount:
        return {"success": False, "message": "Insufficient tokens"}
    
    ua.tokens_remaining -= amount
    usage = TokenUsage(
        user_automation_id=user_automation_id,
        tokens_used=amount,
        usage_type=usage_type,
        description=f"Deducted {amount} token(s) for {usage_type}"
    )
    db.add(usage)
    db.commit()
    return {"success": True, "message": "paid tokens used", "tokens_remaining": ua.tokens_remaining} 