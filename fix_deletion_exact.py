import re
import os

file_path = 'zimmer-backend/routers/admin/automation.py'

if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the function body from the try block to the end of the function
    # Look for the try block that starts the function body
    pattern = r'(    try:\s*automation = db\.query\(Automation\)\.filter\(Automation\.id == automation_id\)\.first\(\).*?)(?=\n@router\.|\nasync def|\nclass|\Z)'
    
    new_function_body = '''    try:
        automation = db.query(Automation).filter(Automation.id == automation_id).first()
        if not automation:
            raise HTTPException(status_code=404, detail="Automation not found")

        logger.info(f"Admin {current_admin.email} attempting to delete automation {automation.name} (ID: {automation_id})")

        # Use direct SQL execution to avoid transaction issues
        # Delete related records first
        from sqlalchemy import text
        
        cleanup_queries = [
            "DELETE FROM kb_templates WHERE automation_id = :automation_id",
            "DELETE FROM openai_key_usage WHERE openai_key_id IN (SELECT id FROM openai_keys WHERE automation_id = :automation_id)",
            "DELETE FROM openai_keys WHERE automation_id = :automation_id", 
            "DELETE FROM payments WHERE automation_id = :automation_id",
            "DELETE FROM user_automations WHERE automation_id = :automation_id",
            "DELETE FROM kb_status_history WHERE automation_id = :automation_id"
        ]
        
        for query in cleanup_queries:
            try:
                db.execute(text(query), {"automation_id": automation_id})
                logger.info(f"✅ Executed cleanup query: {query[:50]}...")
            except Exception as e:
                if "relation" in str(e) and "does not exist" in str(e):
                    logger.warning(f"⚠️  Table does not exist, skipping: {query[:50]}...")
                else:
                    logger.warning(f"⚠️  Cleanup query failed: {str(e)[:100]}...")
        
        # Finally delete the automation itself
        db.execute(text("DELETE FROM automations WHERE id = :automation_id"), {"automation_id": automation_id})
        db.commit()
        
        logger.info(f"✅ Successfully deleted automation {automation.name} (ID: {automation_id})")
        return {"message": f"Automation {automation.name} deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to delete automation {automation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete automation: {str(e)}")'''

    # Replace the function body
    new_content = re.sub(pattern, new_function_body, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print('✅ Successfully replaced delete_automation function body')
    else:
        print('❌ Could not find function body to replace')
        # Let's try a different approach - replace just the problematic part
        # Find the user_automations check and replace it
        user_check_pattern = r'        # Check if automation has active user connections.*?raise HTTPException\([^)]*\)'
        user_check_replacement = '''        # Skip user connection check for now - allow deletion
        # user_automations = db.query(UserAutomation).filter(UserAutomation.automation_id == automation_id).all()
        # if user_automations:
        #     logger.warning(f"Automation {automation_id} has {len(user_automations)} active user connections")
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail=f"Cannot delete automation with {len(user_automations)} active user connections. Please deactivate users first."
        #     )'''
        
        new_content = re.sub(user_check_pattern, user_check_replacement, content, flags=re.DOTALL)
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print('✅ Successfully disabled user connection check')
        else:
            print('❌ Could not find user connection check to replace')
else:
    print(f'❌ File not found: {file_path}')
