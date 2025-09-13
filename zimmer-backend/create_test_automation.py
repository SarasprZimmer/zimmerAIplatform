#!/usr/bin/env python3
"""
Create a test automation for payment testing
"""
from database import get_db
from models.automation import Automation, PricingType

def create_test_automation():
    """Create a test automation with correct status"""
    db = next(get_db())
    
    try:
        # Check if test automation already exists
        existing = db.query(Automation).filter(
            Automation.name == "Payment Test Automation"
        ).first()
        
        if existing:
            print(f"✅ Test automation already exists: {existing.id}")
            # Update status if needed
            if existing.health_status != "healthy" or existing.is_listed != True:
                existing.health_status = "healthy"
                existing.is_listed = True
                db.commit()
                print("✅ Updated automation status to healthy and listed")
            return existing
        
        # Create new test automation
        test_automation = Automation(
            name="Payment Test Automation",
            description="Test automation for payment testing",
            pricing_type=PricingType.token_per_session,
            price_per_token=100,  # 100 Rial per token
            status=True,
            health_status="healthy",
            is_listed=True,
            api_endpoint="/test",
            service_token_hash="test_hash"
        )
        
        db.add(test_automation)
        db.commit()
        db.refresh(test_automation)
        
        print(f"✅ Created test automation: {test_automation.id}")
        print(f"   Name: {test_automation.name}")
        print(f"   Price per token: {test_automation.price_per_token}")
        print(f"   Health status: {test_automation.health_status}")
        print(f"   Is listed: {test_automation.is_listed}")
        
        return test_automation
        
    except Exception as e:
        print(f"❌ Failed to create test automation: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    create_test_automation()
