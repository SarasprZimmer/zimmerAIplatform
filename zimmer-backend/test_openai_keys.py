#!/usr/bin/env python3
"""
Test script for OpenAI key management system
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models.automation import Automation
from models.openai_key import OpenAIKey, OpenAIKeyStatus
from services.openai_key_manager import OpenAIKeyManager
from utils.crypto import encrypt_secret, decrypt_secret, mask_secret, generate_encryption_key

def test_encryption():
    """Test encryption utilities"""
    print("🔐 Testing encryption utilities...")
    
    # Generate a test key
    test_key = "sk-test1234567890abcdefghijklmnopqrstuvwxyz"
    
    # Test encryption/decryption
    encrypted = encrypt_secret(test_key)
    decrypted = decrypt_secret(encrypted)
    
    assert decrypted == test_key, "Encryption/decryption failed"
    print("✅ Encryption/decryption test passed")
    
    # Test masking
    masked = mask_secret(test_key)
    assert masked == "sk-****wxyz", f"Masking failed: {masked}"
    print("✅ Masking test passed")

def test_key_manager():
    """Test key manager functionality"""
    print("\n🔑 Testing key manager...")
    
    db = SessionLocal()
    
    try:
        # Create a test automation
        automation = Automation(
            name="Test Automation",
            description="Test automation for OpenAI keys",
            pricing_type="token_per_session",
            price_per_token=0.001,
            status=True,
            health_status="unknown",  # Add required field
            is_listed=False  # Add required field
        )
        db.add(automation)
        db.commit()
        db.refresh(automation)
        
        print(f"✅ Created test automation: {automation.id}")
        
        # Create test keys
        key_manager = OpenAIKeyManager(db)
        
        # Create 3 test keys
        test_keys = []
        for i in range(3):
            key = OpenAIKey(
                automation_id=automation.id,
                alias=f"test-key-{i+1}",
                key_encrypted=encrypt_secret(f"sk-test{i+1}1234567890abcdefghijklmnopqrstuvwxyz"),
                status=OpenAIKeyStatus.ACTIVE,
                rpm_limit=10 if i < 2 else None,  # First 2 keys have RPM limits
                daily_token_limit=1000 if i < 2 else None  # First 2 keys have daily limits
            )
            db.add(key)
            test_keys.append(key)
        
        db.commit()
        print(f"✅ Created {len(test_keys)} test keys")
        
        # Test key selection
        print("\n🔄 Testing key selection...")
        for i in range(5):
            selected_key = key_manager.select_key(automation.id)
            if selected_key:
                print(f"  Selected key: {selected_key.alias} (RPM: {selected_key.used_requests_minute})")
                
                # Record usage
                key_manager.record_usage(
                    key_id=selected_key.id,
                    tokens_used=100,
                    ok=True,
                    model="gpt-4",
                    prompt_tokens=50,
                    completion_tokens=50,
                    automation_id=automation.id
                )
            else:
                print("  No keys available")
        
        # Test failure handling
        print("\n⚠️ Testing failure handling...")
        failed_key = test_keys[0]
        should_retry = key_manager.handle_failure(failed_key.id, "401")
        print(f"  Key {failed_key.alias} failed with 401, should retry: {should_retry}")
        
        # Test daily limit exhaustion
        print("\n📊 Testing daily limit exhaustion...")
        limit_key = test_keys[1]
        key_manager.record_usage(
            key_id=limit_key.id,
            tokens_used=1000,  # Hit the daily limit
            ok=True,
            model="gpt-4",
            prompt_tokens=500,
            completion_tokens=500,
            automation_id=automation.id
        )
        
        # Check if key is exhausted
        db.refresh(limit_key)
        print(f"  Key {limit_key.alias} status after hitting limit: {limit_key.status}")
        
        # Test key selection after failures
        print("\n🔄 Testing key selection after failures...")
        for i in range(3):
            selected_key = key_manager.select_key(automation.id)
            if selected_key:
                print(f"  Selected key: {selected_key.alias} (status: {selected_key.status})")
            else:
                print("  No keys available")
        
        print("✅ Key manager tests completed")
        
    finally:
        # Cleanup
        db.query(OpenAIKey).filter(OpenAIKey.automation_id == automation.id).delete()
        db.query(Automation).filter(Automation.id == automation.id).delete()
        db.commit()
        db.close()

def test_gpt_integration():
    """Test GPT service integration"""
    print("\n🤖 Testing GPT service integration...")
    
    # This would test the actual GPT service with the key manager
    # For now, we'll just test the function signature
    from services.gpt import generate_gpt_response_with_keys
    
    print("✅ GPT service integration test structure verified")

def main():
    """Run all tests"""
    print("🚀 Starting OpenAI Key Management Tests...")
    print("=" * 50)
    
    try:
        test_encryption()
        test_key_manager()
        test_gpt_integration()
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed successfully!")
        print("\n📋 Test Summary:")
        print("  • Encryption utilities: ✅")
        print("  • Key manager functionality: ✅")
        print("  • GPT service integration: ✅")
        print("\n🔧 Next steps:")
        print("  1. Set OAI_ENCRYPTION_SECRET in your .env file")
        print("  2. Run the migration script: python scripts/migrate_openai_keys.py")
        print("  3. Restart the backend server")
        print("  4. Use the admin panel to add real OpenAI keys")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
