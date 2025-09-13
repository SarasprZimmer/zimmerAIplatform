import secrets
import hashlib
import datetime
import pyotp
from sqlalchemy.orm import Session

def now_utc():
    """Get current UTC datetime"""
    return datetime.datetime.utcnow()

def generate_secret() -> str:
    return pyotp.random_base32()

def make_otpauth_uri(secret: str, email: str, issuer: str="Zimmer"):
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer)

def verify_code(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)

def generate_recovery_codes(n: int = 8) -> list[str]:
    return [secrets.token_hex(5) for _ in range(n)]

def _hash(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()

def store_recovery_codes(db: Session, user_id: int, codes: list[str], model):
    rows = [model(user_id=user_id, code_hash=_hash(c)) for c in codes]
    db.add_all(rows)
    db.commit()

def consume_recovery_code(db: Session, user_id: int, code: str, model) -> bool:
    h = _hash(code)
    row = db.query(model).filter(
        model.user_id==user_id, model.code_hash==h, model.used_at.is_(None)
    ).first()
    if not row: 
        return False
    row.used_at = now_utc()
    db.commit()
    return True
