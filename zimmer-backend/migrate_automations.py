#!/usr/bin/env python3
"""
Migration script to update automations table to new schema
"""

import sqlite3
from sqlalchemy import create_engine, text
from database import SessionLocal, engine
from models.automation import Automation, PricingType

def migrate_automations_table():
    """Migrate the automations table to the new schema"""
    print("=== Migrating Automations Table ===")
    
    conn = sqlite3.connect('zimmer_dashboard.db')
    cur = conn.cursor()
    
    try:
        # Check current table structure
        cur.execute("PRAGMA table_info(automations)")
        columns = cur.fetchall()
        column_names = [col[1] for col in columns]
        print(f"Current columns: {column_names}")
        
        # Add missing columns
        if 'pricing_type' not in column_names:
            print("Adding pricing_type column...")
            cur.execute("ALTER TABLE automations ADD COLUMN pricing_type VARCHAR")
            # Set default value for existing rows
            cur.execute("UPDATE automations SET pricing_type = ?", (PricingType.flat_fee.value,))
        
        if 'price_per_token' not in column_names:
            print("Adding price_per_token column...")
            cur.execute("ALTER TABLE automations ADD COLUMN price_per_token FLOAT")
            # Set default value for existing rows
            cur.execute("UPDATE automations SET price_per_token = 0.0")
        
        if 'status' not in column_names:
            print("Adding status column...")
            cur.execute("ALTER TABLE automations ADD COLUMN status BOOLEAN")
            # Set default value for existing rows
            cur.execute("UPDATE automations SET status = 1")
        
        if 'api_endpoint' not in column_names:
            print("Adding api_endpoint column...")
            cur.execute("ALTER TABLE automations ADD COLUMN api_endpoint VARCHAR")
        
        if 'updated_at' not in column_names:
            print("Adding updated_at column...")
            cur.execute("ALTER TABLE automations ADD COLUMN updated_at DATETIME")
            # Copy created_at to updated_at for existing rows
            cur.execute("UPDATE automations SET updated_at = created_at")
        
        # Remove slug column if it exists (not needed in new schema)
        if 'slug' in column_names:
            print("Removing slug column...")
            # SQLite doesn't support DROP COLUMN directly, so we'll recreate the table
            print("Note: slug column exists but SQLite doesn't support DROP COLUMN easily")
            print("Consider recreating the table if slug column is not needed")
        
        conn.commit()
        
        # Verify the new structure
        cur.execute("PRAGMA table_info(automations)")
        new_columns = cur.fetchall()
        print("New table structure:")
        for col in new_columns:
            print(f"  {col[1]} ({col[2]})")
        
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

def recreate_automations_table():
    """Drop and recreate the automations table with correct schema"""
    print("=== Recreating Automations Table ===")
    
    try:
        # Drop existing table using SQLite directly
        conn = sqlite3.connect('zimmer_dashboard.db')
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS automations")
        conn.commit()
        conn.close()
        
        # Create new table using SQLAlchemy
        from models.automation import Automation
        Automation.__table__.create(engine)
        
        print("Automations table recreated successfully!")
        
        # Add sample data
        db = SessionLocal()
        sample_automation = Automation(
            name="Sample Automation",
            description="This is a sample automation for testing",
            pricing_type=PricingType.flat_fee,
            price_per_token=1000.0,
            status=True,
            api_endpoint="https://api.example.com/automation"
        )
        
        db.add(sample_automation)
        db.commit()
        db.refresh(sample_automation)
        
        print(f"Added sample automation with ID: {sample_automation.id}")
        db.close()
        
    except Exception as e:
        print(f"Error recreating table: {e}")

if __name__ == "__main__":
    print("Choose migration option:")
    print("1. Migrate existing table (preserves data)")
    print("2. Recreate table (loses data but clean)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        migrate_automations_table()
    elif choice == "2":
        recreate_automations_table()
    else:
        print("Invalid choice. Exiting.") 