#!/usr/bin/env python3
"""
Migration script to create KB status history table
"""

import sqlite3
from sqlalchemy import create_engine, text
from database import SessionLocal, engine
from models.kb_status_history import KBStatusHistory

def create_kb_history_table():
    """Create the KB status history table"""
    print("=== Creating KB Status History Table ===")
    
    try:
        # Create table using SQLAlchemy
        KBStatusHistory.__table__.create(engine)
        print("✅ KB Status History table created successfully!")
        
        # Verify table structure
        conn = sqlite3.connect('zimmer_dashboard.db')
        cur = conn.cursor()
        
        cur.execute("PRAGMA table_info(kb_status_history)")
        columns = cur.fetchall()
        print("Table structure:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")

def add_sample_history_data():
    """Add sample history data for testing"""
    print("\n=== Adding Sample History Data ===")
    
    db = SessionLocal()
    
    try:
        # Check if we have any automations and users
        from models.automation import Automation
        from models.user import User
        from models.user_automation import UserAutomation
        
        automations = db.query(Automation).all()
        users = db.query(User).all()
        
        if not automations or not users:
            print("⚠️ No automations or users found. Skipping sample data.")
            return
        
        # Get first automation and user
        automation = automations[0]
        user = users[0]
        
        # Check if user has this automation
        user_automation = db.query(UserAutomation).filter(
            UserAutomation.user_id == user.id,
            UserAutomation.automation_id == automation.id
        ).first()
        
        if not user_automation:
            print("⚠️ User doesn't have this automation. Creating sample user automation...")
            user_automation = UserAutomation(
                user_id=user.id,
                automation_id=automation.id,
                status="active",
                tokens_remaining=1000
            )
            db.add(user_automation)
            db.commit()
            db.refresh(user_automation)
        
        # Add sample history records
        from datetime import datetime, timedelta
        import random
        
        health_statuses = ["healthy", "warning", "problematic"]
        
        for i in range(10):
            # Create records for the last 10 days
            timestamp = datetime.utcnow() - timedelta(days=i)
            health = random.choice(health_statuses)
            backup_status = random.choice([True, False])
            
            history_record = KBStatusHistory(
                user_id=user.id,
                user_automation_id=user_automation.id,
                automation_id=automation.id,
                kb_health=health,
                backup_status=backup_status,
                error_logs=["Sample error log"] if health == "problematic" else None,
                timestamp=timestamp
            )
            
            db.add(history_record)
            print(f"  Added history record for {timestamp.strftime('%Y-%m-%d')}: {health}")
        
        db.commit()
        print(f"✅ Added {10} sample history records!")
        
    except Exception as e:
        print(f"❌ Error adding sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_kb_history_table()
    add_sample_history_data() 