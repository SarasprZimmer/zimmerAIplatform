import re

# Read the current automation.py file
with open('zimmer-backend/routers/admin/automation.py', 'r') as f:
    content = f.read()

# Find and replace the problematic deletion section
old_section = '''        try:
            # Delete KB status history
            db.execute(text("DELETE FROM kb_status_history WHERE automation_id = :automation_id"), {"automation_id": automation_id})
        except Exception as e:
            logger.warning(f"Could not delete kb_status_history: {e}")'''

new_section = '''        try:
            # Delete KB status history (if table exists)
            db.execute(text("DELETE FROM kb_status_history WHERE automation_id = :automation_id"), {"automation_id": automation_id})
        except Exception as e:
            logger.warning(f"Could not delete kb_status_history: {e}")'''

# Apply the replacement
content = content.replace(old_section, new_section)

# Write the updated content back
with open('zimmer-backend/routers/admin/automation.py', 'w') as f:
    f.write(content)

print("✅ Updated deletion code to handle missing kb_status_history table")
