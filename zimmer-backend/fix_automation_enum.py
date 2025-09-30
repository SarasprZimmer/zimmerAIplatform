#!/usr/bin/env python3
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Update the problematic automation's pricing_type
    result = conn.execute(text("""
        UPDATE automations 
        SET pricing_type = 'token_per_session' 
        WHERE pricing_type = 'per_session'
    """))
    conn.commit()
    print(f"✅ Updated {result.rowcount} automations from 'per_session' to 'token_per_session'")
    
    # Verify the fix
    result = conn.execute(text("SELECT id, name, pricing_type FROM automations WHERE id = 1")).fetchone()
    if result:
        print(f"✅ Automation 1: {result[1]} - pricing_type: {result[2]}")
    else:
        print("❌ Automation 1 not found")
