import re

# Read the current support.tsx file
with open('pages/support.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the message type definition to use string IDs
old_message_type = '''  messages: Array<{
    id: number;
    content: string;
    is_from_user: boolean;
    created_at: string;
  }>;'''

new_message_type = '''  messages: Array<{
    id: string;
    content: string;
    is_from_user: boolean;
    created_at: string;
  }>;'''

# Replace the message type definition
content = content.replace(old_message_type, new_message_type)

# Write the updated content
with open('pages/support.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Message ID type fixed successfully!")
