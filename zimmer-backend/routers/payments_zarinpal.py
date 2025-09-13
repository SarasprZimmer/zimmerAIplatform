"""
Zarinpal payment router
"""
import json
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import select
from database import get_db
from utils.auth import get_current_user
from models.user import User
from models.payment import Payment
from models.automation import Automation
from models.user_automation import UserAutomation
from models.discount import DiscountCode, DiscountRedemption
from services.twofa import now_utc
from schemas.payment_zp import (
    PaymentInitRequest, 
    PaymentInitResponse, 
    PaymentVerifyResponse,
    PaymentCallbackRequest
)
from services.pricing import compute_amount_rial, validate_token_range
from utils.zarinpal import ZarinpalClient, PaymentMode
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Import discount service
from services.discounts import validate_code, record_redemption

# Get configuration from environment
PAYMENTS_MODE = os.getenv("PAYMENTS_MODE", "mock")
ZARRINPAL_MERCHANT_ID = os.getenv("ZARRINPAL_MERCHANT_ID", "test-merchant-id")
ZARRINPAL_BASE = os.getenv("ZARRINPAL_BASE", "https://sandbox.zarinpal.com/pg/rest/WebGate")
PAYMENTS_RETURN_BASE = os.getenv("PAYMENTS_RETURN_BASE", "https://userpanel.zimmerai.com/payment/return")

# Initialize Zarinpal client
zarinpal_client = ZarinpalClient(
    merchant_id=ZARRINPAL_MERCHANT_ID,
    base_url=ZARRINPAL_BASE,
    mode=PaymentMode(PAYMENTS_MODE)
)


@router.post("/zarinpal/init", response_model=PaymentInitResponse)
async def init_payment(
    request: PaymentInitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_obj: Request = None
):
    """
    Initialize a payment for automation tokens
    """
    try:
        # Validate token range
        if not validate_token_range(request.tokens):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token amount. Must be between 1 and 100,000."
            )
        
        # Get automation and validate it's active and healthy
        automation = db.query(Automation).filter(
            Automation.id == request.automation_id,
            Automation.status == True
        ).first()
        
        if not automation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation not found or inactive"
            )
        
        # Check health gate
        if not automation.is_listed or automation.health_status != "healthy":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Automation is currently unavailable for purchase"
            )
        
        # Compute amount in Rial
        try:
            amount_rial = compute_amount_rial(automation, request.tokens)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Apply discount if provided
        pending_redemption_id = None
        if getattr(request, "discount_code", None):
            ok, reason, pack = validate_code(db, request.discount_code, request.automation_id, current_user.id, amount_rial)
            if not ok:
                raise HTTPException(status_code=400, detail=f"invalid_discount:{reason}")
            dc, before, disc, after = pack
            # create a pending redemption linked later to payment (payment_id set on verify)
            red = record_redemption(db, dc, current_user.id, request.automation_id, before, disc, after, payment_id=None)
            amount_rial = after
            pending_redemption_id = red.id
        
        # 100% discount: amount becomes 0 → skip gateway, mark as paid now
        if amount_rial == 0:
            payment = Payment(
                user_id=current_user.id,
                automation_id=request.automation_id,
                amount=0,
                tokens_purchased=request.tokens,
                method="discount",
                gateway="none",
                transaction_id=f"DISCOUNT-{current_user.id}-{automation.id}-{request.tokens}",
                status="succeeded"
            )
            db.add(payment); db.commit(); db.refresh(payment)
            
            # attach redemption to payment if existed
            if pending_redemption_id:
                red = db.query(DiscountRedemption).get(pending_redemption_id)
                if red:
                    red.payment_id = payment.id
                    db.commit()
            
            # credit tokens immediately
            await _credit_tokens_to_user(db, current_user.id, request.automation_id, request.tokens)
            return PaymentInitResponse(
                payment_id=payment.id,
                authority="discount",
                redirect_url="",
                amount=0
            )
        
        # Create payment record for normal payments
        payment = Payment(
            user_id=current_user.id,
            automation_id=request.automation_id,
            amount=amount_rial,
            tokens_purchased=request.tokens,
            method="zarinpal",
            gateway="zarinpal",
            transaction_id=f"ZP-{current_user.id}-{automation.id}-{request.tokens}",
            status="pending"
        )
        
        db.add(payment)
        db.flush()  # Get the ID without committing
        
        # Build callback URL
        callback_url = f"{PAYMENTS_RETURN_BASE}{request.return_path}?payment_id={payment.id}"
        
        # Request payment from Zarinpal
        payment_response = await zarinpal_client.request_payment(
            amount_rial=amount_rial,
            description=f"Zimmer - {automation.name} ({request.tokens} tokens)",
            callback_url=callback_url,
            email=current_user.email,
            mobile=getattr(current_user, 'phone_number', None)
        )
        
        # Save authority and commit
        payment.authority = payment_response["authority"]
        db.commit()
        
        # Log the payment initiation
        logger.info(
            f"Payment initiated: user_id={current_user.id}, "
            f"automation_id={automation.id}, tokens={request.tokens}, "
            f"amount_rial={amount_rial}, authority={payment.authority}"
        )
        
        return PaymentInitResponse(
            payment_id=payment.id,
            authority=payment.authority,
            redirect_url=payment_response["url"],
            amount=amount_rial
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment initiation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate payment"
        )


@router.get("/zarinpal/callback", response_model=PaymentVerifyResponse)
async def payment_callback(
    payment_id: int = Query(..., description="Payment ID"),
    Authority: str = Query(..., description="Zarinpal authority"),
    Status: str = Query(..., description="Zarinpal status: OK or NOK"),
    db: Session = Depends(get_db)
):
    """
    Handle payment callback from Zarinpal
    """
    try:
        # Get payment record with row lock to prevent race conditions
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        # Check if payment is already processed (idempotent)
        if payment.status in ["succeeded", "failed", "canceled"]:
            logger.info(
                f"Payment {payment_id} already processed with status {payment.status}"
            )
            return PaymentVerifyResponse(
                payment_id=payment.id,
                status=payment.status,
                ref_id=payment.ref_id,
                message=f"Payment already {payment.status}"
            )
        
        # Handle non-OK status
        if Status != "OK":
            payment.status = "canceled"
            payment.meta = json.dumps({
                "callback_status": Status,
                "authority": Authority,
                "error": "User canceled or payment failed"
            })
            db.commit()
            
            logger.info(f"Payment {payment_id} canceled with status {Status}")
            return PaymentVerifyResponse(
                payment_id=payment.id,
                status="canceled",
                ref_id=None,
                message="Payment was canceled or failed"
            )
        
        # Verify payment with Zarinpal
        verification_result = await zarinpal_client.verify_payment(
            authority=Authority,
            amount_rial=payment.amount
        )
        
        if verification_result["ok"]:
            # Payment successful
            payment.status = "succeeded"
            payment.ref_id = verification_result["ref_id"]
            payment.meta = json.dumps({
                "callback_status": Status,
                "authority": Authority,
                "verification_code": verification_result["code"],
                "verification_message": verification_result["message"]
            })
            
            # If there is a DiscountRedemption without payment_id for this user/automation/amount_after == payment.amount -> attach
            red = db.query(DiscountRedemption).filter(
                DiscountRedemption.user_id==payment.user_id,
                DiscountRedemption.payment_id.is_(None)
            ).order_by(DiscountRedemption.created_at.desc()).first()
            if red:
                red.payment_id = payment.id
                db.commit()
            
            # Credit tokens to user
            await _credit_tokens_to_user(
                db=db,
                user_id=payment.user_id,
                automation_id=payment.automation_id,
                tokens=payment.tokens_purchased
            )
            
            db.commit()
            
            logger.info(
                f"Payment {payment_id} succeeded: ref_id={verification_result['ref_id']}, "
                f"tokens_credited={payment.tokens_purchased}"
            )
            
            return PaymentVerifyResponse(
                payment_id=payment.id,
                status="succeeded",
                ref_id=verification_result["ref_id"],
                message="Payment completed successfully"
            )
        else:
            # Payment verification failed
            payment.status = "failed"
            payment.meta = json.dumps({
                "callback_status": Status,
                "authority": Authority,
                "verification_code": verification_result["code"],
                "verification_message": verification_result["message"]
            })
            db.commit()
            
            logger.warning(
                f"Payment {payment_id} verification failed: {verification_result['message']}"
            )
            
            return PaymentVerifyResponse(
                payment_id=payment.id,
                status="failed",
                ref_id=None,
                message=verification_result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment callback processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process payment callback"
        )


async def _credit_tokens_to_user(
    db: Session, 
    user_id: int, 
    automation_id: int, 
    tokens: int
):
    """
    Credit tokens to user's automation account
    """
    try:
        # Find existing user automation or create new one
        user_automation = db.query(UserAutomation).filter(
            UserAutomation.user_id == user_id,
            UserAutomation.automation_id == automation_id
        ).first()
        
        if user_automation:
            # Update existing record
            user_automation.tokens_remaining += tokens
            user_automation.status = "active"
        else:
            # Create new record
            user_automation = UserAutomation(
                user_id=user_id,
                automation_id=automation_id,
                tokens_remaining=tokens,
                demo_tokens=5,  # Keep demo tokens
                is_demo_active=True,
                status="active"
            )
            db.add(user_automation)
        
        logger.info(
            f"Credited {tokens} tokens to user {user_id} "
            f"for automation {automation_id}"
        )
        
    except Exception as e:
        logger.error(f"Failed to credit tokens: {str(e)}")
        raise Exception(f"Token crediting failed: {str(e)}")
