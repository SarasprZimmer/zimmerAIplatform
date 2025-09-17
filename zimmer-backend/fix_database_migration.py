#!/usr/bin/env python3
"""
Fix Database Migration Issues
This script resolves Alembic migration conflicts when tables already exist
"""

import os
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

def check_alembic_version():
    """Check current Alembic version in database"""
    print("🔍 Checking Alembic version in database...")
    
    try:
        from database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Check if alembic_version table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'alembic_version'
                );
            """))
            
            table_exists = result.scalar()
            
            if table_exists:
                # Get current version
                result = conn.execute(text("SELECT version_num FROM alembic_version;"))
                version = result.scalar()
                print(f"✅ Alembic version found: {version}")
                return version
            else:
                print("❌ Alembic version table not found")
                return None
                
    except Exception as e:
        print(f"❌ Error checking Alembic version: {e}")
        return None

def stamp_database():
    """Stamp the database with current migration version"""
    print("🏷️ Stamping database with current migration version...")
    
    if run_command("alembic stamp head", "Stamping database with current version"):
        print("✅ Database stamped successfully")
        return True
    else:
        print("❌ Failed to stamp database")
        return False

def verify_migration_status():
    """Verify migration status"""
    print("🔍 Verifying migration status...")
    
    if run_command("alembic current", "Checking current migration status"):
        print("✅ Migration status verified")
        return True
    else:
        print("❌ Failed to verify migration status")
        return False

def main():
    """Main fix function"""
    print("🚀 Fixing Database Migration Issues")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("alembic.ini").exists():
        print("❌ alembic.ini not found. Please run this script from the backend directory.")
        return False
    
    # Step 1: Check current Alembic version
    current_version = check_alembic_version()
    
    if current_version is None:
        # No version table exists, stamp the database
        if stamp_database():
            print("✅ Database stamped with current migration version")
        else:
            print("❌ Failed to stamp database")
            return False
    else:
        print(f"✅ Database already has version: {current_version}")
    
    # Step 2: Verify migration status
    if verify_migration_status():
        print("✅ Migration status is correct")
    else:
        print("❌ Migration status verification failed")
        return False
    
    print("=" * 50)
    print("🎉 Database migration issues fixed!")
    return True

if __name__ == "__main__":
    main()
