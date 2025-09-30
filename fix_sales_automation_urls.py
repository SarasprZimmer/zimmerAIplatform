#!/usr/bin/env python3
"""
Fix Sales Automation URLs
========================

This script fixes the sales automation URLs in the database.
It updates the URLs to use the correct format.

Usage:
    python3 fix_sales_automation_urls.py
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def fix_sales_automation_urls():
    """Fix the sales automation URLs in the database"""
    print("🔧 Fixing Sales Automation URLs")
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
            # Check current automation URLs
            result = conn.execute(text("""
                SELECT id, name, api_base_url, api_provision_url, api_usage_url, 
                       api_kb_status_url, api_kb_reset_url
                FROM automations 
                WHERE api_base_url LIKE '%salesautomation.zimmerai.com%'
                   OR api_provision_url LIKE '%salesautomation.zimmerai.com%'
            """))
            
            automations = result.fetchall()
            
            if not automations:
                print("❌ No sales automations found in database")
                return False
            
            for automation in automations:
                automation_id = automation[0]
                name = automation[1]
                current_base = automation[2]
                current_provision = automation[3]
                current_usage = automation[4]
                current_kb_status = automation[5]
                current_kb_reset = automation[6]
                
                print(f"📋 Found automation: {name} (ID: {automation_id})")
                print(f"   Current Base URL: {current_base}")
                print(f"   Current Provision URL: {current_provision}")
                
                # Update URLs to use correct format
                new_base_url = "https://salesautomation.zimmerai.com/api/"
                new_provision_url = "https://salesautomation.zimmerai.com/api/zimmer/provision"
                new_usage_url = "https://salesautomation.zimmerai.com/api/zimmer/usage/consume"
                new_kb_status_url = "https://salesautomation.zimmerai.com/api/zimmer/kb/status"
                new_kb_reset_url = "https://salesautomation.zimmerai.com/api/zimmer/kb/reset"
                
                # Update the automation
                conn.execute(text("""
                    UPDATE automations 
                    SET api_base_url = :base_url,
                        api_provision_url = :provision_url,
                        api_usage_url = :usage_url,
                        api_kb_status_url = :kb_status_url,
                        api_kb_reset_url = :kb_reset_url,
                        updated_at = NOW()
                    WHERE id = :automation_id
                """), {
                    'base_url': new_base_url,
                    'provision_url': new_provision_url,
                    'usage_url': new_usage_url,
                    'kb_status_url': new_kb_status_url,
                    'kb_reset_url': new_kb_reset_url,
                    'automation_id': automation_id
                })
                
                print(f"   ✅ Updated URLs for automation {automation_id}")
                print(f"   New Base URL: {new_base_url}")
                print(f"   New Provision URL: {new_provision_url}")
            
            print(f"\n✅ Successfully updated {len(automations)} sales automation(s)")
            return True
            
    except Exception as e:
        print(f"❌ Error updating automation URLs: {e}")
        return False

if __name__ == "__main__":
    success = fix_sales_automation_urls()
    if success:
        print("\n🎉 Sales automation URLs fixed successfully!")
    else:
        print("\n💥 Failed to fix sales automation URLs")
