#!/usr/bin/env python3
"""
Migration script to add token_adjustments table to existing databases.
Run this script to add the new table without affecting existing data.
"""

import sqlite3
import os
from pathlib import Path


def migrate_token_adjustments():
    """Add token_adjustments table to the database"""
    
    # Database path
    db_path = Path("zimmer_dashboard.db")
    
    if not db_path.exists():
        print("❌ Database file not found. Please run this script from the backend directory.")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("🔍 Checking if token_adjustments table exists...")
        
        # Check if table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='token_adjustments'
        """)
        
        if cursor.fetchone():
            print("✅ token_adjustments table already exists. Skipping migration.")
            return True
        
        print("📝 Creating token_adjustments table...")
        
        # Create token_adjustments table
        cursor.execute("""
            CREATE TABLE token_adjustments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_automation_id INTEGER NOT NULL,
                admin_id INTEGER NOT NULL,
                delta_tokens INTEGER NOT NULL,
                reason VARCHAR(255) NOT NULL,
                note TEXT,
                related_payment_id INTEGER,
                idempotency_key VARCHAR(64) UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (user_automation_id) REFERENCES user_automations (id),
                FOREIGN KEY (admin_id) REFERENCES users (id),
                FOREIGN KEY (related_payment_id) REFERENCES payments (id)
            )
        """)
        
        # Create indexes for performance
        print("📊 Creating indexes...")
        
        # Index on user_id, user_automation_id, created_at
        cursor.execute("""
            CREATE INDEX idx_user_automation_created 
            ON token_adjustments (user_id, user_automation_id, created_at)
        """)
        
        # Index on user_id
        cursor.execute("""
            CREATE INDEX ix_token_adjustments_user_id 
            ON token_adjustments (user_id)
        """)
        
        # Index on user_automation_id
        cursor.execute("""
            CREATE INDEX ix_token_adjustments_user_automation_id 
            ON token_adjustments (user_automation_id)
        """)
        
        # Index on admin_id
        cursor.execute("""
            CREATE INDEX ix_token_adjustments_admin_id 
            ON token_adjustments (admin_id)
        """)
        
        # Index on related_payment_id
        cursor.execute("""
            CREATE INDEX ix_token_adjustments_related_payment_id 
            ON token_adjustments (related_payment_id)
        """)
        
        # Index on idempotency_key
        cursor.execute("""
            CREATE INDEX ix_token_adjustments_idempotency_key 
            ON token_adjustments (idempotency_key)
        """)
        
        # Commit changes
        conn.commit()
        
        print("✅ token_adjustments table created successfully!")
        print("✅ All indexes created successfully!")
        
        # Verify table structure
        cursor.execute("PRAGMA table_info(token_adjustments)")
        columns = cursor.fetchall()
        
        print("\n📋 Table structure:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
        
        # Verify indexes
        cursor.execute("PRAGMA index_list(token_adjustments)")
        indexes = cursor.fetchall()
        
        print("\n🔍 Indexes created:")
        for idx in indexes:
            print(f"  - {idx[1]}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        if conn:
            conn.close()


def verify_migration():
    """Verify that the migration was successful"""
    
    db_path = Path("zimmer_dashboard.db")
    
    if not db_path.exists():
        print("❌ Database file not found.")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='token_adjustments'
        """)
        
        if not cursor.fetchone():
            print("❌ token_adjustments table not found after migration!")
            return False
        
        # Check table structure
        cursor.execute("PRAGMA table_info(token_adjustments)")
        columns = cursor.fetchall()
        
        expected_columns = [
            'id', 'user_id', 'user_automation_id', 'admin_id', 
            'delta_tokens', 'reason', 'note', 'related_payment_id', 
            'idempotency_key', 'created_at'
        ]
        
        actual_columns = [col[1] for col in columns]
        
        if set(actual_columns) != set(expected_columns):
            print("❌ Table structure mismatch!")
            print(f"Expected: {expected_columns}")
            print(f"Actual: {actual_columns}")
            return False
        
        print("✅ Migration verification successful!")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    print("🚀 Token Adjustments Migration Script")
    print("=" * 50)
    
    # Run migration
    if migrate_token_adjustments():
        print("\n🔍 Verifying migration...")
        if verify_migration():
            print("\n🎉 Migration completed successfully!")
            print("\n📋 Next steps:")
            print("  1. Restart your backend server")
            print("  2. Test the new endpoints:")
            print("     - POST /api/admin/tokens/adjust")
            print("     - GET /api/admin/tokens/adjustments")
            print("     - GET /api/admin/tokens/balance/{user_automation_id}")
            print("  3. Run tests: python test_token_adjustments.py")
        else:
            print("\n❌ Migration verification failed!")
    else:
        print("\n❌ Migration failed!")
