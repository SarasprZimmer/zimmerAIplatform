#!/usr/bin/env python3
"""
Script to debug automation deletion issues
Run this on your server to check what's happening
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment variables")
    sys.exit(1)

# Create database connection
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def debug_automation_deletion():
    """Debug automation deletion issues"""
    db = SessionLocal()
    
    try:
        print("🔍 Debugging automation deletion for automation ID 1...")
        
        # Check if automation exists
        automation = db.execute(text("""
            SELECT id, name, description, status, created_at 
            FROM automations 
            WHERE id = 1
        """)).fetchone()
        
        if not automation:
            print("❌ Automation with ID 1 not found")
            return
        
        print(f"✅ Automation found: {automation[1]} (ID: {automation[0]})")
        
        # Check for related records that might prevent deletion
        print("\n🔍 Checking related records...")
        
        # Check UserAutomations
        user_automations = db.execute(text("""
            SELECT COUNT(*) FROM user_automations WHERE automation_id = 1
        """)).fetchone()
        print(f"   UserAutomations: {user_automations[0]}")
        
        # Check Payments
        payments = db.execute(text("""
            SELECT COUNT(*) FROM payments WHERE automation_id = 1
        """)).fetchone()
        print(f"   Payments: {payments[0]}")
        
        # Check OpenAI Keys
        openai_keys = db.execute(text("""
            SELECT COUNT(*) FROM openai_keys WHERE automation_id = 1
        """)).fetchone()
        print(f"   OpenAI Keys: {openai_keys[0]}")
        
        # Check KB Templates
        kb_templates = db.execute(text("""
            SELECT COUNT(*) FROM kb_templates WHERE automation_id = 1
        """)).fetchone()
        print(f"   KB Templates: {kb_templates[0]}")
        
        # Check KB Status History
        kb_status = db.execute(text("""
            SELECT COUNT(*) FROM kb_status_history WHERE automation_id = 1
        """)).fetchone()
        print(f"   KB Status History: {kb_status[0]}")
        
        # Check if any tables have foreign key constraints
        print("\n🔍 Checking database schema...")
        
        # Get table info for SQLite
        if DATABASE_URL.startswith("sqlite"):
            tables = db.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name LIKE '%automation%'
            """)).fetchall()
            print(f"   Automation-related tables: {[t[0] for t in tables]}")
            
            # Check foreign key constraints
            fk_info = db.execute(text("""
                PRAGMA foreign_key_list(automations)
            """)).fetchall()
            if fk_info:
                print(f"   Foreign keys in automations table: {fk_info}")
            else:
                print("   No foreign keys found in automations table")
        
        print("\n💡 Recommendations:")
        if user_automations[0] > 0:
            print("   - Automation has user connections. Consider deactivating users first.")
        if payments[0] > 0:
            print("   - Automation has payment records. These need to be handled carefully.")
        if openai_keys[0] > 0:
            print("   - Automation has OpenAI keys. These will be deleted with the automation.")
        
        print("\n🔧 To fix the deletion issue:")
        print("   1. If there are user connections, deactivate them first")
        print("   2. If you want to force delete, uncomment the force delete code in the endpoint")
        print("   3. Check server logs for the exact error message")
            
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_automation_deletion()
