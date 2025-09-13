"""
Payment endpoints for Zimmer AI Platform
Handles payment creation, verification, and management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone
import uuid
import hashlib

from database import get_db
from models.user import User
from models.payment import Payment
from models.automation import Automation
from utils.auth import get_current_user
from schemas.payment import CreatePaymentRequest, VerifyPaymentRequest, PaymentResponse

router = APIRouter(prefix="/api/payments", tags=["payments"])

@router.post("/create")
async def create_payment(
    request: CreatePaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new payment"""
    try:
        # Validate automation exists
        automation = db.query(Automation).filter(
            Automation.id == request.automation_id,
            Automation.status == True
        ).first()
        
        if not automation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation not found or inactive"
            )
        
        # Calculate amount based on tokens and pricing
        if automation.pricing_type == "token_per_session":
            amount = request.tokens * automation.price_per_token
        else:
            amount = request.tokens * automation.price_per_token
        
        # Generate unique transaction ID
        transaction_id = str(uuid.uuid4())
        
        # Create payment record
        payment = Payment(
            user_id=current_user.id,
            automation_id=request.automation_id,
            amount=int(amount),
            tokens_purchased=request.tokens,
            method=request.payment_method,
            gateway="zarinpal",  # Default gateway
            transaction_id=transaction_id,
            status="pending",
            discount_code=request.discount_code,
            discount_percent=request.discount_percent,
            meta=request.meta
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        # In a real implementation, you would:
        # 1. Call payment gateway API
        # 2. Get payment URL or redirect
        # 3. Store gateway response in meta field
        
        return {
            "payment_id": payment.id,
            "transaction_id": transaction_id,
            "amount": amount,
            "tokens": request.tokens,
            "status": "pending",
            "payment_url": f"https://zarinpal.com/pg/StartPay/{transaction_id}",  # Mock URL
            "message": "Payment created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment: {str(e)}"
        )

@router.post("/verify")
async def verify_payment(
    request: VerifyPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify a payment"""
    try:
        # Find payment by transaction ID
        payment = db.query(Payment).filter(
            Payment.transaction_id == request.transaction_id,
            Payment.user_id == current_user.id
        ).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        if payment.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment already processed with status: {payment.status}"
            )
        
        # In a real implementation, you would:
        # 1. Call payment gateway verification API
        # 2. Verify the payment status
        # 3. Update payment record accordingly
        
        # Mock verification - in real implementation, this would be from gateway
        if request.gateway_response.get("status") == "success":
            payment.status = "succeeded"
            payment.ref_id = request.gateway_response.get("ref_id")
            payment.meta = str(request.gateway_response)
            
            # Add tokens to user's automation
            from models.user_automation import UserAutomation
            user_automation = db.query(UserAutomation).filter(
                UserAutomation.user_id == current_user.id,
                UserAutomation.automation_id == payment.automation_id
            ).first()
            
            if user_automation:
                user_automation.tokens_remaining += payment.tokens_purchased
            else:
                # Create new user automation if it doesn't exist
                user_automation = UserAutomation(
                    user_id=current_user.id,
                    automation_id=payment.automation_id,
                    tokens_remaining=payment.tokens_purchased,
                    status="active"
                )
                db.add(user_automation)
            
            db.commit()
            
            return {
                "payment_id": payment.id,
                "transaction_id": payment.transaction_id,
                "status": "succeeded",
                "tokens_added": payment.tokens_purchased,
                "message": "Payment verified and tokens added successfully"
            }
        else:
            payment.status = "failed"
            payment.meta = str(request.gateway_response)
            db.commit()
            
            return {
                "payment_id": payment.id,
                "transaction_id": payment.transaction_id,
                "status": "failed",
                "message": "Payment verification failed"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify payment: {str(e)}"
        )

@router.get("/history")
async def get_payment_history(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's payment history"""
    try:
        payments = db.query(Payment).filter(
            Payment.user_id == current_user.id
        ).order_by(Payment.created_at.desc()).offset(offset).limit(limit).all()
        
        payment_list = []
        for payment in payments:
            automation = db.query(Automation).filter(
                Automation.id == payment.automation_id
            ).first()
            
            payment_list.append({
                "id": payment.id,
                "transaction_id": payment.transaction_id,
                "automation_name": automation.name if automation else "Unknown",
                "amount": payment.amount,
                "tokens_purchased": payment.tokens_purchased,
                "method": payment.method,
                "status": payment.status,
                "created_at": payment.created_at,
                "ref_id": payment.ref_id
            })
        
        return {
            "payments": payment_list,
            "total": len(payment_list),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve payment history: {str(e)}"
        )

@router.get("/{payment_id}")
async def get_payment_details(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment details by ID"""
    try:
        payment = db.query(Payment).filter(
            Payment.id == payment_id,
            Payment.user_id == current_user.id
        ).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        automation = db.query(Automation).filter(
            Automation.id == payment.automation_id
        ).first()
        
        return {
            "id": payment.id,
            "transaction_id": payment.transaction_id,
            "automation_name": automation.name if automation else "Unknown",
            "amount": payment.amount,
            "tokens_purchased": payment.tokens_purchased,
            "method": payment.method,
            "gateway": payment.gateway,
            "status": payment.status,
            "created_at": payment.created_at,
            "ref_id": payment.ref_id,
            "discount_code": payment.discount_code,
            "discount_percent": payment.discount_percent
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve payment details: {str(e)}"
        )
