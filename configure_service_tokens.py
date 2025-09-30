#!/usr/bin/env python3
"""
Configure Service Tokens
=======================

This script helps configure service tokens for automations.
It generates tokens and updates the database.

Usage:
    python3 configure_service_tokens.py
"""

import os
import secrets
import hashlib
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def generate_service_token():
    """Generate a secure service token"""
    return secrets.token_urlsafe(32)

def hash_service_token(token: str):
    """Hash a service token for storage"""
    return hashlib.sha256(token.encode()).hexdigest()

def configure_service_tokens():
    """Configure service tokens for all automations"""
    print("🔑 Configuring Service Tokens")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        print("❌ No DATABASE_URL found")
        return False
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.begin() as conn:
            # Get all automations
            result = conn.execute(text("""
                SELECT id, name, service_token_hash
                FROM automations 
                ORDER BY id
            """))
            
            automations = result.fetchall()
            
            if not automations:
                print("❌ No automations found in database")
                return False
            
            print(f"📋 Found {len(automations)} automation(s)")
            
            env_vars = []
            
            for automation in automations:
                automation_id = automation[0]
                name = automation[1]
                current_hash = automation[2]
                
                print(f"\n🔧 Processing automation: {name} (ID: {automation_id})")
                
                if current_hash:
                    print(f"   ⚠️  Service token already configured")
                    continue
                
                # Generate new service token
                service_token = generate_service_token()
                token_hash = hash_service_token(service_token)
                
                # Update the automation
                conn.execute(text("""
                    UPDATE automations 
                    SET service_token_hash = :token_hash,
                        updated_at = NOW()
                    WHERE id = :automation_id
                """), {
                    'token_hash': token_hash,
                    'automation_id': automation_id
                })
                
                print(f"   ✅ Generated service token for automation {automation_id}")
                print(f"   Token: {service_token}")
                
                # Add to environment variables list
                env_vars.append(f"AUTOMATION_{automation_id}_SERVICE_TOKEN={service_token}")
            
            print(f"\n📝 Environment Variables to Add:")
            print("=" * 40)
            for env_var in env_vars:
                print(env_var)
            
            print(f"\n💡 Add these environment variables to your .env file or server configuration")
            print(f"   Then restart the backend service")
            
            return True
            
    except Exception as e:
        print(f"❌ Error configuring service tokens: {e}")
        return False

if __name__ == "__main__":
    success = configure_service_tokens()
    if success:
        print("\n🎉 Service tokens configured successfully!")
    else:
        print("\n💥 Failed to configure service tokens")
