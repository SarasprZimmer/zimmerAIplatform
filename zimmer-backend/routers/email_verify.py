import secrets
import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.email_verification import EmailVerificationToken
from schemas.email_verify import RequestVerifyIn, VerifyEmailIn, VerifyEmailOut
from services.mailer import send_email
from settings import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

def _new_token() -> str:
    return secrets.token_urlsafe(48)

@router.post("/request-email-verify")
def request_email_verify(payload: RequestVerifyIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        # Don't reveal email existence
        return {"ok": True}
    # invalidate previous unused tokens (optional)
    db.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == user.id,
        EmailVerificationToken.used_at.is_(None)
    ).delete()
    t = EmailVerificationToken(
        user_id=user.id,
        token=_new_token(),
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.EMAIL_VERIFICATION_TTL_MIN)
    )
    db.add(t)
    db.commit()
    db.refresh(t)

    verify_link = f"{settings.FRONTEND_VERIFY_URL}?token={t.token}"
    html = f"""
    <p>Verify your email for Zimmer.</p>
    <p><a href="{verify_link}">Click here to verify</a> (valid {settings.EMAIL_VERIFICATION_TTL_MIN} minutes)</p>
    """
    send_email(user.email, "Verify your email", html)
    return {"ok": True}

@router.post("/verify-email", response_model=VerifyEmailOut)
def verify_email(payload: VerifyEmailIn, db: Session = Depends(get_db)):
    t = db.query(EmailVerificationToken).filter(EmailVerificationToken.token == payload.token).first()
    if not t:
        raise HTTPException(status_code=400, detail="invalid_token")
    if t.used_at is not None:
        raise HTTPException(status_code=400, detail="token_used")
    if t.expires_at <= datetime.datetime.utcnow():
        raise HTTPException(status_code=400, detail="token_expired")
    user = db.query(User).get(t.user_id)
    if not user:
        raise HTTPException(status_code=400, detail="user_missing")
    user.email_verified_at = datetime.datetime.utcnow()
    t.used_at = datetime.datetime.utcnow()
    db.commit()
    return VerifyEmailOut(ok=True, message="email_verified")
