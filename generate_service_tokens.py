#!/usr/bin/env python3
"""
Generate Service Tokens for Automations
======================================

This script generates secure service tokens for each automation
and provides instructions for configuration.

Usage:
    python3 generate_service_tokens.py
"""

import os
import secrets
import hashlib
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def generate_service_token():
    """Generate a secure service token (32 bytes, URL-safe)"""
    return secrets.token_urlsafe(32)

def hash_service_token(token: str):
    """Hash a service token for secure storage"""
    return hashlib.sha256(token.encode()).hexdigest()

def generate_tokens_for_automations():
    """Generate service tokens for all automations"""
    print("🔑 Generating Service Tokens for Automations")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        print("❌ No DATABASE_URL found")
        print("💡 Make sure you're running this on the server with database access")
        return False
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.begin() as conn:
            # Get all automations that need service tokens
            result = conn.execute(text("""
                SELECT id, name, service_token_hash
                FROM automations 
                WHERE api_provision_url IS NOT NULL
                ORDER BY id
            """))
            
            automations = result.fetchall()
            
            if not automations:
                print("❌ No automations found that need service tokens")
                return False
            
            print(f"📋 Found {len(automations)} automation(s) that need service tokens")
            
            env_vars = []
            updated_count = 0
            
            for automation in automations:
                automation_id = automation[0]
                name = automation[1]
                current_hash = automation[2]
                
                print(f"\n🔧 Processing: {name} (ID: {automation_id})")
                
                if current_hash:
                    print(f"   ⚠️  Service token already exists (hash: {current_hash[:16]}...)")
                    continue
                
                # Generate new service token
                service_token = generate_service_token()
                token_hash = hash_service_token(service_token)
                
                # Update the automation in database
                conn.execute(text("""
                    UPDATE automations 
                    SET service_token_hash = :token_hash,
                        updated_at = NOW()
                    WHERE id = :automation_id
                """), {
                    'token_hash': token_hash,
                    'automation_id': automation_id
                })
                
                print(f"   ✅ Generated new service token")
                print(f"   Token: {service_token}")
                print(f"   Hash: {token_hash[:16]}...")
                
                # Add to environment variables list
                env_vars.append(f"AUTOMATION_{automation_id}_SERVICE_TOKEN={service_token}")
                updated_count += 1
            
            print(f"\n📝 Environment Variables to Add:")
            print("=" * 50)
            for env_var in env_vars:
                print(env_var)
            
            print(f"\n💡 Configuration Instructions:")
            print("=" * 50)
            print("1. Add the environment variables above to your .env file")
            print("2. Or add them to your server environment (PM2, systemd, etc.)")
            print("3. Restart the backend service")
            print("4. The tokens will be used automatically for automation communication")
            
            print(f"\n🔒 Security Notes:")
            print("=" * 50)
            print("• Service tokens are sensitive - keep them secure")
            print("• Never commit tokens to version control")
            print("• Each automation gets a unique token")
            print("• Tokens are hashed in the database for security")
            
            return True
            
    except Exception as e:
        print(f"❌ Error generating service tokens: {e}")
        return False

if __name__ == "__main__":
    success = generate_tokens_for_automations()
    if success:
        print("\n🎉 Service tokens generated successfully!")
        print("\nNext steps:")
        print("1. Add the environment variables to your server")
        print("2. Restart the backend service")
        print("3. Test automation connections")
    else:
        print("\n💥 Failed to generate service tokens")
