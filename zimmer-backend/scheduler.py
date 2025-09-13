from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from database import SessionLocal
from services.backup_service import BackupService
from services.openai_key_manager import OpenAIKeyManager
import logging

logger = logging.getLogger(__name__)

class BackupScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.setup_jobs()
    
    def setup_jobs(self):
        """Setup scheduled backup jobs"""
        # Daily backup at 2 AM
        self.scheduler.add_job(
            self.run_scheduled_backup,
            CronTrigger(hour=2, minute=0),
            id='daily_backup',
            name='Daily Database Backup',
            replace_existing=True
        )
        
        # Cleanup old backups after each backup
        self.scheduler.add_job(
            self.run_scheduled_cleanup,
            CronTrigger(hour=3, minute=0),  # Run cleanup at 3 AM
            id='backup_cleanup',
            name='Backup Cleanup',
            replace_existing=True
        )
        
        # Reset daily OpenAI key usage at midnight
        self.scheduler.add_job(
            self.reset_openai_daily_usage,
            CronTrigger(hour=0, minute=0),  # Run at midnight
            id='openai_daily_reset',
            name='OpenAI Daily Usage Reset',
            replace_existing=True
        )
    
    async def run_scheduled_backup(self):
        """Run scheduled backup"""
        logger.info("Starting scheduled backup...")
        
        try:
            db = SessionLocal()
            backup_service = BackupService(db)
            
            success, message, file_path = backup_service.run_backup()
            
            if success:
                logger.info(f"Scheduled backup successful: {message}")
            else:
                logger.error(f"Scheduled backup failed: {message}")
                
        except Exception as e:
            logger.error(f"Scheduled backup error: {e}")
        finally:
            db.close()
    
    async def run_scheduled_cleanup(self):
        """Run scheduled cleanup"""
        logger.info("Starting scheduled backup cleanup...")
        
        try:
            db = SessionLocal()
            backup_service = BackupService(db)
            
            deleted_count, cleaned_files = backup_service.cleanup_old_backups(retention_days=7)
            
            logger.info(f"Scheduled cleanup completed: {deleted_count} backups removed")
            
        except Exception as e:
            logger.error(f"Scheduled cleanup error: {e}")
        finally:
            db.close()
    
    async def reset_openai_daily_usage(self):
        """Reset daily token usage for all OpenAI keys"""
        logger.info("Starting OpenAI daily usage reset...")
        
        try:
            db = SessionLocal()
            key_manager = OpenAIKeyManager(db)
            
            reset_count = key_manager.reset_daily_usage()
            
            logger.info(f"OpenAI daily usage reset completed: {reset_count} keys reset")
            
        except Exception as e:
            logger.error(f"OpenAI daily usage reset error: {e}")
        finally:
            db.close()
    
    def start(self):
        """Start the scheduler"""
        try:
            self.scheduler.start()
            logger.info("Backup scheduler started successfully")
        except Exception as e:
            logger.error(f"Failed to start backup scheduler: {e}")
    
    def stop(self):
        """Stop the scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Backup scheduler stopped")
        except Exception as e:
            logger.error(f"Failed to stop backup scheduler: {e}")

# Global scheduler instance
backup_scheduler = BackupScheduler() 