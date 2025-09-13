#!/usr/bin/env python3
"""
Debug script to identify server startup issues
"""

import sys
import os
import traceback

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all imports to identify issues"""
    print("🔍 Testing imports...")
    
    try:
        print("  Testing database...")
        from database import Base, engine
        print("  ✅ Database imported successfully")
    except Exception as e:
        print(f"  ❌ Database import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("  Testing models...")
        # Import specific models instead of using *
        from models.user import User
        from models.automation import Automation
        from models.ticket import Ticket
        print("  ✅ Models imported successfully")
    except Exception as e:
        print(f"  ❌ Models import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("  Testing routers...")
        from routers import users, admin, fallback, knowledge, telegram, ticket, ticket_message
        print("  ✅ Routers imported successfully")
    except Exception as e:
        print(f"  ❌ Routers import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("  Testing utils...")
        from utils.jwt import JWT_SECRET_KEY
        from utils.security import hash_password
        print("  ✅ Utils imported successfully")
    except Exception as e:
        print(f"  ❌ Utils import failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_database_connection():
    """Test database connection"""
    print("\n🗄️ Testing database connection...")
    
    try:
        from database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("  ✅ Database connection successful")
            return True
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        traceback.print_exc()
        return False

def test_environment():
    """Test environment variables"""
    print("\n🔧 Testing environment...")
    
    required_vars = ["JWT_SECRET_KEY", "OAI_ENCRYPTION_SECRET"]
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value[:20]}...")
        else:
            print(f"  ❌ {var}: NOT SET")
            return False
    
    return True

def test_app_creation():
    """Test FastAPI app creation"""
    print("\n🚀 Testing FastAPI app creation...")
    
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.middleware.trustedhost import TrustedHostMiddleware
        
        app = FastAPI(
            title="Zimmer Internal Management Dashboard",
            description="Backend API for Zimmer's internal management and automation tracking",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        print("  ✅ FastAPI app created successfully")
        return True
    except Exception as e:
        print(f"  ❌ FastAPI app creation failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main debug function"""
    print("🔍 Starting Debug Analysis")
    print("=" * 50)
    
    # Test environment
    if not test_environment():
        print("\n❌ Environment test failed")
        return False
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed")
        return False
    
    # Test database
    if not test_database_connection():
        print("\n❌ Database test failed")
        return False
    
    # Test app creation
    if not test_app_creation():
        print("\n❌ App creation test failed")
        return False
    
    print("\n✅ All debug tests passed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
