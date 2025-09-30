#!/usr/bin/env python3
import os
import re

# Read the automation.py file
with open('models/automation.py', 'r') as f:
    content = f.read()

# Check if per_session is already in the enum
if 'per_session = \'per_session\'' in content:
    print("✅ per_session already exists in enum")
else:
    # Add per_session to the enum
    old_enum = '''class PricingType(str, enum.Enum):
    token_per_session = 'token_per_session'
    token_per_step = 'token_per_step'
    flat_fee = 'flat_fee' '''
    
    new_enum = '''class PricingType(str, enum.Enum):
    token_per_session = 'token_per_session'
    token_per_step = 'token_per_step'
    flat_fee = 'flat_fee'
    per_session = 'per_session'  # Legacy value for backward compatibility'''
    
    new_content = content.replace(old_enum, new_enum)
    
    # Write the updated file
    with open('models/automation.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Added per_session to PricingType enum")

print("✅ Enum fix completed")
