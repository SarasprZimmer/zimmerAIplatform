#!/usr/bin/env python3
"""
Migration script to add KB monitoring columns to automations table
"""

import sqlite3
from sqlalchemy import create_engine, text
from database import SessionLocal, engine
from models.automation import Automation

def migrate_kb_monitoring_columns():
    """Add KB monitoring columns to automations table"""
    print("=== Migrating KB Monitoring Columns ===")
    
    conn = sqlite3.connect('zimmer_dashboard.db')
    cur = conn.cursor()
    
    try:
        # Check current table structure
        cur.execute("PRAGMA table_info(automations)")
        columns = cur.fetchall()
        column_names = [col[1] for col in columns]
        print(f"Current columns: {column_names}")
        
        # Add missing columns
        if 'api_kb_status_url' not in column_names:
            print("Adding api_kb_status_url column...")
            cur.execute("ALTER TABLE automations ADD COLUMN api_kb_status_url VARCHAR")
        
        if 'api_kb_reset_url' not in column_names:
            print("Adding api_kb_reset_url column...")
            cur.execute("ALTER TABLE automations ADD COLUMN api_kb_reset_url VARCHAR")
        
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

def update_existing_automations():
    """Update existing automations with KB monitoring URLs"""
    print("\n=== Updating Existing Automations ===")
    
    db = SessionLocal()
    
    try:
        # Get all automations
        automations = db.query(Automation).all()
        
        for automation in automations:
            print(f"Updating automation: {automation.name}")
            
            # Set KB monitoring URLs based on automation name
            if "agency" in automation.name.lower():
                automation.api_kb_status_url = f"{automation.api_endpoint}/api/kb-status"
                automation.api_kb_reset_url = f"{automation.api_endpoint}/api/kb-reset"
            elif "seo" in automation.name.lower():
                automation.api_kb_status_url = f"{automation.api_endpoint}/api/kb-status"
                automation.api_kb_reset_url = f"{automation.api_endpoint}/api/kb-reset"
            elif "travel" in automation.name.lower():
                automation.api_kb_status_url = f"{automation.api_endpoint}/api/kb-status"
                automation.api_kb_reset_url = f"{automation.api_endpoint}/api/kb-reset"
            else:
                # Default URLs for other automations
                automation.api_kb_status_url = f"{automation.api_endpoint}/api/kb-status"
                automation.api_kb_reset_url = f"{automation.api_endpoint}/api/kb-reset"
            
            print(f"  KB Status URL: {automation.api_kb_status_url}")
            print(f"  KB Reset URL: {automation.api_kb_reset_url}")
        
        db.commit()
        print(f"Updated {len(automations)} automations!")
        
    except Exception as e:
        print(f"Error updating automations: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_kb_monitoring_columns()
    update_existing_automations() 