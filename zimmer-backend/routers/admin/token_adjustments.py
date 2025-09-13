import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from database import get_db
from utils.auth_dependency import get_current_admin_user
from models.user import User
from schemas.token_adjustment import (
    TokenAdjustmentCreate,
    TokenAdjustmentOut,
    TokenAdjustmentListResponse,
    TokenBalanceResponse
)
from services.token_adjust_service import apply_adjustment, list_adjustments, get_token_balance

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/adjust", response_model=TokenAdjustmentOut)
async def create_token_adjustment(
    payload: TokenAdjustmentCreate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a new token adjustment (Admin only)
    
    This endpoint allows administrators to manually adjust token balances
    for user automations. All adjustments are logged for audit purposes.
    """
    
    try:
        # Log the adjustment attempt
        logger.info(
            f"Token adjustment attempt by admin {current_admin.id}({current_admin.email}): "
            f"UserAutomation={payload.user_automation_id}, "
            f"Delta={payload.delta_tokens}, "
            f"Reason='{payload.reason}', "
            f"IdempotencyKey={payload.idempotency_key}"
        )
        
        # Apply the adjustment
        adjustment = apply_adjustment(db, current_admin, payload)
        
        # Return the created adjustment
        return adjustment
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(
            f"Unexpected error in token adjustment by admin {current_admin.id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="خطای داخلی در تنظیم توکن"
        )


@router.get("/adjustments", response_model=TokenAdjustmentListResponse)
async def get_token_adjustments(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    automation_id: Optional[int] = Query(None, description="Filter by automation ID"),
    admin_id: Optional[int] = Query(None, description="Filter by admin ID"),
    start_date: Optional[str] = Query(None, description="Filter by start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (ISO format)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    List token adjustments with filtering and pagination (Admin only)
    
    Returns a paginated list of all token adjustments with optional filtering.
    """
    
    try:
        # Get adjustments with filters
        result = list_adjustments(
            db=db,
            user_id=user_id,
            automation_id=automation_id,
            admin_id=admin_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size
        )
        
        # Convert to response format
        return TokenAdjustmentListResponse(
            total=result["total"],
            items=result["items"]
        )
        
    except Exception as e:
        logger.error(f"Error listing token adjustments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="خطا در دریافت لیست تنظیمات توکن"
        )


@router.get("/balance/{user_automation_id}", response_model=TokenBalanceResponse)
async def get_user_automation_balance(
    user_automation_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get current token balance for a specific user automation (Admin only)
    
    Returns the current token balance and related information.
    """
    
    try:
        # Get the balance
        balance = get_token_balance(db, user_automation_id)
        
        if not balance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="اتوماسیون کاربر یافت نشد"
            )
        
        return TokenBalanceResponse(**balance)
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error getting token balance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="خطا در دریافت موجودی توکن"
        )
