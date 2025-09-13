#!/usr/bin/env python3
"""
Secure Key Generator for Zimmer AI Platform
This script generates secure keys for JWT and encryption.
"""

import secrets
import base64
from cryptography.fernet import Fernet
import os

def generate_jwt_secret():
    """Generate a secure JWT secret key"""
    return secrets.token_urlsafe(32)

def generate_encryption_key():
    """Generate a secure encryption key for Fernet"""
    return Fernet.generate_key().decode()

def generate_service_token():
    """Generate a secure service token"""
    return secrets.token_urlsafe(32)

def main():
    print("🔐 Zimmer AI Platform - Secure Key Generator")
    print("=" * 50)
    
    # Generate keys
    jwt_secret = generate_jwt_secret()
    encryption_key = generate_encryption_key()
    service_token = generate_service_token()
    
    print("\n📋 Generated Keys:")
    print("-" * 30)
    
    print(f"\n🔑 JWT Secret Key:")
    print(f"JWT_SECRET_KEY={jwt_secret}")
    
    print(f"\n🔐 Encryption Key:")
    print(f"OAI_ENCRYPTION_SECRET={encryption_key}")
    
    print(f"\n🎫 Service Token (example):")
    print(f"AUTOMATION_SERVICE_TOKEN={service_token}")
    
    print("\n📝 Instructions:")
    print("-" * 30)
    print("1. Copy these keys to your .env file")
    print("2. Keep these keys secure and never commit them to version control")
    print("3. Use different keys for development and production")
    print("4. Rotate keys regularly in production")
    
    print("\n⚠️  Security Notes:")
    print("-" * 30)
    print("• Store keys securely (environment variables, secret management)")
    print("• Use HTTPS in production")
    print("• Enable rate limiting")
    print("• Monitor for suspicious activity")
    print("• Regular security audits")
    
    # Create .env template
    env_template = f"""# Zimmer Backend Environment Configuration
# Copy this file to .env and update the values

# Database Configuration
DATABASE_URL=sqlite:///./zimmer_dashboard.db

# JWT Configuration (REQUIRED - Generated above)
JWT_SECRET_KEY={jwt_secret}

# Server Configuration
HOST=0.0.0.0
PORT=8000

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,http://zimmerai.com

# Development Settings
DEBUG=true
ENVIRONMENT=development

# OpenAI Key Encryption (REQUIRED - Generated above)
OAI_ENCRYPTION_SECRET={encryption_key}

# Optional: External Services
# OPENAI_API_KEY=your-openai-api-key
# TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# Optional: File Upload Settings
MAX_FILE_SIZE=2097152  # 2MB in bytes
UPLOAD_DIR=uploads

# Optional: Logging
LOG_LEVEL=info

# Security Settings
ALLOW_INSECURE_AUTH=false
"""
    
    # Write to .env.template
    with open('.env.template', 'w') as f:
        f.write(env_template)
    
    print(f"\n✅ Generated .env.template with secure keys")
    print("📁 Copy .env.template to .env and customize as needed")
    
    print("\n🚀 Next Steps:")
    print("-" * 30)
    print("1. Copy .env.template to .env")
    print("2. Customize other settings as needed")
    print("3. Start the application")
    print("4. Test authentication and functionality")

if __name__ == "__main__":
    main()
