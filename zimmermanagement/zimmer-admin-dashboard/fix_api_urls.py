import re

# Read the file
with open('lib/api.ts', 'r') as f:
    content = f.read()

# Replace relative URLs with environment variable URLs
replacements = [
    ("'/api/auth/login'", "`${process.env.NEXT_PUBLIC_API_URL || 'http://193.162.129.243:8000'}/api/auth/login`"),
    ("'/api/auth/signup'", "`${process.env.NEXT_PUBLIC_API_URL || 'http://193.162.129.243:8000'}/api/auth/signup`"),
    ("'/api/auth/logout'", "`${process.env.NEXT_PUBLIC_API_URL || 'http://193.162.129.243:8000'}/api/auth/logout`"),
    ("'/api/auth/refresh'", "`${process.env.NEXT_PUBLIC_API_URL || 'http://193.162.129.243:8000'}/api/auth/refresh`"),
    ("'/api/admin/", "`${process.env.NEXT_PUBLIC_API_URL || 'http://193.162.129.243:8000'}/api/admin/"),
    ("'/api/token-adjustments'", "`${process.env.NEXT_PUBLIC_API_URL || 'http://193.162.129.243:8000'}/api/token-adjustments`"),
]

# Apply replacements
for old, new in replacements:
    content = content.replace(old, new)

# Write back to file
with open('lib/api.ts', 'w') as f:
    f.write(content)

print("API URLs updated successfully!")
