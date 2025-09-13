#!/usr/bin/env python3
"""
Initialize Alembic migrations for the Zimmer backend.
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        print(f"✅ {cmd}")
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {cmd}")
        print(f"Error: {e.stderr}")
        return None

def main():
    """Initialize Alembic migrations"""
    print("🚀 Initializing Alembic migrations for Zimmer backend")
    print("=" * 60)
    
    # Get the backend directory
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)
    
    # Check if migrations directory exists
    migrations_dir = backend_dir / "migrations"
    if not migrations_dir.exists():
        print("❌ Migrations directory not found. Please create it first.")
        return 1
    
    # Check if env.py exists
    env_py = migrations_dir / "env.py"
    if not env_py.exists():
        print("❌ env.py not found in migrations directory.")
        return 1
    
    # Initialize Alembic (this will create the alembic_version table)
    print("\n📋 Initializing Alembic...")
    result = run_command("alembic init migrations", cwd=backend_dir)
    if result is None:
        return 1
    
    # Create initial migration
    print("\n📋 Creating initial migration...")
    result = run_command("alembic revision --autogenerate -m 'Initial migration'", cwd=backend_dir)
    if result is None:
        return 1
    
    # Apply the migration
    print("\n📋 Applying initial migration...")
    result = run_command("alembic upgrade head", cwd=backend_dir)
    if result is None:
        return 1
    
    print("\n🎉 Alembic migrations initialized successfully!")
    print("\n📝 Next steps:")
    print("1. Review the generated migration in migrations/versions/")
    print("2. Test the migration with: alembic upgrade head")
    print("3. For future changes, use: alembic revision --autogenerate -m 'Description'")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
