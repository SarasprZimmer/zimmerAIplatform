import re
import os

file_path = 'zimmer-backend/routers/admin/automation.py'

if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the function body and replace it with a bulletproof version
    pattern = r'(    try:\s*automation = db\.query\(Automation\)\.filter\(Automation\.id == automation_id\)\.first\(\).*?)(?=\n@router\.|\nasync def|\nclass|\Z)'
    
    new_function_body = '''    try:
        automation = db.query(Automation).filter(Automation.id == automation_id).first()
        if not automation:
            raise HTTPException(status_code=404, detail="Automation not found")

        logger.info(f"Admin {current_admin.email} attempting to delete automation {automation.name} (ID: {automation_id})")

        # Use completely separate database connections to avoid transaction issues
        from sqlalchemy import create_engine
        import os
        
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise HTTPException(status_code=500, detail="Database configuration error")
        
        # Create a new engine for separate connections
        separate_engine = create_engine(database_url)
        
        # List of tables to clean up
        cleanup_operations = [
            ('kb_templates', f'DELETE FROM kb_templates WHERE automation_id = {automation_id}'),
            ('openai_key_usage', f'DELETE FROM openai_key_usage WHERE openai_key_id IN (SELECT id FROM openai_keys WHERE automation_id = {automation_id})'),
            ('openai_keys', f'DELETE FROM openai_keys WHERE automation_id = {automation_id}'),
            ('payments', f'DELETE FROM payments WHERE automation_id = {automation_id}'),
            ('user_automations', f'DELETE FROM user_automations WHERE automation_id = {automation_id}'),
            ('kb_status_history', f'DELETE FROM kb_status_history WHERE automation_id = {automation_id}')
        ]
        
        # Clean up each table using separate connections
        for table_name, sql_query in cleanup_operations:
            try:
                # Use a separate connection for each operation
                with separate_engine.begin() as conn:
                    conn.execute(text(sql_query))
                logger.info(f'✅ Deleted from {table_name} for automation {automation_id}')
            except Exception as e:
                if "relation \"" in str(e) and "\" does not exist" in str(e):
                    logger.warning(f'⚠️  Table {table_name} does not exist, skipping')
                else:
                    logger.warning(f'⚠️  Could not delete from {table_name}: {str(e)[:100]}...')
                # Continue with next table
        
        # Finally delete the automation itself using the main session
        db.query(Automation).filter(Automation.id == automation_id).delete()
        db.commit()
        
        logger.info(f'✅ Successfully deleted automation {automation.name} (ID: {automation_id})')
        return {"message": f"Automation {automation.name} deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f'❌ Failed to delete automation {automation_id}: {e}')
        raise HTTPException(status_code=500, detail=f"Failed to delete automation: {str(e)}")
    finally:
        # Close the separate engine
        if 'separate_engine' in locals():
            separate_engine.dispose()'''

    # Replace the function body
    new_content = re.sub(pattern, new_function_body, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print('✅ Successfully replaced delete_automation function with bulletproof version')
    else:
        print('❌ Could not find function body to replace')
else:
    print(f'❌ File not found: {file_path}')
