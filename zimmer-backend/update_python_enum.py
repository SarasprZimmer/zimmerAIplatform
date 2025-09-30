#!/usr/bin/env python3
import os
import re

# Read the automation.py file
with open('models/automation.py', 'r') as f:
    content = f.read()

# Update the enum to include all values
old_enum = '''class PricingType(str, enum.Enum):
    token_per_session = 'token_per_session'
    token_per_step = 'token_per_step'
    flat_fee = 'flat_fee'
    per_session = 'per_session'  # Legacy value for backward compatibility'''

new_enum = '''class PricingType(str, enum.Enum):
    token_per_session = 'token_per_session'
    token_per_step = 'token_per_step'
    flat_fee = 'flat_fee'
    per_session = 'per_session'  # Legacy value for backward compatibility
    per_message = 'per_message'  # Per message pricing
    per_minute = 'per_minute'    # Per minute pricing'''

new_content = content.replace(old_enum, new_enum)

# Write the updated file
with open('models/automation.py', 'w') as f:
    f.write(new_content)

print("✅ Updated Python enum to include all values")
