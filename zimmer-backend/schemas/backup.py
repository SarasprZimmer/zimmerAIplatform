from pydantic import BaseModel, ConfigDict
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models.backup import BackupStatus

class BackupLogOut(BaseModel):
    id: int
    backup_date: datetime
    file_name: str
    file_path: str
    file_size: int
    status: BackupStatus
    verified: bool

    model_config = ConfigDict(from_attributes=True)

class BackupTriggerResponse(BaseModel):
    success: bool
    message: str
    backup_id: Optional[int] = None

class BackupCleanupResponse(BaseModel):
    deleted_count: int
    cleaned_files: list
    message: str

class BackupStats(BaseModel):
    total_backups: int
    successful_backups: int
    failed_backups: int
    last_backup: Optional[str]
    total_size_bytes: int
