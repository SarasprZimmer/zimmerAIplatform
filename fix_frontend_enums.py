#!/usr/bin/env python3
import os
import re

# Fix the automation form in admin dashboard
file_path = 'zimmermanagement/zimmer-admin-dashboard/pages/automations.tsx'

if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the enum values
    content = content.replace('"per_session"', '"token_per_session"')
    content = content.replace('"per_message"', '"token_per_message"')
    content = content.replace("'per_session'", "'token_per_session'")
    content = content.replace("'per_message'", "'token_per_message'")
    
    # Also fix the type definitions
    content = content.replace("'per_message' | 'per_minute' | 'per_session'", "'token_per_message' | 'token_per_session'")
    
    # Fix the pricing type options object
    content = content.replace("per_message: 'به ازای پیام',", "token_per_message: 'به ازای پیام',")
    content = content.replace("per_session: 'به ازای جلسه'", "token_per_session: 'به ازای جلسه'")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('✅ Fixed frontend enum values in automations.tsx')
else:
    print('❌ automations.tsx not found')
