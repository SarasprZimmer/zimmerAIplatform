#!/usr/bin/env python3
"""
Migration script to add unique constraint for telegram_bot_token in user_automations table
"""

import sqlite3
import os

def migrate_bot_token_uniqueness():
    """Add unique constraint for telegram_bot_token in user_automations table"""
    db_path = "zimmer_dashboard.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found")
        return False
    
    print("Starting bot token uniqueness migration...")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if unique constraint already exists
        cursor.execute("PRAGMA index_list(user_automations)")
        indexes = [index[1] for index in cursor.fetchall()]
        
        print(f"Current indexes: {indexes}")
        
        # Check if our unique constraint already exists
        if 'uq_telegram_bot_token' in indexes:
            print("✅ Unique constraint for telegram_bot_token already exists")
            return True
        
        # Check for duplicate bot tokens before adding constraint
        print("Checking for existing duplicate bot tokens...")
        cursor.execute("""
            SELECT telegram_bot_token, COUNT(*) as count
            FROM user_automations 
            WHERE telegram_bot_token IS NOT NULL
            GROUP BY telegram_bot_token 
            HAVING COUNT(*) > 1
        """)
        
        duplicates = cursor.fetchall()
        if duplicates:
            print("❌ Found duplicate bot tokens that need to be resolved:")
            for token, count in duplicates:
                print(f"   Token: {token} (used {count} times)")
            print("Please resolve duplicates before adding unique constraint")
            return False
        
        # Add unique constraint
        print("Adding unique constraint for telegram_bot_token...")
        cursor.execute("""
            CREATE UNIQUE INDEX uq_telegram_bot_token 
            ON user_automations(telegram_bot_token)
        """)
        
        # Commit changes
        conn.commit()
        
        # Verify migration
        cursor.execute("PRAGMA index_list(user_automations)")
        indexes_after = [index[1] for index in cursor.fetchall()]
        
        if 'uq_telegram_bot_token' in indexes_after:
            print("✅ Unique constraint for telegram_bot_token added successfully")
            return True
        else:
            print("❌ Failed to add unique constraint")
            return False
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def test_bot_token_uniqueness():
    """Test the unique constraint by attempting to insert duplicate tokens"""
    db_path = "zimmer_dashboard.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found")
        return False
    
    print("\nTesting bot token uniqueness...")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get a sample user and automation for testing
        cursor.execute("SELECT id FROM users LIMIT 1")
        user_result = cursor.fetchone()
        if not user_result:
            print("❌ No users found in database")
            return False
        
        cursor.execute("SELECT id FROM automations LIMIT 1")
        automation_result = cursor.fetchone()
        if not automation_result:
            print("❌ No automations found in database")
            return False
        
        user_id = user_result[0]
        automation_id = automation_result[0]
        test_token = "test_bot_token_12345"
        
        # Insert first record with test token
        print(f"Inserting first record with token: {test_token}")
        cursor.execute("""
            INSERT INTO user_automations (user_id, automation_id, telegram_bot_token, tokens_remaining, demo_tokens, is_demo_active, demo_expired, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, automation_id, test_token, 100, 5, True, False, 'active'))
        
        # Try to insert second record with same token (should fail)
        print(f"Attempting to insert second record with same token: {test_token}")
        try:
            cursor.execute("""
                INSERT INTO user_automations (user_id, automation_id, telegram_bot_token, tokens_remaining, demo_tokens, is_demo_active, demo_expired, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, automation_id, test_token, 100, 5, True, False, 'active'))
            
            print("❌ Unique constraint test failed - duplicate token was inserted")
            conn.rollback()
            return False
            
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                print("✅ Unique constraint test passed - duplicate token was rejected")
                conn.rollback()
                return True
            else:
                print(f"❌ Unexpected error: {e}")
                conn.rollback()
                return False
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 Bot Token Uniqueness Migration")
    print("=" * 50)
    
    # Run migration
    success = migrate_bot_token_uniqueness()
    
    if success:
        # Test the constraint
        test_success = test_bot_token_uniqueness()
        
        if test_success:
            print("\n🎉 Migration and testing completed successfully!")
        else:
            print("\n⚠️ Migration completed but testing failed")
    else:
        print("\n❌ Migration failed") 