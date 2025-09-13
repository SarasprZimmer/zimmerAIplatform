#!/usr/bin/env python3
"""
Verifies that importing models builds Base.metadata without errors.
"""
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from models import Base  # noqa
    print("✅ OK: models import successful")
    print(f"📋 Metadata tables: {[t.name for t in Base.metadata.sorted_tables]}")
    print(f"📊 Total tables: {len(Base.metadata.sorted_tables)}")
except Exception as e:
    print(f"❌ ERROR: Failed to import models: {e}")
    sys.exit(1)
