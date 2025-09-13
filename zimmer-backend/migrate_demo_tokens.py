#!/usr/bin/env python3
"""
Migration script to add demo token columns to user_automations table
"""

import sqlite3
import os

def migrate_demo_tokens():
    """Add demo token columns to user_automations table"""
    db_path = "zimmer_dashboard.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found")
        return False
    
    print("Starting demo tokens migration...")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(user_automations)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"Current columns: {columns}")
        
        # Add new columns if they don't exist
        new_columns = [
            ("demo_tokens", "INTEGER DEFAULT 5"),
            ("is_demo_active", "BOOLEAN DEFAULT 1"),
            ("demo_expired", "BOOLEAN DEFAULT 0")
        ]
        
        for column_name, column_def in new_columns:
            if column_name not in columns:
                print(f"Adding column: {column_name}")
                cursor.execute(f"ALTER TABLE user_automations ADD COLUMN {column_name} {column_def}")
            else:
                print(f"Column {column_name} already exists")
        
        # Update existing records to have demo tokens
        print("Updating existing user automations with demo tokens...")
        cursor.execute("""
            UPDATE user_automations 
            SET demo_tokens = 5, is_demo_active = 1, demo_expired = 0 
            WHERE demo_tokens IS NULL OR is_demo_active IS NULL OR demo_expired IS NULL
        """)
        
        updated_count = cursor.rowcount
        print(f"Updated {updated_count} records")
        
        # Commit changes
        conn.commit()
        
        # Verify migration
        cursor.execute("PRAGMA table_info(user_automations)")
        columns_after = [column[1] for column in cursor.fetchall()]
        print(f"Columns after migration: {columns_after}")
        
        # Check if all required columns exist
        required_columns = ["demo_tokens", "is_demo_active", "demo_expired"]
        missing_columns = [col for col in required_columns if col not in columns_after]
        
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
            return False
        
        print("✅ Demo tokens migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    migrate_demo_tokens() 