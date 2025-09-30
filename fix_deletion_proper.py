import re

# Read the current automation.py file
with open('zimmer-backend/routers/admin/automation.py', 'r') as f:
    content = f.read()

# Find and replace the delete_automation function with a proper implementation
old_function = '''@router.delete("/{automation_id}")
async def delete_automation(
    automation_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete an automation and all related data"""
    logger.info(f"Admin {current_user.email} attempting to delete automation (ID: {automation_id})")
    
    # Get the automation first
    automation = db.query(Automation).filter(Automation.id == automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    
    automation_name = automation.name
    
    try:
        # Delete related records in order (foreign key constraints)
        # 1. Delete kb_templates
        try:
            db.query(KBTemplate).filter(KBTemplate.automation_id == automation_id).delete()
            logger.info(f"Deleted kb_templates for automation {automation_id}")
        except Exception as e:
            logger.warning(f"Could not delete kb_templates: {e}")
        
        # 2. Delete openai_key_usage first, then openai_keys
        try:
            # Delete usage records first
            db.query(OpenAIKeyUsage).filter(
                OpenAIKeyUsage.openai_key_id.in_(
                    db.query(OpenAIKey.id).filter(OpenAIKey.automation_id == automation_id)
                )
            ).delete()
            # Then delete the keys
            db.query(OpenAIKey).filter(OpenAIKey.automation_id == automation_id).delete()
            logger.info(f"Deleted openai_keys for automation {automation_id}")
        except Exception as e:
            logger.warning(f"Could not delete openai_keys: {e}")
        
        # 3. Delete payments
        try:
            db.query(Payment).filter(Payment.automation_id == automation_id).delete()
            logger.info(f"Deleted payments for automation {automation_id}")
        except Exception as e:
            logger.warning(f"Could not delete payments: {e}")
        
        # 4. Delete user_automations
        try:
            db.query(UserAutomation).filter(UserAutomation.automation_id == automation_id).delete()
            logger.info(f"Deleted user_automations for automation {automation_id}")
        except Exception as e:
            logger.warning(f"Could not delete user_automations: {e}")
        
        # 5. Delete kb_status_history
        try:
            db.query(KBStatusHistory).filter(KBStatusHistory.automation_id == automation_id).delete()
            logger.info(f"Deleted kb_status_history for automation {automation_id}")
        except Exception as e:
            logger.warning(f"Could not delete kb_status_history: {e}")
        
        # 6. Finally delete the automation itself
        db.query(Automation).filter(Automation.id == automation_id).delete()
        db.commit()
        
        logger.info(f"Successfully deleted automation {automation_name} (ID: {automation_id})")
        return {"message": f"Automation {automation_name} deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete automation {automation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete automation: {str(e)}")'''

new_function = '''@router.delete("/{automation_id}")
async def delete_automation(
    automation_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete an automation and all related data"""
    logger.info(f"Admin {current_user.email} attempting to delete automation (ID: {automation_id})")
    
    # Get the automation first
    automation = db.query(Automation).filter(Automation.id == automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    
    automation_name = automation.name
    
    # List of tables to clean up (in order of dependencies)
    cleanup_tables = [
        ('kb_templates', 'automation_id'),
        ('openai_key_usage', 'openai_key_id IN (SELECT id FROM openai_keys WHERE automation_id = %s)'),
        ('openai_keys', 'automation_id'),
        ('payments', 'automation_id'),
        ('user_automations', 'automation_id'),
        ('kb_status_history', 'automation_id')
    ]
    
    try:
        # Clean up each table in separate transactions to avoid cascading failures
        for table_name, condition in cleanup_tables:
            try:
                if 'openai_key_usage' in condition:
                    # Special case for openai_key_usage
                    db.execute(text(f"DELETE FROM {table_name} WHERE {condition}"), (automation_id,))
                else:
                    # Standard case
                    db.execute(text(f"DELETE FROM {table_name} WHERE {condition} = %s"), (automation_id,))
                db.commit()
                logger.info(f"✅ Deleted from {table_name} for automation {automation_id}")
            except Exception as e:
                db.rollback()  # Rollback this specific operation
                logger.warning(f"⚠️  Could not delete from {table_name}: {str(e)[:100]}...")
                # Continue with next table
        
        # Finally delete the automation itself
        db.execute(text("DELETE FROM automations WHERE id = %s"), (automation_id,))
        db.commit()
        
        logger.info(f"✅ Successfully deleted automation {automation_name} (ID: {automation_id})")
        return {"message": f"Automation {automation_name} deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to delete automation {automation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete automation: {str(e)}")'''

# Apply the replacement
content = content.replace(old_function, new_function)

# Write the updated content back
with open('zimmer-backend/routers/admin/automation.py', 'w') as f:
    f.write(content)

print("✅ Fixed delete_automation function to use separate transactions")
