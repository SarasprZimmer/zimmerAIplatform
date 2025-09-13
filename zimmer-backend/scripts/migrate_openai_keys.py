#!/usr/bin/env python3
"""
Migration script for OpenAI key management tables
Creates openai_keys and openai_key_usage tables if they don't exist
"""

import sys
import os
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DATABASE_URL

def create_openai_keys_table(engine):
    """Create the openai_keys table"""
    with engine.connect() as conn:
        # Check if table exists
        inspector = inspect(engine)
        if 'openai_keys' in inspector.get_table_names():
            print("✅ Table 'openai_keys' already exists")
            return
        
        # Create the table
        create_table_sql = """
        CREATE TABLE openai_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            automation_id INTEGER NOT NULL,
            alias VARCHAR(100) NOT NULL,
            key_encrypted TEXT NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'active',
            rpm_limit INTEGER,
            daily_token_limit BIGINT,
            used_requests_minute INTEGER DEFAULT 0,
            used_tokens_today BIGINT DEFAULT 0,
            last_minute_window DATETIME,
            last_used_at DATETIME,
            failure_count INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (automation_id) REFERENCES automations (id)
        )
        """
        
        try:
            conn.execute(text(create_table_sql))
            conn.commit()
            print("✅ Created table 'openai_keys'")
        except Exception as e:
            print(f"❌ Error creating openai_keys table: {e}")
            return False
        
        # Create index
        try:
            index_sql = """
            CREATE INDEX idx_openai_keys_automation_status 
            ON openai_keys (automation_id, status)
            """
            conn.execute(text(index_sql))
            conn.commit()
            print("✅ Created index on openai_keys (automation_id, status)")
        except Exception as e:
            print(f"⚠️  Warning: Could not create index: {e}")
        
        return True

def create_openai_key_usage_table(engine):
    """Create the openai_key_usage table"""
    with engine.connect() as conn:
        # Check if table exists
        inspector = inspect(engine)
        if 'openai_key_usage' in inspector.get_table_names():
            print("✅ Table 'openai_key_usage' already exists")
            return
        
        # Create the table
        create_table_sql = """
        CREATE TABLE openai_key_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            openai_key_id INTEGER NOT NULL,
            automation_id INTEGER NOT NULL,
            user_id INTEGER,
            model VARCHAR(100) NOT NULL,
            prompt_tokens INTEGER NOT NULL,
            completion_tokens INTEGER NOT NULL,
            total_tokens INTEGER NOT NULL,
            status VARCHAR(10) NOT NULL,
            error_code VARCHAR(50),
            error_message TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (openai_key_id) REFERENCES openai_keys (id),
            FOREIGN KEY (automation_id) REFERENCES automations (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
        
        try:
            conn.execute(text(create_table_sql))
            conn.commit()
            print("✅ Created table 'openai_key_usage'")
        except Exception as e:
            print(f"❌ Error creating openai_key_usage table: {e}")
            return False
        
        return True

def main():
    """Main migration function"""
    print("🚀 Starting OpenAI Keys Migration...")
    print(f"📊 Database: {DATABASE_URL}")
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        
        # Create tables
        success1 = create_openai_keys_table(engine)
        success2 = create_openai_key_usage_table(engine)
        
        if success1 and success2:
            print("\n🎉 Migration completed successfully!")
            print("\n📋 Summary:")
            print("   • openai_keys table: ✅")
            print("   • openai_key_usage table: ✅")
            print("   • Indexes: ✅")
            print("\n🔧 Next steps:")
            print("   1. Set OAI_ENCRYPTION_SECRET in your .env file")
            print("   2. Restart the backend server")
            print("   3. Use the admin panel to add OpenAI keys")
        else:
            print("\n❌ Migration failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Migration error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
