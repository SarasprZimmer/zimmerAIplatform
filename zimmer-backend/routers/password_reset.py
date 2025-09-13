from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from database import get_db
from models.user import User
from models.password_reset_token import PasswordResetToken
from schemas.password_reset import ForgotPasswordRequest, ForgotPasswordResponse, ResetPasswordRequest, ResetPasswordResponse
from services.email_service import email_service
import bcrypt

router = APIRouter()

@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Send password reset email to user
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == request.email).first()
        
        if not user:
            # Don't reveal if user exists or not for security
            return ForgotPasswordResponse(
                message="اگر ایمیل شما در سیستم ثبت شده باشد، لینک بازنشانی رمز عبور ارسال خواهد شد.",
                success=True
            )
        
        # Delete any existing tokens for this user
        db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).delete()
        
        # Create new token
        token = PasswordResetToken.generate_token()
        expires_at = datetime.utcnow() + timedelta(minutes=30)
        
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        
        db.add(reset_token)
        db.commit()
        
        # Send email
        email_sent = email_service.send_password_reset_email(
            to_email=user.email,
            reset_token=token,
            user_name=user.name
        )
        
        if email_sent:
            return ForgotPasswordResponse(
                message="لینک بازنشانی رمز عبور به ایمیل شما ارسال شد.",
                success=True
            )
        else:
            # If email failed, still return success to user but log the error
            print(f"Failed to send password reset email to {user.email}")
            return ForgotPasswordResponse(
                message="لینک بازنشانی رمز عبور به ایمیل شما ارسال شد.",
                success=True
            )
            
    except Exception as e:
        print(f"Error in forgot_password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="خطا در پردازش درخواست"
        )

@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Reset user password using token
    """
    try:
        # Find token
        reset_token = db.query(PasswordResetToken).filter(
            PasswordResetToken.token == request.token
        ).first()
        
        if not reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="توکن نامعتبر است"
            )
        
        # Check if token is expired
        if reset_token.is_expired():
            # Delete expired token
            db.delete(reset_token)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="توکن منقضی شده است"
            )
        
        # Get user
        user = db.query(User).filter(User.id == reset_token.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="کاربر یافت نشد"
            )
        
        # Hash new password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(request.new_password.encode('utf-8'), salt)
        
        # Update user password
        user.password_hash = hashed_password.decode('utf-8')
        
        # Delete all reset tokens for this user
        db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).delete()
        
        db.commit()
        
        return ResetPasswordResponse(
            message="رمز عبور شما با موفقیت تغییر یافت.",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in reset_password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="خطا در بازنشانی رمز عبور"
        )

@router.post("/cleanup-expired-tokens")
async def cleanup_expired_tokens(db: Session = Depends(get_db)):
    """
    Clean up expired password reset tokens (can be called by a scheduled task)
    """
    try:
        # Delete expired tokens
        expired_tokens = db.query(PasswordResetToken).filter(
            PasswordResetToken.expires_at < datetime.utcnow()
        ).all()
        
        for token in expired_tokens:
            db.delete(token)
        
        db.commit()
        
        return {
            "message": f"{len(expired_tokens)} توکن منقضی شده حذف شد",
            "deleted_count": len(expired_tokens)
        }
        
    except Exception as e:
        print(f"Error cleaning up expired tokens: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="خطا در پاکسازی توکن‌های منقضی شده"
        ) 