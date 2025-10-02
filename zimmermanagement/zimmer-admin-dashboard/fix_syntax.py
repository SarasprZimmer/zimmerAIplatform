import re

# Read the file
with open('/home/zimmer/zimmerAIplatform/zimmermanagement/zimmer-admin-dashboard/pages/automations.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the missing comma after api_kb_reset_url in openEditForm
content = re.sub(
    r'(api_kb_reset_url: automation\.api_kb_reset_url \|\| \'\'\')(\s+)(dashboard_url:)',
    r'\1,\2\3',
    content
)

# Fix the missing comma after dashboard_url in openEditForm
content = re.sub(
    r'(dashboard_url: automation\.dashboard_url \|\| \'\'\')(\s+)(\}\);)',
    r'\1,\2\3',
    content
)

# Fix the missing comma in resetForm function
content = re.sub(
    r'(dashboard_url: \'\'\')(\s+)(\}\);)',
    r'\1,\2\3',
    content
)

# Write the fixed content back
with open('/home/zimmer/zimmerAIplatform/zimmermanagement/zimmer-admin-dashboard/pages/automations.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Syntax errors fixed!")
