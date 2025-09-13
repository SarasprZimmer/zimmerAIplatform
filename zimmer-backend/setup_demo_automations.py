#!/usr/bin/env python3
"""
Script to set up comprehensive demo automations for testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models.automation import Automation, PricingType
from datetime import datetime, timezone

def setup_demo_automations():
    """Set up comprehensive demo automations"""
    print("=== Setting Up Demo Automations ===")
    
    db = SessionLocal()
    
    try:
        # Clear existing automations
        db.query(Automation).delete()
        print("Cleared existing automations")
        
        # Comprehensive demo automations
        demo_automations = [
            {
                "name": "Agency AI",
                "description": "هوش مصنوعی آژانس مسافرتی با قابلیت رزرو هتل، بلیط هواپیما و برنامه‌ریزی سفر کامل",
                "pricing_type": PricingType.token_per_session,
                "price_per_token": 50.0,
                "status": True,
                "api_base_url": "https://agency-demo.zimmerai.com",
                "api_provision_url": "https://agency-demo.zimmerai.com/api/provision",
                "api_usage_url": "https://agency-demo.zimmerai.com/api/usage",
                "api_kb_status_url": "https://agency-demo.zimmerai.com/api/kb-status",
                "api_kb_reset_url": "https://agency-demo.zimmerai.com/api/kb-reset",
                "health_check_url": "https://agency-demo.zimmerai.com/health",
                "health_status": "healthy",
                "is_listed": True,
                "last_health_at": datetime.now(timezone.utc),
                "health_details": {
                    "status": "ok",
                    "version": "1.0.0",
                    "uptime": 86400,
                    "services": ["booking", "payment", "notifications"]
                }
            },
            {
                "name": "SEO Agent Pro",
                "description": "عامل پیشرفته بهینه‌سازی موتور جستجو با تحلیل کلمات کلیدی، رقبا و بهبود محتوا",
                "pricing_type": PricingType.token_per_step,
                "price_per_token": 25.0,
                "status": True,
                "api_base_url": "https://seo-demo.zimmerai.com",
                "api_provision_url": "https://seo-demo.zimmerai.com/api/provision",
                "api_usage_url": "https://seo-demo.zimmerai.com/api/usage",
                "api_kb_status_url": "https://seo-demo.zimmerai.com/api/kb-status",
                "api_kb_reset_url": "https://seo-demo.zimmerai.com/api/kb-reset",
                "health_check_url": "https://seo-demo.zimmerai.com/health",
                "health_status": "healthy",
                "is_listed": True,
                "last_health_at": datetime.now(timezone.utc),
                "health_details": {
                    "status": "ok",
                    "version": "2.1.0",
                    "uptime": 172800,
                    "services": ["keyword_analysis", "competitor_tracking", "content_optimization"]
                }
            },
            {
                "name": "Customer Support Bot",
                "description": "ربات پشتیبانی مشتریان با قابلیت پاسخ‌دهی خودکار و انتقال به اپراتور انسانی",
                "pricing_type": PricingType.flat_fee,
                "price_per_token": 1000.0,
                "status": True,
                "api_base_url": "https://support-demo.zimmerai.com",
                "api_provision_url": "https://support-demo.zimmerai.com/api/provision",
                "api_usage_url": "https://support-demo.zimmerai.com/api/usage",
                "api_kb_status_url": "https://support-demo.zimmerai.com/api/kb-status",
                "api_kb_reset_url": "https://support-demo.zimmerai.com/api/kb-reset",
                "health_check_url": "https://support-demo.zimmerai.com/health",
                "health_status": "healthy",
                "is_listed": True,
                "last_health_at": datetime.now(timezone.utc),
                "health_details": {
                    "status": "ok",
                    "version": "1.5.0",
                    "uptime": 259200,
                    "services": ["chat", "ticket_management", "escalation"]
                }
            },
            {
                "name": "E-commerce Assistant",
                "description": "دستیار فروشگاه آنلاین با قابلیت مدیریت محصولات، سفارشات و تحلیل فروش",
                "pricing_type": PricingType.token_per_session,
                "price_per_token": 75.0,
                "status": True,
                "api_base_url": "https://ecommerce-demo.zimmerai.com",
                "api_provision_url": "https://ecommerce-demo.zimmerai.com/api/provision",
                "api_usage_url": "https://ecommerce-demo.zimmerai.com/api/usage",
                "api_kb_status_url": "https://ecommerce-demo.zimmerai.com/api/kb-status",
                "api_kb_reset_url": "https://ecommerce-demo.zimmerai.com/api/kb-reset",
                "health_check_url": "https://ecommerce-demo.zimmerai.com/health",
                "health_status": "healthy",
                "is_listed": True,
                "last_health_at": datetime.now(timezone.utc),
                "health_details": {
                    "status": "ok",
                    "version": "1.2.0",
                    "uptime": 432000,
                    "services": ["inventory", "orders", "analytics", "recommendations"]
                }
            },
            {
                "name": "Content Creator AI",
                "description": "هوش مصنوعی تولید محتوا برای وب‌سایت‌ها، شبکه‌های اجتماعی و بازاریابی",
                "pricing_type": PricingType.token_per_step,
                "price_per_token": 30.0,
                "status": True,
                "api_base_url": "https://content-demo.zimmerai.com",
                "api_provision_url": "https://content-demo.zimmerai.com/api/provision",
                "api_usage_url": "https://content-demo.zimmerai.com/api/usage",
                "api_kb_status_url": "https://content-demo.zimmerai.com/api/kb-status",
                "api_kb_reset_url": "https://content-demo.zimmerai.com/api/kb-reset",
                "health_check_url": "https://content-demo.zimmerai.com/health",
                "health_status": "degraded",
                "is_listed": False,
                "last_health_at": datetime.now(timezone.utc),
                "health_details": {
                    "status": "maintenance",
                    "version": "1.0.0",
                    "uptime": 7200,
                    "services": ["article_writing", "social_media", "seo_content"],
                    "maintenance_mode": True
                }
            }
        ]
        
        # Add automations to database
        for automation_data in demo_automations:
            automation = Automation(**automation_data)
            db.add(automation)
            print(f"Adding automation: {automation_data['name']} (Status: {automation_data['health_status']})")
        
        db.commit()
        print(f"\nSuccessfully added {len(demo_automations)} demo automations!")
        
        # Display added automations
        automations = db.query(Automation).all()
        print("\n=== Demo Automations ===")
        for automation in automations:
            print(f"  ID: {automation.id}")
            print(f"  Name: {automation.name}")
            print(f"  Status: {automation.status}")
            print(f"  Listed: {automation.is_listed}")
            print(f"  Health: {automation.health_status}")
            print(f"  Pricing: {automation.pricing_type} - {automation.price_per_token}")
            print(f"  API Base: {automation.api_base_url}")
            print("  ---")
            
    except Exception as e:
        print(f"Error setting up automations: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    setup_demo_automations()
