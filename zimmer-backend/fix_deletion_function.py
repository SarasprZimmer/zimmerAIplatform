#!/usr/bin/env python3
import os
import re

# Read the automation.py file
with open('routers/admin/automation.py', 'r') as f:
    content = f.read()

# Find the delete_automation function and replace it with a working version
old_function_pattern = r'@router\.delete\("/automations/\{automation_id\}"\).*?(?=@router\.|\Z)'
new_function = '''@router.delete("/automations/{automation_id}")
async def delete_automation(
    automation_id: int = Path(...),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Delete an automation (admin only)
    Handles foreign key constraints by deleting related records first
    """
    try:
        automation = db.query(Automation).filter(Automation.id == automation_id).first()
        if not automation:
            raise HTTPException(status_code=404, detail="Automation not found")
        
        logger.info(f"Admin {current_admin.email} attempting to delete automation {automation.name} (ID: {automation_id})")
        
        # Check if automation has active user connections
        user_automations = db.query(UserAutomation).filter(UserAutomation.automation_id == automation_id).all()
        if user_automations:
            logger.warning(f"Automation {automation_id} has {len(user_automations)} active user connections")
            # Option 1: Prevent deletion if users are connected
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete automation with {len(user_automations)} active user connections. Please deactivate users first."
            )
        
        # Delete related records safely - only delete tables that exist
        from sqlalchemy import text
        
        try:
            # Delete KB templates
            db.execute(text("DELETE FROM kb_templates WHERE automation_id = :automation_id"), {"automation_id": automation_id})
        except Exception as e:
            logger.warning(f"Could not delete kb_templates: {e}")
        
        try:
            # Delete OpenAI keys and their usage
            db.execute(text("DELETE FROM openai_key_usage WHERE openai_key_id IN (SELECT id FROM openai_keys WHERE automation_id = :automation_id)"), {"automation_id": automation_id})
            db.execute(text("DELETE FROM openai_keys WHERE automation_id = :automation_id"), {"automation_id": automation_id})
        except Exception as e:
            logger.warning(f"Could not delete openai_keys: {e}")
        
        try:
            # Delete payments
            db.execute(text("DELETE FROM payments WHERE automation_id = :automation_id"), {"automation_id": automation_id})
        except Exception as e:
            logger.warning(f"Could not delete payments: {e}")
        
        try:
            # Delete KB status history (only if table exists)
            db.execute(text("DELETE FROM kb_status_history WHERE automation_id = :automation_id"), {"automation_id": automation_id})
        except Exception as e:
            logger.warning(f"Could not delete kb_status_history: {e}")
        
        # Delete the automation itself
        db.delete(automation)
        db.commit()
        
        logger.info(f"Successfully deleted automation {automation.name} (ID: {automation_id})")
        return {"message": "Automation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete automation {automation_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete automation: {str(e)}"
        )

'''

# Replace the function
new_content = re.sub(old_function_pattern, new_function, content, flags=re.DOTALL)

# Write the updated file
with open('routers/admin/automation.py', 'w') as f:
    f.write(new_content)

print("✅ Fixed automation deletion function")
