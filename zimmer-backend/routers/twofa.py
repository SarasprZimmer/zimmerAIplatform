from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from database import get_db
from utils.auth_dependency import get_current_user
from schemas.twofa import TwoFAInitiateOut, TwoFAActivateIn, TwoFAStatusOut, TwoFAVerifyIn, RecoveryCodesOut
from services.twofa import generate_secret, make_otpauth_uri, verify_code, generate_recovery_codes, store_recovery_codes, consume_recovery_code, now_utc
from utils.jwt import create_access_token, create_refresh_token, hash_refresh_token, JWT_SECRET_KEY
from models.user import User
from models.session import Session as UserSession
from models.twofa import TwoFactorRecoveryCode
import datetime
import jwt

router = APIRouter(prefix="/api/auth/2fa", tags=["auth"])

def create_otp_challenge_token(user_id: int, secret: str) -> str:
    payload = {
        "sub": str(user_id),
        "typ": "otp",
        "iat": int(now_utc().timestamp()),
        "exp": int((now_utc() + datetime.timedelta(minutes=2)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

@router.get("/status", response_model=TwoFAStatusOut)
def status(user=Depends(get_current_user)):
    return TwoFAStatusOut(enabled=bool(user.twofa_enabled))

@router.post("/initiate", response_model=TwoFAInitiateOut)
def initiate(user=Depends(get_current_user), db: Session = Depends(get_db)):
    if user.twofa_enabled:
        raise HTTPException(status_code=400, detail="already_enabled")
    secret = generate_secret()
    user.twofa_secret = secret
    db.commit()
    return TwoFAInitiateOut(otpauth_uri=make_otpauth_uri(secret, user.email, issuer="Zimmer"))

@router.post("/activate")
def activate(payload: TwoFAActivateIn, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user.twofa_secret:
        raise HTTPException(status_code=400, detail="initiate_first")
    if not verify_code(user.twofa_secret, payload.otp_code):
        raise HTTPException(status_code=400, detail="invalid_otp")
    user.twofa_enabled = True
    db.commit()
    codes = generate_recovery_codes()
    store_recovery_codes(db, user.id, codes, TwoFactorRecoveryCode)
    return {"ok": True, "recovery_codes": codes}

@router.post("/disable")
def disable(user=Depends(get_current_user), db: Session = Depends(get_db)):
    user.twofa_enabled = False
    user.twofa_secret = None
    db.query(TwoFactorRecoveryCode).filter_by(user_id=user.id).delete()
    db.commit()
    return {"ok": True}

@router.post("/recovery-codes/regenerate", response_model=RecoveryCodesOut)
def regenerate(user=Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(TwoFactorRecoveryCode).filter_by(user_id=user.id).delete()
    codes = generate_recovery_codes()
    store_recovery_codes(db, user.id, codes, TwoFactorRecoveryCode)
    return RecoveryCodesOut(codes=codes)

@router.post("/verify")
def verify(payload: TwoFAVerifyIn, request: Request, response: Response, db: Session = Depends(get_db)):
    try:
        data = jwt.decode(payload.challenge_token, JWT_SECRET_KEY, algorithms=["HS256"])
        if data.get("typ") != "otp":
            raise HTTPException(status_code=401, detail="invalid_challenge_token")
        user_id = int(data.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="invalid_challenge_token")

    user = db.query(User).get(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="user_inactive")

    ok = False
    if user.twofa_secret and verify_code(user.twofa_secret, payload.otp_code):
        ok = True
    elif consume_recovery_code(db, user_id, payload.otp_code, TwoFactorRecoveryCode):
        ok = True
    if not ok:
        raise HTTPException(status_code=400, detail="invalid_otp")

    access = create_access_token(user.id, user.is_admin)
    refresh = create_refresh_token()
    sess = UserSession(
        user_id=user.id,
        refresh_token_hash=hash_refresh_token(refresh),
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
        expires_at=now_utc() + datetime.timedelta(days=7),
    )
    db.add(sess)
    db.commit()
    response.set_cookie("refresh_token", refresh, httponly=True, secure=False, samesite="lax", path="/")
    return {"access_token": access, "refresh_token": refresh, "token_type":"bearer"}
