#!/usr/bin/env python3
import os
import re
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Read the current automation.py file
with open('routers/admin/automation.py', 'r') as f:
    content = f.read()

# Find the delete_automation function and replace it with a safer version
old_function = '''@router.delete("/automations/{automation_id}")
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
            
            # Option 2: Force delete all user connections (uncomment if you want this behavior)
            # for ua in user_automations:
            #     # Delete related records first
            #     db.query(KBStatusHistory).filter(KBStatusHistory.user_automation_id == ua.id).delete()
            #     db.query(TokenAdjustment).filter(TokenAdjustment.user_automation_id == ua.id).delete()
            #     db.query(TokenUsage).filter(TokenUsage.user_automation_id == ua.id).delete()
            #     db.query(FallbackLog).filter(FallbackLog.user_automation_id == ua.id).delete()
            #     # Delete user automation
            #     db.delete(ua)
        
        # Delete related records that don't have CASCADE
        from models.kb_template import KBTemplate
        from models.openai_key import OpenAIKey
        from models.openai_key_usage import OpenAIKeyUsage
        from models.payment import Payment
        from models.kb_status_history import KBStatusHistory
        
        # Delete KB templates
        db.query(KBTemplate).filter(KBTemplate.automation_id == automation_id).delete()
        
        # Delete OpenAI keys and their usage
        openai_keys = db.query(OpenAIKey).filter(OpenAIKey.automation_id == automation_id).all()
        for key in openai_keys:
            db.query(OpenAIKeyUsage).filter(OpenAIKeyUsage.openai_key_id == key.id).delete()
            db.delete(key)
        
        # Delete payments
        db.query(Payment).filter(Payment.automation_id == automation_id).delete()
        
        # Delete KB status history
        db.query(KBStatusHistory).filter(KBStatusHistory.automation_id == automation_id).delete()
        
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
        )'''

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
        )'''

# Replace the function in the file
new_content = content.replace(old_function, new_function)

# Write the updated file
with open('routers/admin/automation.py', 'w') as f:
    f.write(new_content)

print("✅ Updated automation deletion function to handle missing tables safely")
