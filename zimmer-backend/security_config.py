"""
Security Configuration for Zimmer AI Platform
"""
import os
from typing import List

# Security Settings
SECURITY_CONFIG = {
    # JWT Settings
    "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY"),
    "JWT_ALGORITHM": "HS256",
    "JWT_EXPIRY_DAYS": 7,
    
    # Rate Limiting
    "RATE_LIMIT_WINDOW": 60,  # seconds
    "RATE_LIMIT_MAX_REQUESTS": 100,  # requests per window
    "RATE_LIMIT_LOGIN_MAX": 5,  # login attempts per window
    
    # File Upload Security
    "MAX_FILE_SIZE": 2 * 1024 * 1024,  # 2MB
    "ALLOWED_EXTENSIONS": {".pdf", ".doc", ".docx", ".txt", ".jpg", ".jpeg", ".png", ".gif"},
    "UPLOAD_DIR": "uploads",
    
    # CORS Settings
    "ALLOWED_ORIGINS": [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "https://zimmerai.com"  # Use HTTPS in production
    ],
    
    # Password Security
    "MIN_PASSWORD_LENGTH": 8,
    "PASSWORD_REQUIRE_UPPERCASE": True,
    "PASSWORD_REQUIRE_LOWERCASE": True,
    "PASSWORD_REQUIRE_DIGITS": True,
    "PASSWORD_REQUIRE_SPECIAL": True,
    
    # Session Security
    "SESSION_TIMEOUT": 3600,  # 1 hour
    "MAX_SESSIONS_PER_USER": 5,
    
    # API Security
    "API_KEY_LENGTH": 32,
    "SERVICE_TOKEN_LENGTH": 64,
    
    # Database Security
    "DB_CONNECTION_POOL_SIZE": 10,
    "DB_MAX_OVERFLOW": 20,
    "DB_POOL_RECYCLE": 3600,
    
    # Logging Security
    "LOG_SENSITIVE_DATA": False,
    "LOG_LEVEL": "INFO",
    
    # Environment-specific settings
    "ENVIRONMENT": os.getenv("ENVIRONMENT", "development"),
    "DEBUG": os.getenv("DEBUG", "false").lower() == "true",
}

def validate_security_config():
    """Validate that all required security settings are properly configured"""
    errors = []
    
    # Check JWT secret key
    if not SECURITY_CONFIG["JWT_SECRET_KEY"]:
        errors.append("JWT_SECRET_KEY environment variable is required")
    elif SECURITY_CONFIG["JWT_SECRET_KEY"] == "your-secret-key-change-in-production":
        errors.append("JWT_SECRET_KEY must be changed from default value")
    
    # Check environment
    if SECURITY_CONFIG["ENVIRONMENT"] == "production":
        if SECURITY_CONFIG["DEBUG"]:
            errors.append("DEBUG should be False in production")
        
        # Check for HTTPS in production
        if not any(origin.startswith("https://") for origin in SECURITY_CONFIG["ALLOWED_ORIGINS"]):
            errors.append("HTTPS origins required in production")
    
    if errors:
        raise ValueError(f"Security configuration errors: {'; '.join(errors)}")
    
    return True

def get_cors_origins() -> List[str]:
    """Get CORS origins based on environment"""
    if SECURITY_CONFIG["ENVIRONMENT"] == "production":
        return [origin for origin in SECURITY_CONFIG["ALLOWED_ORIGINS"] if origin.startswith("https://")]
    return SECURITY_CONFIG["ALLOWED_ORIGINS"]

def is_production() -> bool:
    """Check if running in production environment"""
    return SECURITY_CONFIG["ENVIRONMENT"] == "production"

def should_log_sensitive_data() -> bool:
    """Check if sensitive data should be logged"""
    return SECURITY_CONFIG["LOG_SENSITIVE_DATA"] and SECURITY_CONFIG["DEBUG"]
