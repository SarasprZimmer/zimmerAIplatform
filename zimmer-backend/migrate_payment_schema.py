"""
Migration script to update payment table for Zarinpal integration
"""
import sqlite3
import os
from pathlib import Path

def migrate_payment_schema():
    """Migrate payment table to add new fields for Zarinpal"""
    
    # Get database path
    db_path = Path("zimmer_dashboard.db")
    
    if not db_path.exists():
        print("❌ Database file not found. Please run the backend first to create it.")
        return
    
    print("🔄 Migrating payment table schema...")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(payments)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add new columns if they don't exist
        if "automation_id" not in columns:
            print("➕ Adding automation_id column...")
            cursor.execute("ALTER TABLE payments ADD COLUMN automation_id INTEGER REFERENCES automations(id)")
        
        if "gateway" not in columns:
            print("➕ Adding gateway column...")
            cursor.execute("ALTER TABLE payments ADD COLUMN gateway TEXT DEFAULT 'zarinpal'")
        
        if "authority" not in columns:
            print("➕ Adding authority column...")
            cursor.execute("ALTER TABLE payments ADD COLUMN authority TEXT")
            # Add index for authority
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_authority ON payments(authority)")
        
        if "ref_id" not in columns:
            print("➕ Adding ref_id column...")
            cursor.execute("ALTER TABLE payments ADD COLUMN ref_id TEXT")
        
        if "meta" not in columns:
            print("➕ Adding meta column...")
            cursor.execute("ALTER TABLE payments ADD COLUMN meta TEXT")
        
        # Update amount column type if needed (SQLite doesn't support ALTER COLUMN TYPE easily)
        # We'll handle this in the application layer
        
        # Commit changes
        conn.commit()
        
        print("✅ Payment table migration completed successfully!")
        
        # Show final schema
        cursor.execute("PRAGMA table_info(payments)")
        columns = cursor.fetchall()
        
        print("\n📋 Final payment table schema:")
        for column in columns:
            print(f"   {column[1]} ({column[2]}) - {'NOT NULL' if column[3] else 'NULL'}")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    migrate_payment_schema()
