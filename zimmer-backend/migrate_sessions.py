#!/usr/bin/env python3
"""
Migration script to add sessions table to existing databases.
Run this script to add the new table without affecting existing data.
"""

import sqlite3
import os
from pathlib import Path


def migrate_sessions():
    """Add sessions table to the database"""
    
    # Database path
    db_path = Path("zimmer_dashboard.db")
    
    if not db_path.exists():
        print("❌ Database file not found. Please run this script from the backend directory.")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("🔍 Checking if sessions table exists...")
        
        # Check if table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='sessions'
        """)
        
        if cursor.fetchone():
            print("✅ sessions table already exists. Skipping migration.")
            return True
        
        print("📝 Creating sessions table...")
        
        # Create sessions table
        cursor.execute("""
            CREATE TABLE sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                refresh_token_hash TEXT NOT NULL,
                user_agent TEXT,
                ip_address TEXT,
                last_used_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                expires_at DATETIME NOT NULL,
                revoked_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Create indexes for performance
        print("📊 Creating indexes...")
        
        # Index on user_id
        cursor.execute("""
            CREATE INDEX ix_sessions_user_id 
            ON sessions (user_id)
        """)
        
        # Index on refresh_token_hash
        cursor.execute("""
            CREATE INDEX ix_sessions_refresh_token_hash 
            ON sessions (refresh_token_hash)
        """)
        
        # Index on last_used_at
        cursor.execute("""
            CREATE INDEX ix_sessions_last_used_at 
            ON sessions (last_used_at)
        """)
        
        # Index on expires_at
        cursor.execute("""
            CREATE INDEX ix_sessions_expires_at 
            ON sessions (expires_at)
        """)
        
        # Composite index for user_id and revoked_at
        cursor.execute("""
            CREATE INDEX idx_user_active_sessions 
            ON sessions (user_id, revoked_at)
        """)
        
        # Composite index for expires_at and revoked_at
        cursor.execute("""
            CREATE INDEX idx_session_expiry 
            ON sessions (expires_at, revoked_at)
        """)
        
        # Commit changes
        conn.commit()
        
        print("✅ sessions table created successfully!")
        print("✅ All indexes created successfully!")
        
        # Verify table structure
        cursor.execute("PRAGMA table_info(sessions)")
        columns = cursor.fetchall()
        
        print("\n📋 Table structure:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
        
        # Verify indexes
        cursor.execute("PRAGMA index_list(sessions)")
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
            WHERE type='table' AND name='sessions'
        """)
        
        if not cursor.fetchone():
            print("❌ sessions table not found after migration!")
            return False
        
        # Check table structure
        cursor.execute("PRAGMA table_info(sessions)")
        columns = cursor.fetchall()
        
        expected_columns = [
            'id', 'user_id', 'refresh_token_hash', 'user_agent', 'ip_address',
            'last_used_at', 'expires_at', 'revoked_at', 'created_at'
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
    print("🚀 Sessions Migration Script")
    print("=" * 50)
    
    # Run migration
    if migrate_sessions():
        print("\n🔍 Verifying migration...")
        if verify_migration():
            print("\n🎉 Migration completed successfully!")
            print("\n📋 Next steps:")
            print("  1. Restart your backend server")
            print("  2. Test the new endpoints:")
            print("     - POST /api/auth/login")
            print("     - POST /api/auth/refresh")
            print("     - POST /api/auth/logout")
            print("     - POST /api/auth/logout-all")
            print("  3. Run tests: python test_auth_sessions.py")
        else:
            print("\n❌ Migration verification failed!")
    else:
        print("\n❌ Migration failed!")
