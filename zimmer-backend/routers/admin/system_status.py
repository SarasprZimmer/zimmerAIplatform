from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal
from models.user import User
from models.automation import Automation
from models.backup import BackupLog
from models.payment import Payment
from models.ticket import Ticket
from utils.auth_dependency import get_current_admin_user, get_db
from datetime import datetime, timedelta
import os

# Try to import psutil, but make it optional
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

router = APIRouter()

@router.get("/status")
async def get_system_status(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Get system status and health information (admin only)
    """
    try:
        # Get basic system stats
        system_stats = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy"
        }
        
        # Database statistics
        try:
            total_users = db.query(func.count(User.id)).scalar()
            total_automations = db.query(func.count(Automation.id)).scalar()
            total_payments = db.query(func.count(Payment.id)).scalar()
            total_tickets = db.query(func.count(Ticket.id)).scalar()
            
            # Recent activity (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            new_users_24h = db.query(func.count(User.id)).filter(User.created_at >= yesterday).scalar()
            new_payments_24h = db.query(func.count(Payment.id)).filter(Payment.created_at >= yesterday).scalar()
            new_tickets_24h = db.query(func.count(Ticket.id)).filter(Ticket.created_at >= yesterday).scalar()
            
            system_stats["database"] = {
                "total_users": total_users,
                "total_automations": total_automations,
                "total_payments": total_payments,
                "total_tickets": total_tickets,
                "activity_24h": {
                    "new_users": new_users_24h,
                    "new_payments": new_payments_24h,
                    "new_tickets": new_tickets_24h
                }
            }
        except Exception as e:
            system_stats["database"] = {"error": str(e)}
            system_stats["status"] = "degraded"
        
        # Backup status
        try:
            latest_backup = db.query(BackupLog).order_by(BackupLog.backup_date.desc()).first()
            if latest_backup:
                system_stats["backup"] = {
                    "latest_backup": latest_backup.backup_date.isoformat(),
                    "latest_status": latest_backup.status,
                    "latest_file": latest_backup.file_name,
                    "verified": latest_backup.verified
                }
            else:
                system_stats["backup"] = {"status": "no_backups_found"}
        except Exception as e:
            system_stats["backup"] = {"error": str(e)}
        
        # System resources (if available)
        try:
            if PSUTIL_AVAILABLE:
                system_stats["resources"] = {
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_usage": psutil.disk_usage('/').percent if os.path.exists('/') else None
                }
            else:
                system_stats["resources"] = {"status": "psutil_not_installed"}
        except Exception:
            system_stats["resources"] = {"status": "unavailable"}
        
        # Environment info
        system_stats["environment"] = {
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
            "platform": os.name,
            "working_directory": os.getcwd()
        }
        
        return system_stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system status: {str(e)}"
        )

@router.get("/health")
async def get_system_health(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Get system health check (admin only)
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }
        
        # Database connectivity check
        try:
            db.execute("SELECT 1")
            health_status["checks"]["database"] = "healthy"
        except Exception as e:
            health_status["checks"]["database"] = f"unhealthy: {str(e)}"
            health_status["status"] = "unhealthy"
        
        # Check if we can query basic models
        try:
            user_count = db.query(func.count(User.id)).scalar()
            health_status["checks"]["models"] = "healthy"
        except Exception as e:
            health_status["checks"]["models"] = f"unhealthy: {str(e)}"
            health_status["status"] = "unhealthy"
        
        # System resource check
        try:
            if PSUTIL_AVAILABLE:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                
                if cpu_percent > 90 or memory_percent > 90:
                    health_status["checks"]["resources"] = "warning: high usage"
                    if health_status["status"] == "healthy":
                        health_status["status"] = "degraded"
                else:
                    health_status["checks"]["resources"] = "healthy"
            else:
                health_status["checks"]["resources"] = "unavailable"
        except Exception as e:
            health_status["checks"]["resources"] = f"unhealthy: {str(e)}"
            health_status["status"] = "unhealthy"
        
        return health_status
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system health: {str(e)}"
        )
