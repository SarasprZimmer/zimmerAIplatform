from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models.backup import BackupStatus

class BackupLogBase(BaseModel):
    file_name: str
    file_size: int
    status: BackupStatus
    storage_location: str = "local"
    verified: bool = False

class BackupLogCreate(BackupLogBase):
    pass

class BackupLogOut(BackupLogBase):
    id: int
    backup_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class BackupTriggerResponse(BaseModel):
    message: str
    backup_id: Optional[int] = None
    status: str

class BackupCleanupResponse(BaseModel):
    message: str
    deleted_count: int
    cleaned_files: list[str]

class BackupStats(BaseModel):
    total_backups: int
    successful_backups: int
    failed_backups: int
    verified_backups: int
    last_successful_backup: Optional[datetime] = None
    total_size_bytes: int 