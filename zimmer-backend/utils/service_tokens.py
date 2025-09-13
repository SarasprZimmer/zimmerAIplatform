import secrets
import bcrypt
from typing import Optional

def generate_token() -> str:
    return secrets.token_hex(32)

def hash_token(token: str) -> str:
    token_bytes = token.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(token_bytes, salt)
    return hashed.decode("utf-8")

def verify_token(plain: str, hashed: str) -> bool:
    try:
        plain_bytes = plain.encode("utf-8")
        hashed_bytes = hashed.encode("utf-8")
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception:
        return False

def mask_token(token: str) -> str:
    if len(token) <= 8:
        return "*" * len(token)
    return "*" * (len(token) - 4) + token[-4:]