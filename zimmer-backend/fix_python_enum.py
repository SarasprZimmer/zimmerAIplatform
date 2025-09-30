#!/usr/bin/env python3
import os
import re

# Read the automation.py file
with open('models/automation.py', 'r') as f:
    content = f.read()

# Find and replace the enum definition
old_enum_pattern = r'class PricingType\(str, enum\.Enum\):.*?(?=\nclass|\nfrom|\nimport|\Z)'
new_enum = '''class PricingType(str, enum.Enum):
    token_per_session = 'token_per_session'
    token_per_message = 'token_per_message'
'''

new_content = re.sub(old_enum_pattern, new_enum, content, flags=re.DOTALL)

# Write the updated file
with open('models/automation.py', 'w') as f:
    f.write(new_content)

print("✅ Updated Python enum to only include token_per_session and token_per_message")
