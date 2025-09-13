from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timedelta
from database import get_db
from models.backup import BackupLog, BackupStatus
from models.user import User
from schemas.backup import BackupLogOut, BackupTriggerResponse, BackupCleanupResponse, BackupStats
from services.backup_service import BackupService
from utils.auth_dependency import get_current_admin_user

router = APIRouter()

@router.get("/backups", response_model=List[BackupLogOut])
async def get_backups(
    status_filter: Optional[BackupStatus] = Query(None, description="Filter by backup status"),
    from_date: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Records per page"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get paginated list of backups with optional filters"""
    
    # Build query
    query = db.query(BackupLog)
    
    # Apply filters
    if status_filter:
        query = query.filter(BackupLog.status == status_filter)
    
    if from_date:
        try:
            from_datetime = datetime.strptime(from_date, "%Y-%m-%d")
            query = query.filter(BackupLog.backup_date >= from_datetime)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid from_date format. Use YYYY-MM-DD"
            )
    
    if to_date:
        try:
            to_datetime = datetime.strptime(to_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(BackupLog.backup_date < to_datetime)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid to_date format. Use YYYY-MM-DD"
            )
    
    # Order by backup date (newest first)
    query = query.order_by(desc(BackupLog.backup_date))
    
    # Apply pagination
    offset = (page - 1) * limit
    total_count = query.count()
    
    # Get paginated results
    backups = query.offset(offset).limit(limit).all()
    
    return backups

@router.get("/backups/stats", response_model=BackupStats)
async def get_backup_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get backup statistics"""
    
    backup_service = BackupService(db)
    stats = backup_service.get_backup_stats()
    
    return BackupStats(**stats)

@router.post("/backups/trigger", response_model=BackupTriggerResponse)
async def trigger_backup(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Manually trigger a new backup"""
    
    try:
        backup_service = BackupService(db)
        success, message, file_path = backup_service.run_backup()
        
        if success:
            # Get the backup ID
            backup = db.query(BackupLog).filter(
                BackupLog.file_name == file_path.split('/')[-1] if file_path else None
            ).order_by(desc(BackupLog.id)).first()
            
            return BackupTriggerResponse(
                message=message,
                backup_id=backup.id if backup else None,
                status="success"
            )
        else:
            return BackupTriggerResponse(
                message=message,
                status="failed"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger backup: {str(e)}"
        )

@router.post("/backups/verify/{backup_id}")
async def verify_backup(
    backup_id: int = Path(..., description="Backup ID to verify"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Mark a backup as verified"""
    
    try:
        backup_service = BackupService(db)
        success = backup_service.verify_backup(backup_id)
        
        if success:
            return {"message": "Backup marked as verified successfully"}
        else:
            raise HTTPException(
                status_code=404,
                detail="Backup not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify backup: {str(e)}"
        )

@router.delete("/backups/cleanup", response_model=BackupCleanupResponse)
async def cleanup_backups(
    retention_days: int = Query(7, ge=1, le=365, description="Number of days to retain backups"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Clean up old backups according to retention rules"""
    
    try:
        backup_service = BackupService(db)
        deleted_count, cleaned_files = backup_service.cleanup_old_backups(retention_days)
        
        return BackupCleanupResponse(
            message=f"Cleanup completed. {deleted_count} backups removed.",
            deleted_count=deleted_count,
            cleaned_files=cleaned_files
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup backups: {str(e)}"
        )

@router.get("/backups/{backup_id}", response_model=BackupLogOut)
async def get_backup(
    backup_id: int = Path(..., description="Backup ID"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get a specific backup by ID"""
    
    backup = db.query(BackupLog).filter(BackupLog.id == backup_id).first()
    
    if not backup:
        raise HTTPException(
            status_code=404,
            detail="Backup not found"
        )
    
    return backup 