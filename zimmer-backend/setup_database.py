#!/usr/bin/env python3
"""
Database Setup Script for Zimmer Platform
This script initializes the PostgreSQL database for production use.
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

def check_postgresql_connection():
    """Check if PostgreSQL is running and accessible"""
    print("🔍 Checking PostgreSQL connection...")
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    if not database_url.startswith("postgresql"):
        print("❌ DATABASE_URL is not configured for PostgreSQL")
        return False
    
    print(f"✅ Database URL configured: {database_url.split('@')[1] if '@' in database_url else 'localhost'}")
    return True

def create_database():
    """Create the database if it doesn't exist"""
    print("🗄️ Setting up database...")
    
    # Extract database connection details
    database_url = os.getenv("DATABASE_URL", "postgresql+psycopg2://zimmer:zimmer@localhost:5432/zimmer")
    
    # Parse the URL
    if "postgresql+psycopg2://" in database_url:
        url_part = database_url.replace("postgresql+psycopg2://", "")
    elif "postgresql://" in database_url:
        url_part = database_url.replace("postgresql://", "")
    else:
        print("❌ Invalid database URL format")
        return False
    
    if "@" in url_part:
        auth_part, host_part = url_part.split("@", 1)
        if ":" in auth_part:
            username, password = auth_part.split(":", 1)
        else:
            username = auth_part
            password = ""
        
        if "/" in host_part:
            host_port, database = host_part.split("/", 1)
            if ":" in host_port:
                host, port = host_port.split(":", 1)
            else:
                host = host_port
                port = "5432"
        else:
            host = host_part
            port = "5432"
            database = "zimmer"
    else:
        print("❌ Could not parse database URL")
        return False
    
    # Create database using psql
    create_db_command = f'psql -h {host} -p {port} -U {username} -d postgres -c "CREATE DATABASE {database};" 2>/dev/null || echo "Database may already exist"'
    
    if run_command(create_db_command, f"Creating database '{database}'"):
        print(f"✅ Database '{database}' is ready")
        return True
    else:
        print(f"❌ Failed to create database '{database}'")
        return False

def run_migrations():
    """Run Alembic migrations to create/update tables"""
    print("📊 Running database migrations...")
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Run alembic upgrade
    if run_command("alembic upgrade head", "Running Alembic migrations"):
        print("✅ Database tables created/updated successfully")
        return True
    else:
        print("❌ Failed to run migrations")
        return False

def verify_tables():
    """Verify that all required tables exist"""
    print("🔍 Verifying database tables...")
    
    try:
        from database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Get list of tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """))
            
            tables = [row[0] for row in result]
            
            # Expected tables
            expected_tables = [
                'users', 'automations', 'tickets', 'ticket_messages', 
                'payments', 'knowledge_entries', 'kb_templates', 
                'kb_status_history', 'openai_keys', 'openai_key_usage',
                'password_reset_tokens', 'backup_logs', 'fallback_logs',
                'token_usage', 'user_automations', 'token_adjustments',
                'sessions', 'notifications', 'discount_codes',
                'discount_code_automations', 'discount_redemptions',
                'alembic_version'
            ]
            
            missing_tables = [table for table in expected_tables if table not in tables]
            
            if missing_tables:
                print(f"❌ Missing tables: {', '.join(missing_tables)}")
                return False
            else:
                print(f"✅ All {len(tables)} tables found")
                return True
                
    except Exception as e:
        print(f"❌ Error verifying tables: {e}")
        return False

def create_admin_user():
    """Create a default admin user if none exists"""
    print("👤 Checking for admin user...")
    
    try:
        from database import SessionLocal
        from models.user import User, UserRole
        from utils.password import hash_password
        
        db = SessionLocal()
        
        # Check if any admin users exist
        admin_count = db.query(User).filter(User.role.in_([
            UserRole.manager, 
            UserRole.technical_team, 
            UserRole.support_staff
        ])).count()
        
        if admin_count > 0:
            print(f"✅ Found {admin_count} admin user(s)")
            db.close()
            return True
        
        # Create default admin user
        admin_user = User(
            name="System Administrator",
            email="admin@zimmer.local",
            password_hash=hash_password("admin123"),
            role=UserRole.manager,
            is_active=True,
            email_verified_at=None
        )
        
        db.add(admin_user)
        db.commit()
        db.close()
        
        print("✅ Default admin user created (admin@zimmer.local / admin123)")
        print("⚠️  IMPORTANT: Change the default password in production!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Starting Zimmer Platform Database Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("alembic.ini").exists():
        print("❌ alembic.ini not found. Please run this script from the backend directory.")
        sys.exit(1)
    
    # Step 1: Check PostgreSQL connection
    if not check_postgresql_connection():
        print("❌ PostgreSQL connection check failed")
        sys.exit(1)
    
    # Step 2: Create database
    if not create_database():
        print("❌ Database creation failed")
        sys.exit(1)
    
    # Step 3: Run migrations
    if not run_migrations():
        print("❌ Migration failed")
        sys.exit(1)
    
    # Step 4: Verify tables
    if not verify_tables():
        print("❌ Table verification failed")
        sys.exit(1)
    
    # Step 5: Create admin user
    if not create_admin_user():
        print("❌ Admin user creation failed")
        sys.exit(1)
    
    print("=" * 50)
    print("🎉 Database setup completed successfully!")
    print("")
    print("📋 Next steps:")
    print("   1. Update the admin user password")
    print("   2. Configure environment variables")
    print("   3. Start the application")
    print("")
    print("🔐 Default admin credentials:")
    print("   Email: admin@zimmer.local")
    print("   Password: admin123")
    print("   ⚠️  CHANGE THIS PASSWORD IMMEDIATELY!")

if __name__ == "__main__":
    main()
