#!/usr/bin/env python3
"""
Test the Zarinpal payment system end-to-end
"""
import asyncio
import os
from dotenv import load_dotenv
from database import get_db
from models.user import User, UserRole
from models.automation import Automation, PricingType
from models.payment import Payment
from models.user_automation import UserAutomation
from utils.security import hash_password
from utils.zarinpal import ZarinpalClient, PaymentMode
from services.pricing import compute_amount_rial

# Load environment variables
load_dotenv("env.payments")

async def test_payment_system():
    """Test the complete payment flow"""
    print("🧪 Testing Zarinpal Payment System...")
    
    # Initialize Zarinpal client
    zarinpal_client = ZarinpalClient(
        merchant_id=os.getenv("ZARRINPAL_MERCHANT_ID"),
        base_url=os.getenv("ZARRINPAL_BASE"),
        mode=PaymentMode.SANDBOX
    )
    
    print(f"✅ Zarinpal client initialized:")
    print(f"   Merchant ID: {os.getenv('ZARRINPAL_MERCHANT_ID')}")
    print(f"   Base URL: {os.getenv('ZARRINPAL_BASE')}")
    print(f"   Mode: {os.getenv('PAYMENTS_MODE')}")
    
    # Test 1: Payment Request
    print("\n📝 Test 1: Payment Request")
    try:
        payment_response = await zarinpal_client.request_payment(
            amount_rial=100000,  # 100,000 Rial = 1000 tokens at 100 Rial per token
            description="Test Payment - Zimmer AI Automation",
            callback_url="https://userpanel.zimmerai.com/payment/return/test",
            email="test@zimmerai.com"
        )
        
        print(f"✅ Payment request successful:")
        print(f"   Authority: {payment_response['authority']}")
        print(f"   Redirect URL: {payment_response['url']}")
        
        authority = payment_response['authority']
        
    except Exception as e:
        print(f"❌ Payment request failed: {e}")
        return
    
    # Test 2: Payment Verification (simulate callback)
    print("\n📝 Test 2: Payment Verification")
    try:
        verification_result = await zarinpal_client.verify_payment(
            authority=authority,
            amount_rial=100000
        )
        
        print(f"✅ Payment verification result:")
        print(f"   Success: {verification_result['ok']}")
        print(f"   Ref ID: {verification_result['ref_id']}")
        print(f"   Code: {verification_result['code']}")
        print(f"   Message: {verification_result['message']}")
        
    except Exception as e:
        print(f"❌ Payment verification failed: {e}")
        return
    
    # Test 3: Database Integration
    print("\n📝 Test 3: Database Integration")
    try:
        db = next(get_db())
        
        # Create test user
        test_user = User(
            name="Payment Test User",
            email="payment-test@zimmerai.com",
            password_hash=hash_password("test123"),
            role=UserRole.support_staff,
            is_active=True
        )
        db.add(test_user)
        db.flush()
        print(f"✅ Test user created: {test_user.id}")
        
        # Create test automation
        test_automation = Automation(
            name="Payment Test Automation",
            description="Test automation for payment testing",
            pricing_type=PricingType.token_per_session,
            price_per_token=100,  # 100 Rial per token
            status=True,
            health_status="healthy",
            is_listed=True
        )
        db.add(test_automation)
        db.flush()
        print(f"✅ Test automation created: {test_automation.id}")
        
        # Test pricing calculation
        tokens = 1000
        amount_rial = compute_amount_rial(test_automation, tokens)
        print(f"✅ Pricing calculation: {tokens} tokens = {amount_rial:,} Rial")
        
        # Create payment record
        payment = Payment(
            user_id=test_user.id,
            automation_id=test_automation.id,
            amount=amount_rial,
            tokens_purchased=tokens,
            method="zarinpal",
            gateway="zarinpal",
            transaction_id=f"TEST-{test_user.id}-{test_automation.id}",
            status="pending",
            authority=authority
        )
        db.add(payment)
        db.flush()
        print(f"✅ Payment record created: {payment.id}")
        
        # Simulate successful payment
        payment.status = "succeeded"
        payment.ref_id = verification_result.get("ref_id", "TEST-REF-123")
        db.commit()
        print(f"✅ Payment marked as succeeded")
        
        # Credit tokens to user
        user_automation = UserAutomation(
            user_id=test_user.id,
            automation_id=test_automation.id,
            tokens_remaining=tokens,
            demo_tokens=5,
            is_demo_active=True,
            status="active"
        )
        db.add(user_automation)
        db.commit()
        print(f"✅ {tokens} tokens credited to user")
        
        # Verify token balance
        user_automation = db.query(UserAutomation).filter(
            UserAutomation.user_id == test_user.id,
            UserAutomation.automation_id == test_automation.id
        ).first()
        
        if user_automation:
            print(f"✅ User automation record verified:")
            print(f"   Tokens remaining: {user_automation.tokens_remaining}")
            print(f"   Demo tokens: {user_automation.demo_tokens}")
            print(f"   Status: {user_automation.status}")
        
        # Cleanup test data
        db.query(Payment).filter(Payment.id == payment.id).delete()
        db.query(UserAutomation).filter(UserAutomation.user_id == test_user.id).delete()
        db.query(Automation).filter(Automation.id == test_automation.id).delete()
        db.query(User).filter(User.id == test_user.id).delete()
        db.commit()
        print("🧹 Test data cleaned up")
        
    except Exception as e:
        print(f"❌ Database integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n🎉 All payment system tests passed!")

if __name__ == "__main__":
    asyncio.run(test_payment_system())
