from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from database import Base
import enum

class BackupStatus(str, enum.Enum):
    success = 'success'
    failed = 'failed'

class BackupLog(Base):
    __tablename__ = "backup_logs"

    id = Column(Integer, primary_key=True, index=True)
    backup_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    file_name = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    status = Column(Enum(BackupStatus), nullable=False)
    storage_location = Column(String, nullable=False, default="local")  # "local", "s3", etc.
    verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False) 