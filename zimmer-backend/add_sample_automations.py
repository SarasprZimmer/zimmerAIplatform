#!/usr/bin/env python3
"""
Script to add sample automations to the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models.automation import Automation, PricingType

def add_sample_automations():
    """Add sample automations to the database"""
    print("=== Adding Sample Automations ===")
    
    db = SessionLocal()
    
    try:
        # Check if automations already exist
        existing_count = db.query(Automation).count()
        print(f"Current automations in database: {existing_count}")
        
        if existing_count > 0:
            print("Automations already exist. Skipping...")
            return
        
        # Sample automations
        sample_automations = [
            {
                "name": "Agency AI",
                "description": "هوش مصنوعی آژانس مسافرتی با قابلیت رزرو هتل، بلیط هواپیما و برنامه‌ریزی سفر",
                "pricing_type": PricingType.token_per_session,
                "price_per_token": 50.0,
                "status": True,
                "api_endpoint": "https://agency.zimmerai.com/api"
            },
            {
                "name": "SEO Agent",
                "description": "عامل بهینه‌سازی موتور جستجو برای بهبود رتبه‌بندی وب‌سایت‌ها",
                "pricing_type": PricingType.token_per_step,
                "price_per_token": 25.0,
                "status": True,
                "api_endpoint": "https://seo.zimmerai.com/api"
            },
            {
                "name": "Travel Assistant",
                "description": "دستیار سفر هوشمند برای برنامه‌ریزی و مدیریت سفرها",
                "pricing_type": PricingType.flat_fee,
                "price_per_token": 1000.0,
                "status": True,
                "api_endpoint": "https://travel.zimmerai.com/api"
            }
        ]
        
        # Add automations to database
        for automation_data in sample_automations:
            automation = Automation(**automation_data)
            db.add(automation)
            print(f"Adding automation: {automation_data['name']}")
        
        db.commit()
        print(f"Successfully added {len(sample_automations)} automations!")
        
        # Display added automations
        automations = db.query(Automation).all()
        print("\nCurrent automations:")
        for automation in automations:
            print(f"  ID: {automation.id}, Name: {automation.name}, Status: {automation.status}")
            
    except Exception as e:
        print(f"Error adding automations: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_automations() 