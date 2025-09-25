#!/usr/bin/env python3
"""
Script to fix existing staff users by auto-verifying their emails
"""
import sys
sys.path.append('.')

from database import SessionLocal
from models.user import User, UserRole
from datetime import datetime

def fix_staff_emails():
    """Auto-verify emails for existing staff users"""
    db = SessionLocal()
    
    try:
        # Get all staff users with unverified emails
        staff_users = db.query(User).filter(
            User.role.in_([UserRole.support_staff, UserRole.manager, UserRole.technical_team]),
            User.email_verified_at.is_(None)
        ).all()
        
        print(f"Found {len(staff_users)} staff users with unverified emails:")
        
        for user in staff_users:
            print(f"  - {user.email} ({user.role})")
        
        if len(staff_users) > 0:
            confirm = input(f"\nAuto-verify emails for {len(staff_users)} staff users? (y/N): ")
            if confirm.lower() in ['y', 'yes']:
                # Update all staff users to have verified emails
                for user in staff_users:
                    user.email_verified_at = datetime.utcnow()
                
                db.commit()
                print(f"✅ Successfully verified emails for {len(staff_users)} staff users")
            else:
                print("❌ Operation cancelled")
        else:
            print("✅ All staff users already have verified emails")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_staff_emails()
