import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv('zimmer-backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ No DATABASE_URL found in environment")
    sys.exit(1)

print(f"🔗 Using database: {DATABASE_URL[:20]}...")

engine = create_engine(DATABASE_URL)

def safe_delete_automation(automation_id):
    """Safely delete an automation by handling missing tables"""
    
    print(f"🗑️ Deleting automation {automation_id}...")
    
    # List of tables that might be related to automations
    related_tables = [
        'kb_templates',
        'openai_key_usage', 
        'openai_keys',
        'payments',
        'user_automations',
        'kb_status_history'  # This one might not exist
    ]
    
    # Delete from each table in separate transactions
    for table in related_tables:
        try:
            with engine.begin() as conn:
                if table == 'openai_key_usage':
                    # Delete usage records first
                    conn.execute(text('''
                        DELETE FROM openai_key_usage 
                        WHERE openai_key_id IN (
                            SELECT id FROM openai_keys WHERE automation_id = :automation_id
                        )
                    '''), {'automation_id': automation_id})
                elif table == 'openai_keys':
                    # Delete keys
                    conn.execute(text('DELETE FROM openai_keys WHERE automation_id = :automation_id'), 
                               {'automation_id': automation_id})
                else:
                    # Delete from other tables
                    conn.execute(text(f'DELETE FROM {table} WHERE automation_id = :automation_id'), 
                               {'automation_id': automation_id})
                print(f"✅ Deleted from {table}")
        except Exception as e:
            print(f"⚠️ Could not delete from {table}: {str(e)[:50]}...")
    
    # Finally delete the automation itself
    try:
        with engine.begin() as conn:
            result = conn.execute(text('DELETE FROM automations WHERE id = :automation_id'), 
                                {'automation_id': automation_id})
            print(f"✅ Deleted automation {automation_id} (affected {result.rowcount} rows)")
            return True
    except Exception as e:
        print(f"❌ Failed to delete automation: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        automation_id = int(sys.argv[1])
        safe_delete_automation(automation_id)
    else:
        print("Usage: python3 fix_deletion.py <automation_id>")
