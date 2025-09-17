#!/usr/bin/env python3
"""
Database Migration Script for Zimmer Platform
Ensures all database tables are created and up to date
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"   Error: {e.stderr.strip()}")
        return False

def check_alembic_config():
    """Check if Alembic is properly configured"""
    print("🔍 Checking Alembic configuration...")
    
    if not Path("alembic.ini").exists():
        print("❌ alembic.ini not found")
        return False
    
    if not Path("migrations").exists():
        print("❌ migrations directory not found")
        return False
    
    print("✅ Alembic configuration found")
    return True

def create_migration():
    """Create a new migration if needed"""
    print("📝 Creating migration...")
    
    # Check if there are any pending changes
    result = subprocess.run("alembic check", shell=True, capture_output=True, text=True)
    
    if "No changes detected" in result.stdout:
        print("✅ No changes detected, database is up to date")
        return True
    
    # Create new migration
    if run_command("alembic revision --autogenerate -m 'Update database schema'", "Creating migration"):
        print("✅ Migration created successfully")
        return True
    else:
        print("❌ Failed to create migration")
        return False

def run_migrations():
    """Run all pending migrations"""
    print("📊 Running migrations...")
    
    if run_command("alembic upgrade head", "Running migrations"):
        print("✅ All migrations completed successfully")
        return True
    else:
        print("❌ Migration failed")
        return False

def verify_database():
    """Verify database structure"""
    print("🔍 Verifying database structure...")
    
    try:
        from database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Check if all required tables exist
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """))
            
            tables = [row[0] for row in result]
            
            # Required tables for the application
            required_tables = [
                'alembic_version',  # Alembic version tracking
                'users',           # User management
                'automations',     # Automation services
                'tickets',         # Support tickets
                'ticket_messages', # Ticket messages
                'payments',        # Payment records
                'knowledge_entries', # Knowledge base
                'kb_templates',    # KB templates
                'kb_status_history', # KB status tracking
                'openai_keys',     # OpenAI API keys
                'openai_key_usage', # API key usage
                'password_reset_tokens', # Password reset
                'backup_logs',     # Backup logs
                'fallback_logs',   # Fallback logs
                'token_usage',     # Token usage tracking
                'user_automations', # User automation assignments
                'token_adjustments', # Token adjustments
                'sessions',        # User sessions
                'notifications',   # Notifications
                'discount_codes',  # Discount codes
                'discount_code_automations', # Discount automation links
                'discount_redemptions' # Discount redemptions
            ]
            
            missing_tables = [table for table in required_tables if table not in tables]
            extra_tables = [table for table in tables if table not in required_tables]
            
            print(f"📊 Found {len(tables)} tables in database")
            
            if missing_tables:
                print(f"❌ Missing required tables: {', '.join(missing_tables)}")
                return False
            
            if extra_tables:
                print(f"ℹ️  Extra tables found: {', '.join(extra_tables)}")
            
            print("✅ All required tables present")
            
            # Check table structure for key tables
            key_tables = ['users', 'automations', 'tickets', 'payments']
            for table in key_tables:
                if table in tables:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"   {table}: {count} records")
            
            return True
            
    except Exception as e:
        print(f"❌ Error verifying database: {e}")
        return False

def main():
    """Main migration function"""
    print("🚀 Starting Zimmer Platform Database Migration")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("alembic.ini").exists():
        print("❌ alembic.ini not found. Please run this script from the backend directory.")
        sys.exit(1)
    
    # Step 1: Check Alembic configuration
    if not check_alembic_config():
        print("❌ Alembic configuration check failed")
        sys.exit(1)
    
    # Step 2: Create migration if needed
    if not create_migration():
        print("❌ Migration creation failed")
        sys.exit(1)
    
    # Step 3: Run migrations
    if not run_migrations():
        print("❌ Migration execution failed")
        sys.exit(1)
    
    # Step 4: Verify database
    if not verify_database():
        print("❌ Database verification failed")
        sys.exit(1)
    
    print("=" * 50)
    print("🎉 Database migration completed successfully!")
    print("")
    print("📋 Database is ready for production use")

if __name__ == "__main__":
    main()
