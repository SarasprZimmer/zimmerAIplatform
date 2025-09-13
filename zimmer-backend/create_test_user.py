#!/usr/bin/env python3
"""
Create a test user for development
"""
import sys
import os

# Add current directory to path
sys.path.append('.')

from database import SessionLocal, engine, Base
from models.user import User
from utils.security import hash_password
import sqlalchemy.exc

def create_test_user():
    """Create a test user for development"""
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        print("Database tables created/verified")
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Check if test user exists
            existing_user = db.query(User).filter(User.email == 'test@example.com').first()
            if existing_user:
                print('✅ Test user already exists: test@example.com')
                print(f'   Name: {existing_user.name}')
                print(f'   Active: {existing_user.is_active}')
                return True
            
            # Create test user
            test_user = User(
                name='Test User',
                email='test@example.com',
                password_hash=hash_password('test123'),
                is_active=True,
                role='support_staff'  # Use default role
            )
            
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            print('✅ Test user created successfully!')
            print('   Email: test@example.com')
            print('   Password: test123')
            print(f'   ID: {test_user.id}')
            print(f'   Role: {test_user.role}')
            
            return True
            
        except Exception as e:
            db.rollback()
            print(f'❌ Error creating test user: {e}')
            return False
        finally:
            db.close()
            
    except Exception as e:
        print(f'❌ Database connection error: {e}')
        return False

if __name__ == "__main__":
    success = create_test_user()
    sys.exit(0 if success else 1)
