import re
import os

file_path = 'zimmer-backend/routers/admin/automation.py'

if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the exact delete_automation function and replace it
    # Look for the specific route pattern and function signature
    pattern = r'@router\.delete\("/automations/\{automation_id\}"\)\s*async def delete_automation\([^)]*\):.*?(?=\n@router\.|\nasync def|\nclass|\Z)'
    
    new_function = '''@router.delete("/automations/{automation_id}")
async def delete_automation(
    automation_id: int = Path(...),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Delete an automation (admin only)
    Uses direct SQL execution to avoid transaction issues
    """
    try:
        automation = db.query(Automation).filter(Automation.id == automation_id).first()
        if not automation:
            raise HTTPException(status_code=404, detail="Automation not found")

        logger.info(f"Admin {current_admin.email} attempting to delete automation {automation.name} (ID: {automation_id})")

        # Use direct SQL execution to avoid transaction issues
        # Delete related records first
        cleanup_queries = [
            "DELETE FROM kb_templates WHERE automation_id = %s",
            "DELETE FROM openai_key_usage WHERE openai_key_id IN (SELECT id FROM openai_keys WHERE automation_id = %s)",
            "DELETE FROM openai_keys WHERE automation_id = %s", 
            "DELETE FROM payments WHERE automation_id = %s",
            "DELETE FROM user_automations WHERE automation_id = %s",
            "DELETE FROM kb_status_history WHERE automation_id = %s"
        ]
        
        for query in cleanup_queries:
            try:
                db.execute(text(query), (automation_id,))
                logger.info(f"✅ Executed cleanup query: {query[:50]}...")
            except Exception as e:
                if "relation" in str(e) and "does not exist" in str(e):
                    logger.warning(f"⚠️  Table does not exist, skipping: {query[:50]}...")
                else:
                    logger.warning(f"⚠️  Cleanup query failed: {str(e)[:100]}...")
        
        # Finally delete the automation itself
        db.execute(text("DELETE FROM automations WHERE id = %s"), (automation_id,))
        db.commit()
        
        logger.info(f"✅ Successfully deleted automation {automation.name} (ID: {automation_id})")
        return {"message": f"Automation {automation.name} deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to delete automation {automation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete automation: {str(e)}")'''

    # Replace the function
    new_content = re.sub(pattern, new_function, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print('✅ Successfully replaced delete_automation function')
    else:
        print('❌ Could not find delete_automation function to replace')
        # Let's try a simpler approach - just replace the function body
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'async def delete_automation' in line:
                print(f'Found function at line {i+1}: {line}')
                # Show more context
                for j in range(max(0, i-2), min(len(lines), i+50)):
                    print(f'{j+1:3d}: {lines[j]}')
                break
else:
    print(f'❌ File not found: {file_path}')
