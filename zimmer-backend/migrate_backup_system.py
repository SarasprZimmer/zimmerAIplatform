#!/usr/bin/env python3
"""
Migration script to create backup system tables and add sample data
"""

import sqlite3
from sqlalchemy import create_engine, text
from database import SessionLocal, engine
from models.backup import BackupLog, BackupStatus
from services.backup_service import BackupService
from datetime import datetime, timedelta
import random

def create_backup_table():
    """Create the backup logs table"""
    print("=== Creating Backup Logs Table ===")
    
    try:
        # Create table using SQLAlchemy
        BackupLog.__table__.create(engine)
        print("✅ Backup logs table created successfully!")
        
        # Verify table structure
        conn = sqlite3.connect('zimmer_dashboard.db')
        cur = conn.cursor()
        
        cur.execute("PRAGMA table_info(backup_logs)")
        columns = cur.fetchall()
        print("Table structure:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")

def add_sample_backup_data():
    """Add sample backup data for testing"""
    print("\n=== Adding Sample Backup Data ===")
    
    db = SessionLocal()
    
    try:
        # Create sample backup records for the last 30 days
        for i in range(30):
            # Create backup date (going backwards from today)
            backup_date = datetime.now() - timedelta(days=i)
            
            # Randomly determine if backup was successful
            is_successful = random.choice([True, True, True, False])  # 75% success rate
            
            if is_successful:
                file_name = f"zimmer_backup_{backup_date.strftime('%Y%m%d_%H%M%S')}.sql"
                file_size = random.randint(1024 * 1024, 10 * 1024 * 1024)  # 1MB to 10MB
                status = BackupStatus.success
                verified = random.choice([True, False])  # 50% verified
            else:
                file_name = f"failed_backup_{backup_date.strftime('%Y%m%d_%H%M%S')}"
                file_size = 0
                status = BackupStatus.failed
                verified = False
            
            backup_log = BackupLog(
                backup_date=backup_date,
                file_name=file_name,
                file_size=file_size,
                status=status,
                storage_location="local",
                verified=verified
            )
            
            db.add(backup_log)
            print(f"  Added backup record for {backup_date.strftime('%Y-%m-%d')}: {status.value}")
        
        db.commit()
        print(f"✅ Added {30} sample backup records!")
        
    except Exception as e:
        print(f"❌ Error adding sample data: {e}")
        db.rollback()
    finally:
        db.close()

def test_backup_service():
    """Test the backup service functionality"""
    print("\n=== Testing Backup Service ===")
    
    db = SessionLocal()
    
    try:
        backup_service = BackupService(db)
        
        # Test backup stats
        stats = backup_service.get_backup_stats()
        print(f"Backup stats: {stats}")
        
        # Test manual backup
        print("Testing manual backup...")
        success, message, file_path = backup_service.run_backup()
        print(f"Backup result: {success} - {message}")
        
        if success:
            print(f"Backup file: {file_path}")
        
        # Test cleanup
        print("Testing cleanup...")
        deleted_count, cleaned_files = backup_service.cleanup_old_backups(retention_days=30)
        print(f"Cleanup result: {deleted_count} files deleted")
        
    except Exception as e:
        print(f"❌ Error testing backup service: {e}")
    finally:
        db.close()

def create_backup_directory():
    """Create backups directory"""
    print("\n=== Creating Backups Directory ===")
    
    try:
        from pathlib import Path
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        print(f"✅ Backups directory created: {backup_dir.absolute()}")
    except Exception as e:
        print(f"❌ Error creating backups directory: {e}")

if __name__ == "__main__":
    create_backup_table()
    add_sample_backup_data()
    create_backup_directory()
    test_backup_service() 