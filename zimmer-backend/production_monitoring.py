"""
Production Monitoring and Alerting System for Zimmer AI Platform
Real-time monitoring, alerting, and health checks for production deployment
"""

import time
import psutil
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, func

from database import get_db
from models.user import User
from models.automation import Automation
from models.user_automation import UserAutomation
from models.payment import Payment
from models.ticket import Ticket
from utils.auth import get_current_admin_user
from cache_manager import cache, get_cache_stats

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class Alert:
    level: AlertLevel
    message: str
    timestamp: datetime
    metric: str
    value: float
    threshold: float

@dataclass
class SystemMetrics:
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    active_connections: int
    response_time_avg: float
    error_rate: float
    throughput: float

class ProductionMonitor:
    """Production monitoring and alerting system"""
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.metrics_history: List[SystemMetrics] = []
        self.thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 90.0,
            "disk_percent": 85.0,
            "response_time_ms": 500.0,
            "error_rate_percent": 5.0,
            "active_connections": 150,
        }
        self.start_time = datetime.utcnow()
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Application metrics (simplified)
            active_connections = 0  # Would be collected from connection pool
            response_time_avg = 0.0  # Would be collected from request logs
            error_rate = 0.0  # Would be collected from error logs
            throughput = 0.0  # Would be collected from request logs
            
            metrics = SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=(disk.used / disk.total) * 100,
                active_connections=active_connections,
                response_time_avg=response_time_avg,
                error_rate=error_rate,
                throughput=throughput
            )
            
            self.metrics_history.append(metrics)
            
            # Keep only last 1000 metrics
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_percent=0.0,
                active_connections=0,
                response_time_avg=0.0,
                error_rate=0.0,
                throughput=0.0
            )
    
    def check_thresholds(self, metrics: SystemMetrics) -> List[Alert]:
        """Check metrics against thresholds and generate alerts"""
        new_alerts = []
        
        # CPU threshold check
        if metrics.cpu_percent > self.thresholds["cpu_percent"]:
            alert = Alert(
                level=AlertLevel.WARNING if metrics.cpu_percent < 95 else AlertLevel.CRITICAL,
                message=f"High CPU usage: {metrics.cpu_percent:.1f}%",
                timestamp=datetime.utcnow(),
                metric="cpu_percent",
                value=metrics.cpu_percent,
                threshold=self.thresholds["cpu_percent"]
            )
            new_alerts.append(alert)
        
        # Memory threshold check
        if metrics.memory_percent > self.thresholds["memory_percent"]:
            alert = Alert(
                level=AlertLevel.WARNING if metrics.memory_percent < 95 else AlertLevel.CRITICAL,
                message=f"High memory usage: {metrics.memory_percent:.1f}%",
                timestamp=datetime.utcnow(),
                metric="memory_percent",
                value=metrics.memory_percent,
                threshold=self.thresholds["memory_percent"]
            )
            new_alerts.append(alert)
        
        # Disk threshold check
        if metrics.disk_percent > self.thresholds["disk_percent"]:
            alert = Alert(
                level=AlertLevel.WARNING if metrics.disk_percent < 95 else AlertLevel.CRITICAL,
                message=f"High disk usage: {metrics.disk_percent:.1f}%",
                timestamp=datetime.utcnow(),
                metric="disk_percent",
                value=metrics.disk_percent,
                threshold=self.thresholds["disk_percent"]
            )
            new_alerts.append(alert)
        
        # Response time threshold check
        if metrics.response_time_avg > self.thresholds["response_time_ms"]:
            alert = Alert(
                level=AlertLevel.WARNING if metrics.response_time_avg < 1000 else AlertLevel.CRITICAL,
                message=f"High response time: {metrics.response_time_avg:.1f}ms",
                timestamp=datetime.utcnow(),
                metric="response_time_ms",
                value=metrics.response_time_avg,
                threshold=self.thresholds["response_time_ms"]
            )
            new_alerts.append(alert)
        
        # Error rate threshold check
        if metrics.error_rate > self.thresholds["error_rate_percent"]:
            alert = Alert(
                level=AlertLevel.WARNING if metrics.error_rate < 10 else AlertLevel.CRITICAL,
                message=f"High error rate: {metrics.error_rate:.1f}%",
                timestamp=datetime.utcnow(),
                metric="error_rate_percent",
                value=metrics.error_rate,
                threshold=self.thresholds["error_rate_percent"]
            )
            new_alerts.append(alert)
        
        # Add new alerts to the list
        self.alerts.extend(new_alerts)
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        return new_alerts
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status"""
        current_metrics = self.collect_system_metrics()
        new_alerts = self.check_thresholds(current_metrics)
        
        # Calculate health score (0-100)
        health_score = 100
        for alert in new_alerts:
            if alert.level == AlertLevel.WARNING:
                health_score -= 10
            elif alert.level == AlertLevel.CRITICAL:
                health_score -= 25
        
        health_score = max(0, health_score)
        
        # Determine overall status
        if health_score >= 90:
            status = "healthy"
        elif health_score >= 70:
            status = "degraded"
        else:
            status = "unhealthy"
        
        return {
            "status": status,
            "health_score": health_score,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "current_metrics": {
                "cpu_percent": current_metrics.cpu_percent,
                "memory_percent": current_metrics.memory_percent,
                "disk_percent": current_metrics.disk_percent,
                "active_connections": current_metrics.active_connections,
                "response_time_avg": current_metrics.response_time_avg,
                "error_rate": current_metrics.error_rate,
                "throughput": current_metrics.throughput
            },
            "recent_alerts": [
                {
                    "level": alert.level.value,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "metric": alert.metric,
                    "value": alert.value,
                    "threshold": alert.threshold
                }
                for alert in self.alerts[-10:]  # Last 10 alerts
            ],
            "thresholds": self.thresholds
        }
    
    def get_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get metrics history for the specified time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            {
                "timestamp": metrics.timestamp.isoformat(),
                "cpu_percent": metrics.cpu_percent,
                "memory_percent": metrics.memory_percent,
                "disk_percent": metrics.disk_percent,
                "active_connections": metrics.active_connections,
                "response_time_avg": metrics.response_time_avg,
                "error_rate": metrics.error_rate,
                "throughput": metrics.throughput
            }
            for metrics in self.metrics_history
            if metrics.timestamp >= cutoff_time
        ]
    
    def get_alerts(self, level: Optional[AlertLevel] = None, hours: int = 24) -> List[Dict[str, Any]]:
        """Get alerts for the specified time period and level"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        filtered_alerts = [
            alert for alert in self.alerts
            if alert.timestamp >= cutoff_time and (level is None or alert.level == level)
        ]
        
        return [
            {
                "level": alert.level.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "metric": alert.metric,
                "value": alert.value,
                "threshold": alert.threshold
            }
            for alert in filtered_alerts
        ]

# Global monitor instance
monitor = ProductionMonitor()

# FastAPI router for monitoring endpoints
router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])

@router.get("/health")
async def get_health_status():
    """Get comprehensive system health status"""
    try:
        return monitor.get_health_status()
    except Exception as e:
        logger.error(f"Error getting health status: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/metrics")
async def get_metrics_history(hours: int = 24):
    """Get system metrics history"""
    try:
        if hours > 168:  # Max 1 week
            hours = 168
        
        return {
            "metrics": monitor.get_metrics_history(hours),
            "period_hours": hours
        }
    except Exception as e:
        logger.error(f"Error getting metrics history: {e}")
        raise HTTPException(status_code=500, detail=f"Metrics retrieval failed: {str(e)}")

@router.get("/alerts")
async def get_alerts(level: Optional[str] = None, hours: int = 24):
    """Get system alerts"""
    try:
        if hours > 168:  # Max 1 week
            hours = 168
        
        alert_level = None
        if level:
            try:
                alert_level = AlertLevel(level)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid alert level: {level}")
        
        return {
            "alerts": monitor.get_alerts(alert_level, hours),
            "level_filter": level,
            "period_hours": hours
        }
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Alerts retrieval failed: {str(e)}")

@router.get("/database/health")
async def get_database_health(db: Session = Depends(get_db)):
    """Get database health status"""
    try:
        # Test database connection
        start_time = time.time()
        db.execute(text("SELECT 1"))
        response_time = (time.time() - start_time) * 1000
        
        # Get database statistics
        stats = {}
        
        # Count records in major tables
        tables = ['users', 'automations', 'user_automations', 'payments', 'tickets']
        for table in tables:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                stats[f"{table}_count"] = result.scalar()
            except Exception as e:
                stats[f"{table}_count"] = f"Error: {str(e)}"
        
        return {
            "status": "healthy",
            "response_time_ms": response_time,
            "timestamp": datetime.utcnow().isoformat(),
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/cache/health")
async def get_cache_health():
    """Get cache health status"""
    try:
        cache_stats = get_cache_stats()
        
        # Test cache functionality
        test_key = "health_check_test"
        test_value = {"test": True, "timestamp": datetime.utcnow().isoformat()}
        
        start_time = time.time()
        cache.set(test_key, test_value, ttl=60)
        retrieved_value = cache.get(test_key)
        response_time = (time.time() - start_time) * 1000
        
        cache.delete(test_key)
        
        return {
            "status": "healthy" if retrieved_value == test_value else "unhealthy",
            "response_time_ms": response_time,
            "timestamp": datetime.utcnow().isoformat(),
            "statistics": cache_stats
        }
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/performance")
async def get_performance_metrics(db: Session = Depends(get_db)):
    """Get performance metrics"""
    try:
        # Get current system metrics
        current_metrics = monitor.collect_system_metrics()
        
        # Get database performance metrics
        db_start_time = time.time()
        db.execute(text("SELECT COUNT(*) FROM users"))
        db_response_time = (time.time() - db_start_time) * 1000
        
        # Get cache performance metrics
        cache_stats = get_cache_stats()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system_metrics": {
                "cpu_percent": current_metrics.cpu_percent,
                "memory_percent": current_metrics.memory_percent,
                "disk_percent": current_metrics.disk_percent
            },
            "database_metrics": {
                "response_time_ms": db_response_time,
                "active_connections": current_metrics.active_connections
            },
            "cache_metrics": cache_stats,
            "application_metrics": {
                "response_time_avg": current_metrics.response_time_avg,
                "error_rate": current_metrics.error_rate,
                "throughput": current_metrics.throughput
            }
        }
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Performance metrics retrieval failed: {str(e)}")

@router.post("/alerts/clear")
async def clear_alerts(current_admin: User = Depends(get_current_admin_user)):
    """Clear all alerts (admin only)"""
    try:
        monitor.alerts.clear()
        return {"message": "All alerts cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear alerts: {str(e)}")

@router.post("/thresholds/update")
async def update_thresholds(
    thresholds: Dict[str, float],
    current_admin: User = Depends(get_current_admin_user)
):
    """Update monitoring thresholds (admin only)"""
    try:
        # Validate thresholds
        valid_keys = set(monitor.thresholds.keys())
        for key, value in thresholds.items():
            if key not in valid_keys:
                raise HTTPException(status_code=400, detail=f"Invalid threshold key: {key}")
            if not isinstance(value, (int, float)) or value < 0:
                raise HTTPException(status_code=400, detail=f"Invalid threshold value for {key}: {value}")
        
        # Update thresholds
        monitor.thresholds.update(thresholds)
        
        return {
            "message": "Thresholds updated successfully",
            "new_thresholds": monitor.thresholds
        }
    except Exception as e:
        logger.error(f"Error updating thresholds: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update thresholds: {str(e)}")

# Background task for continuous monitoring
async def monitoring_background_task():
    """Background task for continuous monitoring"""
    while True:
        try:
            # Collect metrics and check thresholds
            metrics = monitor.collect_system_metrics()
            alerts = monitor.check_thresholds(metrics)
            
            # Log new alerts
            for alert in alerts:
                if alert.level == AlertLevel.CRITICAL:
                    logger.critical(f"CRITICAL ALERT: {alert.message}")
                elif alert.level == AlertLevel.WARNING:
                    logger.warning(f"WARNING ALERT: {alert.message}")
                else:
                    logger.info(f"INFO ALERT: {alert.message}")
            
            # Wait 30 seconds before next check
            await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f"Error in monitoring background task: {e}")
            await asyncio.sleep(60)  # Wait longer on error

# Start background monitoring task
async def start_monitoring():
    """Start the background monitoring task"""
    asyncio.create_task(monitoring_background_task())
    logger.info("Production monitoring started")
