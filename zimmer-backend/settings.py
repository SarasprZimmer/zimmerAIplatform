from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Payments
    PAYMENTS_MODE: str = "sandbox"
    ZARRINPAL_MERCHANT_ID: str = ""
    ZARRINPAL_CALLBACK_URL: str = ""
    ZARRINPAL_DESCRIPTION: str = "Zimmer token purchase"
    
    # Email
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "no-reply@zimmerai.com")
    FRONTEND_VERIFY_URL: str = os.getenv("FRONTEND_VERIFY_URL", "http://localhost:3000/verify-email")
    EMAIL_VERIFICATION_TTL_MIN: int = int(os.getenv("EMAIL_VERIFICATION_TTL_MIN", "30"))
    REQUIRE_VERIFIED_EMAIL_FOR_LOGIN: bool = os.getenv("REQUIRE_VERIFIED_EMAIL_FOR_LOGIN", "False").lower() == "true"
    print(f"DEBUG: REQUIRE_VERIFIED_EMAIL_FOR_LOGIN = {REQUIRE_VERIFIED_EMAIL_FOR_LOGIN}")
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URL: str = os.getenv("GOOGLE_REDIRECT_URL", "http://localhost:8000/api/auth/google/callback")
    FRONTEND_BASE_URL: str = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
