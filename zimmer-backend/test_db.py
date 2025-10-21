#!/usr/bin/env python3

from database import engine
from sqlalchemy import text
from models import ConstructionEmail

def test_database():
    try:
        print("Testing database connection...")
        with engine.connect() as conn:
            result = conn.execute(text('SELECT 1'))
            print("✅ Database connection OK")
        
        print("Testing ConstructionEmail model...")
        # Try to create the table if it doesn't exist
        ConstructionEmail.__table__.create(engine, checkfirst=True)
        print("✅ ConstructionEmail table created/verified")
        
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    test_database()
