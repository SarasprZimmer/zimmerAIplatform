import os
import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.token_adjustment import TokenAdjustment
from models.user_automation import UserAutomation
from models.user import User
from schemas.token_adjustment import TokenAdjustmentCreate
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


def apply_adjustment(db: Session, admin: User, payload: TokenAdjustmentCreate) -> TokenAdjustment:
    """
    Apply a token adjustment with full safety checks and audit logging.
    
    Args:
        db: Database session
        admin: Admin user performing the adjustment
        payload: Adjustment details
        
    Returns:
        TokenAdjustment: Created adjustment record
        
    Raises:
        HTTPException: For validation errors or insufficient tokens
    """
    
    # Validate delta_tokens is not zero
    if payload.delta_tokens == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="مقدار تغییر توکن نمی‌تواند صفر باشد"
        )
    
    # Check idempotency if key provided
    if payload.idempotency_key:
        existing = db.query(TokenAdjustment).filter(
            TokenAdjustment.idempotency_key == payload.idempotency_key
        ).first()
        if existing:
            logger.info(f"Idempotency key {payload.idempotency_key} already used, returning existing adjustment {existing.id}")
            return existing
    
    # Load UserAutomation with FOR UPDATE to prevent race conditions
    user_automation = db.query(UserAutomation).filter(
        UserAutomation.id == payload.user_automation_id
    ).with_for_update().first()
    
    if not user_automation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="اتوماسیون کاربر یافت نشد"
        )
    
    # Calculate new balance
    new_balance = user_automation.tokens_remaining + payload.delta_tokens
    
    # Check if negative balance is allowed
    allow_negative = os.getenv("ALLOW_NEGATIVE_TOKENS", "false").lower() == "true"
    
    if new_balance < 0 and not allow_negative:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="موجودی توکن نمی‌تواند منفی شود"
        )
    
    # Update user automation token balance
    user_automation.tokens_remaining = new_balance
    
    # Create adjustment record
    adjustment = TokenAdjustment(
        user_id=user_automation.user_id,
        user_automation_id=payload.user_automation_id,
        admin_id=admin.id,
        delta_tokens=payload.delta_tokens,
        reason=payload.reason,
        note=payload.note,
        related_payment_id=payload.related_payment_id,
        idempotency_key=payload.idempotency_key
    )
    
    # Add and commit
    db.add(adjustment)
    db.commit()
    db.refresh(adjustment)
    
    # Log the adjustment for audit
    logger.info(
        f"Token adjustment applied: ID={adjustment.id}, "
        f"Admin={admin.id}({admin.email}), "
        f"User={user_automation.user_id}, "
        f"Automation={user_automation.automation_id}, "
        f"Delta={payload.delta_tokens}, "
        f"NewBalance={new_balance}, "
        f"Reason='{payload.reason}', "
        f"IdempotencyKey={payload.idempotency_key}"
    )
    
    return adjustment


def list_adjustments(
    db: Session,
    user_id: Optional[int] = None,
    user_automation_id: Optional[int] = None,
    automation_id: Optional[int] = None,
    admin_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
) -> Dict[str, Any]:
    """
    List token adjustments with filtering and pagination.
    
    Args:
        db: Database session
        user_id: Filter by user ID
        user_automation_id: Filter by user automation ID
        automation_id: Filter by automation ID
        admin_id: Filter by admin ID
        start_date: Filter by start date (ISO format)
        end_date: Filter by end date (ISO format)
        page: Page number (1-based)
        page_size: Items per page
        
    Returns:
        Dict with total count and items
    """
    
    # Build base query
    query = db.query(TokenAdjustment)
    
    # Apply filters
    if user_id:
        query = query.filter(TokenAdjustment.user_id == user_id)
    
    if user_automation_id:
        query = query.filter(TokenAdjustment.user_automation_id == user_automation_id)
    
    if admin_id:
        query = query.filter(TokenAdjustment.admin_id == admin_id)
    
    if start_date:
        query = query.filter(TokenAdjustment.created_at >= start_date)
    
    if end_date:
        query = query.filter(TokenAdjustment.created_at <= end_date)
    
    # Filter by automation_id through user_automation relationship
    if automation_id:
        query = query.join(UserAutomation).filter(UserAutomation.automation_id == automation_id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    query = query.order_by(TokenAdjustment.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    # Execute query
    items = query.all()
    
    return {
        "total": total,
        "items": items,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


def get_token_balance(db: Session, user_automation_id: int) -> Optional[Dict[str, Any]]:
    """
    Get current token balance for a user automation.
    
    Args:
        db: Database session
        user_automation_id: ID of the user automation
        
    Returns:
        Dict with balance information or None if not found
    """
    
    user_automation = db.query(UserAutomation).filter(
        UserAutomation.id == user_automation_id
    ).first()
    
    if not user_automation:
        return None
    
    return {
        "user_automation_id": user_automation.id,
        "tokens_remaining": user_automation.tokens_remaining,
        "user_id": user_automation.user_id,
        "automation_id": user_automation.automation_id
    }
