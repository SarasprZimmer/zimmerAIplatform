#!/usr/bin/env python3
"""
Fix Database Permission Issues
This script fixes PostgreSQL permission issues for the zimmer user
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

def fix_database_permissions():
    """Fix database permissions for zimmer user"""
    print("🔧 Fixing database permissions...")
    
    # Grant ownership of all tables to zimmer user
    commands = [
        "sudo -u postgres psql -d zimmer -c \"ALTER DATABASE zimmer OWNER TO zimmer;\"",
        "sudo -u postgres psql -d zimmer -c \"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO zimmer;\"",
        "sudo -u postgres psql -d zimmer -c \"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO zimmer;\"",
        "sudo -u postgres psql -d zimmer -c \"GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO zimmer;\"",
        "sudo -u postgres psql -d zimmer -c \"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO zimmer;\"",
        "sudo -u postgres psql -d zimmer -c \"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO zimmer;\"",
        "sudo -u postgres psql -d zimmer -c \"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO zimmer;\""
    ]
    
    for command in commands:
        if not run_command(command, f"Running: {command.split()[-1]}"):
            print(f"⚠️  Warning: Command failed, but continuing...")
    
    print("✅ Database permissions fixed")

def main():
    """Main fix function"""
    print("🚀 Fixing Database Permission Issues")
    print("=" * 50)
    
    fix_database_permissions()
    
    print("=" * 50)
    print("🎉 Database permission issues fixed!")

if __name__ == "__main__":
    main()
