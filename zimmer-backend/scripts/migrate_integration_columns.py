#!/usr/bin/env python3
"""
Migration script to add Automation Integration Contract columns.
Adds new fields to automations and user_automations tables.
Compatible with both SQLite and PostgreSQL.
"""

import sys
import os
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError

# Add parent directory to path to import database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine

def get_database_type():
    """Detect if we're using SQLite or PostgreSQL"""
    url = str(engine.url)
    if 'sqlite' in url.lower():
        return 'sqlite'
    elif 'postgresql' in url.lower() or 'postgres' in url.lower():
        return 'postgresql'
    else:
        return 'unknown'

def get_column_type(db_type, column_name):
    """Get appropriate column type for the database"""
    if db_type == 'sqlite':
        # SQLite uses TEXT for everything
        return 'TEXT'
    elif db_type == 'postgresql':
        # PostgreSQL uses specific types
        if column_name == 'provisioned_at':
            return 'TIMESTAMP'
        else:
            return 'TEXT'
    else:
        # Default to TEXT for unknown databases
        return 'TEXT'

def get_default_value(db_type, column_name):
    """Get appropriate default value for the database"""
    if column_name == 'integration_status':
        if db_type == 'sqlite':
            return "DEFAULT 'pending'"
        elif db_type == 'postgresql':
            return "DEFAULT 'pending'"
    return ""

def migrate_integration_columns():
    """Add integration contract columns to database tables"""
    
    db_type = get_database_type()
    print(f"🔍 Detected database type: {db_type}")
    
    inspector = inspect(engine)
    changes_made = []
    
    # Define columns to add
    automations_columns = [
        ('api_base_url', 'TEXT'),
        ('api_provision_url', 'TEXT'),
        ('api_usage_url', 'TEXT'),
        ('service_token_hash', 'TEXT')
    ]
    
    user_automations_columns = [
        ('provisioned_at', 'TIMESTAMP' if db_type == 'postgresql' else 'TEXT'),
        ('integration_status', 'TEXT')
    ]
    
    with engine.connect() as conn:
        # Check and add columns to automations table
        print("\n📋 Checking automations table...")
        existing_columns = [col['name'] for col in inspector.get_columns('automations')]
        
        for column_name, column_type in automations_columns:
            if column_name not in existing_columns:
                try:
                    sql_type = get_column_type(db_type, column_name)
                    alter_sql = f"ALTER TABLE automations ADD COLUMN {column_name} {sql_type}"
                    conn.execute(text(alter_sql))
                    conn.commit()
                    changes_made.append(f"✅ Added {column_name} to automations table")
                    print(f"  ✅ Added {column_name}")
                except OperationalError as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"  ⚠️  Column {column_name} already exists")
                    else:
                        print(f"  ❌ Error adding {column_name}: {e}")
            else:
                print(f"  ✓ Column {column_name} already exists")
        
        # Check and add columns to user_automations table
        print("\n📋 Checking user_automations table...")
        existing_columns = [col['name'] for col in inspector.get_columns('user_automations')]
        
        for column_name, column_type in user_automations_columns:
            if column_name not in existing_columns:
                try:
                    sql_type = get_column_type(db_type, column_name)
                    default_value = get_default_value(db_type, column_name)
                    alter_sql = f"ALTER TABLE user_automations ADD COLUMN {column_name} {sql_type} {default_value}"
                    conn.execute(text(alter_sql))
                    conn.commit()
                    changes_made.append(f"✅ Added {column_name} to user_automations table")
                    print(f"  ✅ Added {column_name}")
                except OperationalError as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"  ⚠️  Column {column_name} already exists")
                    else:
                        print(f"  ❌ Error adding {column_name}: {e}")
            else:
                print(f"  ✓ Column {column_name} already exists")
    
    # Print summary
    print("\n" + "="*60)
    if changes_made:
        print("🎉 Migration completed successfully!")
        print("\nChanges made:")
        for change in changes_made:
            print(f"  {change}")
    else:
        print("✅ No changes needed - all columns already exist")
    
    print("\n📊 Summary:")
    print(f"  Database: {db_type}")
    print(f"  Tables checked: automations, user_automations")
    print(f"  Columns added: {len(changes_made)}")
    
    return len(changes_made) > 0

if __name__ == "__main__":
    print("🚀 Starting Automation Integration Contract Migration")
    print("="*60)
    
    try:
        success = migrate_integration_columns()
        if success:
            print("\n✅ Migration completed with changes")
            sys.exit(0)
        else:
            print("\n✅ Migration completed - no changes needed")
            sys.exit(0)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)
