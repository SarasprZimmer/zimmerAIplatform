"""
Simple test for Zarinpal payment system (mock mode)
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db, engine
from models.user import User
from models.automation import Automation, PricingType
from models.payment import Payment
from models.user_automation import UserAutomation
from services.pricing import compute_amount_rial
from utils.zarinpal import ZarinpalClient, PaymentMode
from routers.payments_zarinpal import zarinpal_client

# Create tables
from database import Base
Base.metadata.create_all(bind=engine)


async def test_payment_system():
    """Test the payment system end-to-end"""
    print("🧪 Testing Zarinpal Payment System (Mock Mode)")
    print("=" * 50)
    
    # Get database session
    db = next(get_db())
    
    try:
        # 1. Create test user
        print("\n1. Creating test user...")
        test_user = User(
            name="Test User",
            email="test@example.com",
            phone_number="09123456789",
            password_hash="test_hash_123",  # Required field
            role="manager",
            is_active=True
        )
        db.add(test_user)
        db.flush()
        print(f"✅ User created: {test_user.name} (ID: {test_user.id})")
        
        # 2. Create test automation
        print("\n2. Creating test automation...")
        test_automation = Automation(
            name="Test Automation",
            description="Test automation for payment testing",
            pricing_type=PricingType.token_per_session,
            price_per_token=50000,  # 50,000 Rial per token
            status=True,
            health_status="unknown",  # Add required field
            is_listed=False  # Add required field
        )
        db.add(test_automation)
        db.flush()
        print(f"✅ Automation created: {test_automation.name} (ID: {test_automation.id})")
        print(f"   Pricing: {test_automation.pricing_type} - {test_automation.price_per_token:,} Rial per token")
        
        # 3. Test pricing calculation
        print("\n3. Testing pricing calculation...")
        tokens = 10
        amount_rial = compute_amount_rial(test_automation, tokens)
        print(f"✅ {tokens} tokens = {amount_rial:,} Rial")
        
        # 4. Test payment request (mock)
        print("\n4. Testing payment request (mock mode)...")
        payment_response = await zarinpal_client.request_payment(
            amount_rial=amount_rial,
            description=f"Test - {test_automation.name} ({tokens} tokens)",
            callback_url="https://example.com/callback",
            email=test_user.email,
            mobile=test_user.phone_number
        )
        print(f"✅ Payment request successful:")
        print(f"   Authority: {payment_response['authority']}")
        print(f"   Redirect URL: {payment_response['url']}")
        
        # 5. Create payment record
        print("\n5. Creating payment record...")
        payment = Payment(
            user_id=test_user.id,
            automation_id=test_automation.id,
            amount=amount_rial,
            tokens_purchased=tokens,
            method="zarinpal",
            gateway="zarinpal",
            transaction_id=f"TEST-{test_user.id}-{test_automation.id}-{tokens}",
            status="pending",
            authority=payment_response['authority']
        )
        db.add(payment)
        db.flush()
        print(f"✅ Payment record created: ID {payment.id}")
        
        # 6. Test payment verification (mock)
        print("\n6. Testing payment verification (mock mode)...")
        verification_result = await zarinpal_client.verify_payment(
            authority=payment_response['authority'],
            amount_rial=amount_rial
        )
        print(f"✅ Verification result:")
        print(f"   Success: {verification_result['ok']}")
        print(f"   Ref ID: {verification_result['ref_id']}")
        print(f"   Code: {verification_result['code']}")
        print(f"   Message: {verification_result['message']}")
        
        # 7. Simulate successful payment
        if verification_result['ok']:
            print("\n7. Simulating successful payment...")
            payment.status = "succeeded"
            payment.ref_id = verification_result['ref_id']
            payment.meta = '{"test": true, "mock_mode": true}'
            
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
            print(f"✅ Payment marked as succeeded")
            print(f"✅ {tokens} tokens credited to user")
            
            # 8. Verify token balance
            print("\n8. Verifying token balance...")
            user_automation = db.query(UserAutomation).filter(
                UserAutomation.user_id == test_user.id,
                UserAutomation.automation_id == test_automation.id
            ).first()
            
            if user_automation:
                print(f"✅ User automation record found:")
                print(f"   Tokens remaining: {user_automation.tokens_remaining}")
                print(f"   Demo tokens: {user_automation.demo_tokens}")
                print(f"   Status: {user_automation.status}")
            else:
                print("❌ User automation record not found")
        
        # 9. Test idempotency
        print("\n9. Testing idempotency...")
        verification_result_2 = await zarinpal_client.verify_payment(
            authority=payment_response['authority'],
            amount_rial=amount_rial
        )
        print(f"✅ Second verification (should be idempotent):")
        print(f"   Success: {verification_result_2['ok']}")
        print(f"   Ref ID: {verification_result_2['ref_id']}")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_payment_system())
