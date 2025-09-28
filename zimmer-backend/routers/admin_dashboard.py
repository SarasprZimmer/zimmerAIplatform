from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.automation import Automation
from models.ticket import Ticket
from utils.auth_dependency import get_current_user

router = APIRouter(prefix="/admin", tags=["admin-dashboard"])

@router.get("/dashboard")
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get admin dashboard statistics"""
    try:
        # Get basic statistics
        total_users = db.query(User).count()
        total_automations = db.query(Automation).count()
        total_tickets = db.query(Ticket).count()
        
        return {
            "status": "success",
            "data": {
                "total_users": total_users,
                "total_automations": total_automations,
                "total_tickets": total_tickets,
                "system_status": "healthy"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")
