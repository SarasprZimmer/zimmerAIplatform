#!/usr/bin/env python3
"""
Comprehensive tests for the token adjustment system.
Tests happy path scenarios and safety mechanisms.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import uuid

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models.user import User
from models.automation import Automation
from models.user_automation import UserAutomation
from models.token_adjustment import TokenAdjustment
from services.token_adjust_service import apply_adjustment, list_adjustments, get_token_balance
from schemas.token_adjustment import TokenAdjustmentCreate


def create_test_database():
    """Create a test database in memory"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return engine


def create_test_data(session):
    """Create test users, automation, and user_automation"""
    
    # Create test user
    test_user = User(
        name="Test User",
        email="test@example.com",
        phone_number="09123456789",
        password_hash="test_hash_123",
        role="manager",
        is_active=True
    )
    session.add(test_user)
    
    # Create test admin
    test_admin = User(
        name="Test Admin",
        email="admin@example.com",
        phone_number="09123456788",
        password_hash="admin_hash_123",
        role="manager",  # Using valid enum value
        is_active=True
    )
    session.add(test_admin)
    
    # Create test automation
    test_automation = Automation(
        name="Test Automation",
        description="Test automation for token adjustment testing",
        price_per_token=1000,  # 1000 Rial per token
        pricing_type="token_per_session",
        status=True,
        health_status="unknown",  # Add required field
        is_listed=False  # Add required field
    )
    session.add(test_automation)
    
    session.commit()
    
    # Create user automation with 0 tokens
    user_automation = UserAutomation(
        user_id=test_user.id,
        automation_id=test_automation.id,
        tokens_remaining=0,
        status="active"
    )
    session.add(user_automation)
    session.commit()
    
    return test_user, test_admin, test_automation, user_automation


def test_token_adjustments():
    """Run comprehensive token adjustment tests"""
    print("🧪 Starting Token Adjustment System Tests...")
    
    # Create test database
    engine = create_test_database()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Create test data
        test_user, test_admin, test_automation, user_automation = create_test_data(session)
        print(f"✅ Test data created: User={test_user.id}, Admin={test_admin.id}, Automation={test_automation.id}")
        
        # Test 1: Add +100 tokens
        print("\n📝 Test 1: Adding +100 tokens")
        adjustment1 = apply_adjustment(
            session, 
            test_admin, 
            TokenAdjustmentCreate(
                user_automation_id=user_automation.id,
                delta_tokens=100,
                reason="test_addition",
                note="تست اضافه کردن توکن"
            )
        )
        
        # Verify adjustment was created
        assert adjustment1.id is not None
        assert adjustment1.delta_tokens == 100
        assert adjustment1.reason == "test_addition"
        assert adjustment1.admin_id == test_admin.id
        assert adjustment1.user_id == test_user.id
        
        # Verify user automation balance was updated
        session.refresh(user_automation)
        assert user_automation.tokens_remaining == 100
        print(f"✅ +100 tokens added successfully. New balance: {user_automation.tokens_remaining}")
        
        # Test 2: Deduct -40 tokens
        print("\n📝 Test 2: Deducting -40 tokens")
        adjustment2 = apply_adjustment(
            session, 
            test_admin, 
            TokenAdjustmentCreate(
                user_automation_id=user_automation.id,
                delta_tokens=-40,
                reason="test_deduction",
                note="تست کسر کردن توکن"
            )
        )
        
        # Verify adjustment was created
        assert adjustment2.id is not None
        assert adjustment2.delta_tokens == -40
        assert adjustment2.reason == "test_deduction"
        
        # Verify user automation balance was updated
        session.refresh(user_automation)
        assert user_automation.tokens_remaining == 60
        print(f"✅ -40 tokens deducted successfully. New balance: {user_automation.tokens_remaining}")
        
        # Test 3: Try to deduct more than available (should fail)
        print("\n📝 Test 3: Attempting to deduct -100 tokens (should fail)")
        try:
            apply_adjustment(
                session, 
                test_admin, 
                TokenAdjustmentCreate(
                    user_automation_id=user_automation.id,
                    delta_tokens=-100,
                    reason="test_overdraft",
                    note="تست کسر بیش از موجودی"
                )
            )
            assert False, "Should have failed with insufficient tokens"
        except Exception as e:
            if hasattr(e, 'detail'):
                assert "موجودی توکن نمی‌تواند منفی شود" in str(e.detail)
            else:
                assert "موجودی توکن نمی‌تواند منفی شود" in str(e)
            print(f"✅ Correctly prevented overdraft: {e}")
        
        # Verify balance unchanged
        session.refresh(user_automation)
        assert user_automation.tokens_remaining == 60
        print(f"✅ Balance unchanged: {user_automation.tokens_remaining}")
        
        # Test 4: Test idempotency
        print("\n📝 Test 4: Testing idempotency with same key")
        idempotency_key = str(uuid.uuid4())
        
        # First call
        adjustment3a = apply_adjustment(
            session, 
            test_admin, 
            TokenAdjustmentCreate(
                user_automation_id=user_automation.id,
                delta_tokens=50,
                reason="test_idempotency",
                idempotency_key=idempotency_key
            )
        )
        
        # Second call with same key
        adjustment3b = apply_adjustment(
            session, 
            test_admin, 
            TokenAdjustmentCreate(
                user_automation_id=user_automation.id,
                delta_tokens=50,
                reason="test_idempotency",
                idempotency_key=idempotency_key
            )
        )
        
        # Should return same adjustment
        assert adjustment3a.id == adjustment3b.id
        print(f"✅ Idempotency working: Same adjustment returned (ID: {adjustment3a.id})")
        
        # Verify balance only increased once
        session.refresh(user_automation)
        assert user_automation.tokens_remaining == 110  # 60 + 50 (not 60 + 50 + 50)
        print(f"✅ Balance correctly updated once: {user_automation.tokens_remaining}")
        
        # Test 5: List adjustments with filtering
        print("\n📝 Test 5: Listing adjustments with filters")
        result = list_adjustments(
            session,
            user_automation_id=user_automation.id,
            page=1,
            page_size=20
        )
        
        # Should have 3 adjustments (100, -40, 50)
        assert result["total"] == 3
        assert len(result["items"]) == 3
        print(f"✅ Found {result['total']} adjustments for user automation")
        
        # Test 6: Get token balance
        print("\n📝 Test 6: Getting current token balance")
        balance = get_token_balance(session, user_automation.id)
        
        assert balance is not None
        assert balance["user_automation_id"] == user_automation.id
        assert balance["tokens_remaining"] == 110
        assert balance["user_id"] == test_user.id
        assert balance["automation_id"] == test_automation.id
        print(f"✅ Balance retrieved correctly: {balance['tokens_remaining']} tokens")
        
        # Test 7: Test zero delta validation
        print("\n📝 Test 7: Attempting zero delta (should fail)")
        try:
            apply_adjustment(
                session, 
                test_admin, 
                TokenAdjustmentCreate(
                    user_automation_id=user_automation.id,
                    delta_tokens=0,
                    reason="test_zero",
                    note="تست تغییر صفر"
                )
            )
            assert False, "Should have failed with zero delta"
        except Exception as e:
            if hasattr(e, 'detail'):
                assert "مقدار تغییر توکن نمی‌تواند صفر باشد" in str(e.detail)
            else:
                assert "مقدار تغییر توکن نمی‌تواند صفر باشد" in str(e)
            print(f"✅ Correctly prevented zero delta: {e}")
        
        # Test 8: Test invalid user automation ID
        print("\n📝 Test 8: Attempting adjustment with invalid user automation ID")
        try:
            apply_adjustment(
                session, 
                test_admin, 
                TokenAdjustmentCreate(
                    user_automation_id=99999,  # Non-existent ID
                    delta_tokens=10,
                    reason="test_invalid_id"
                )
            )
            assert False, "Should have failed with invalid user automation ID"
        except Exception as e:
            if hasattr(e, 'detail'):
                assert "اتوماسیون کاربر یافت نشد" in str(e.detail)
            else:
                assert "اتوماسیون کاربر یافت نشد" in str(e)
            print(f"✅ Correctly handled invalid user automation ID: {e}")
        
        print("\n🎉 All tests passed successfully!")
        print(f"Final token balance: {user_automation.tokens_remaining}")
        
        # Summary
        print("\n📊 Test Summary:")
        print(f"  - Total adjustments created: {result['total']}")
        print(f"  - Final balance: {user_automation.tokens_remaining} tokens")
        print(f"  - All safety checks working")
        print(f"  - Idempotency verified")
        print(f"  - Error handling validated")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()
    
    return True


if __name__ == "__main__":
    print("🚀 Token Adjustment System Test Suite")
    print("=" * 50)
    
    success = test_token_adjustments()
    
    if success:
        print("\n✅ All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
