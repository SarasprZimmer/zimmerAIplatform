import os
import base64
from cryptography.fernet import Fernet
from typing import Optional

_fernet_instance: Optional[Fernet] = None

def load_fernet() -> Fernet:
    """Load Fernet instance from environment variable"""
    global _fernet_instance
    
    if _fernet_instance is None:
        secret = os.getenv("OAI_ENCRYPTION_SECRET")
        if not secret:
            raise ValueError("OAI_ENCRYPTION_SECRET environment variable is required")
        
        # Ensure the key is properly formatted for Fernet
        try:
            # If it's not already base64, encode it
            if len(secret) != 44:  # Fernet key length
                # Generate a proper Fernet key from the secret
                key = base64.urlsafe_b64encode(secret.encode()[:32].ljust(32, b'0'))
            else:
                key = secret.encode()
            
            _fernet_instance = Fernet(key)
        except Exception as e:
            raise ValueError(f"Invalid OAI_ENCRYPTION_SECRET: {e}")
    
    return _fernet_instance

def encrypt_secret(plain: str) -> str:
    """Encrypt a plain text secret"""
    fernet = load_fernet()
    encrypted = fernet.encrypt(plain.encode())
    return encrypted.decode()

def decrypt_secret(encrypted: str) -> str:
    """Decrypt an encrypted secret"""
    fernet = load_fernet()
    decrypted = fernet.decrypt(encrypted.encode())
    return decrypted.decode()

def mask_secret(plain_or_decrypted: str) -> str:
    """Mask a secret for display (e.g., "sk-****abcd")"""
    if not plain_or_decrypted or len(plain_or_decrypted) <= 8:
        return "*" * len(plain_or_decrypted) if plain_or_decrypted else ""
    
    # For OpenAI keys, preserve the prefix
    if plain_or_decrypted.startswith("sk-"):
        return "sk-****" + plain_or_decrypted[-4:]
    elif plain_or_decrypted.startswith("sk-proj-"):
        return "sk-proj-****" + plain_or_decrypted[-4:]
    
    # Generic masking
    return "*" * (len(plain_or_decrypted) - 4) + plain_or_decrypted[-4:]

def generate_encryption_key() -> str:
    """Generate a new Fernet encryption key for OAI_ENCRYPTION_SECRET"""
    return Fernet.generate_key().decode()
