import sqlite3

conn = sqlite3.connect('zimmer_dashboard.db')
cursor = conn.cursor()

try:
    print("Adding columns to automations table...")
    cursor.execute('ALTER TABLE automations ADD COLUMN api_base_url TEXT')
    print("Added api_base_url")
    cursor.execute('ALTER TABLE automations ADD COLUMN api_provision_url TEXT')
    print("Added api_provision_url")
    cursor.execute('ALTER TABLE automations ADD COLUMN api_usage_url TEXT')
    print("Added api_usage_url")
    cursor.execute('ALTER TABLE automations ADD COLUMN service_token_hash TEXT')
    print("Added service_token_hash")
    
    print("Adding columns to user_automations table...")
    cursor.execute('ALTER TABLE user_automations ADD COLUMN provisioned_at DATETIME')
    print("Added provisioned_at")
    cursor.execute('ALTER TABLE user_automations ADD COLUMN integration_status TEXT DEFAULT "pending"')
    print("Added integration_status")
    
    conn.commit()
    print("Migration completed successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()

finally:
    conn.close()
