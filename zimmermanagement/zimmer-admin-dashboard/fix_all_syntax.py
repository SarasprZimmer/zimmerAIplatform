import re

# Read the file
with open('/home/zimmer/zimmerAIplatform/zimmermanagement/zimmer-admin-dashboard/pages/automations.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the openEditForm function - replace semicolons with commas
content = re.sub(
    r'(api_base_url: automation\.api_base_url \|\| \'\'\')(\s+)(api_provision_url:)',
    r'\1,\2\3',
    content
)

content = re.sub(
    r'(api_provision_url: automation\.api_provision_url \|\| \'\'\')(\s+)(api_usage_url:)',
    r'\1,\2\3',
    content
)

content = re.sub(
    r'(api_usage_url: automation\.api_usage_url \|\| \'\'\')(\s+)(api_kb_status_url:)',
    r'\1,\2\3',
    content
)

content = re.sub(
    r'(api_kb_status_url: automation\.api_kb_status_url \|\| \'\'\')(\s+)(api_kb_reset_url:)',
    r'\1,\2\3',
    content
)

content = re.sub(
    r'(api_kb_reset_url: automation\.api_kb_reset_url \|\| \'\'\')(\s+)(dashboard_url:)',
    r'\1,\2\3',
    content
)

content = re.sub(
    r'(dashboard_url: automation\.dashboard_url \|\| \'\'\')(\s+)(\}\);)',
    r'\1,\2\3',
    content
)

# Fix the resetForm function
content = re.sub(
    r'(dashboard_url: \'\'\')(\s+)(\}\);)',
    r'\1,\2\3',
    content
)

# Write the fixed content back
with open('/home/zimmer/zimmerAIplatform/zimmermanagement/zimmer-admin-dashboard/pages/automations.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("All syntax errors fixed!")
