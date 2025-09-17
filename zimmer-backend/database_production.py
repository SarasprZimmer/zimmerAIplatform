"""
Production Database Configuration for Zimmer Platform
Optimized for PostgreSQL with production-ready settings
"""

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

load_dotenv()

# Naming convention for constraints (PostgreSQL best practices)
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(metadata=metadata)

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required for production")

if not DATABASE_URL.startswith("postgresql"):
    raise ValueError("Production requires PostgreSQL database")

# Production-optimized PostgreSQL configuration
engine = create_engine(
    DATABASE_URL,
    # Connection pooling for production
    poolclass=QueuePool,
    pool_size=10,  # Base number of connections to maintain
    max_overflow=20,  # Additional connections when pool is exhausted
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle connections every hour
    
    # Performance optimizations
    future=True,  # Use SQLAlchemy 2.0 style
    echo=False,  # Disable SQL logging in production
    pool_timeout=30,  # Timeout for getting connection from pool
    pool_reset_on_return='commit',  # Reset connections on return
    
    # PostgreSQL-specific optimizations
    connect_args={
        "options": "-c default_transaction_isolation=read_committed"
    }
)

# Production session configuration
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,  # Manual control over flushing
    autocommit=False,  # Manual control over commits
    future=True,  # Use SQLAlchemy 2.0 style
    expire_on_commit=False  # Prevent lazy loading issues
)

def get_db():
    """
    Production database session with proper error handling
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        print(f"Database session error: {e}")
        raise e
    finally:
        db.close()

def get_db_sync():
    """
    Synchronous database session for non-async operations
    """
    return SessionLocal()

def test_connection():
    """
    Test database connection for health checks
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False

def get_connection_info():
    """
    Get database connection information (without sensitive data)
    """
    if "@" in DATABASE_URL:
        # Extract host and database name
        url_part = DATABASE_URL.split("@")[1]
        if "/" in url_part:
            host_port, database = url_part.split("/", 1)
            return {
                "host": host_port.split(":")[0] if ":" in host_port else host_port,
                "database": database.split("?")[0] if "?" in database else database,
                "type": "PostgreSQL"
            }
    return {"type": "PostgreSQL", "status": "configured"}

# Production database health check
def health_check():
    """
    Comprehensive database health check
    """
    try:
        # Test basic connection
        if not test_connection():
            return {"status": "unhealthy", "error": "Connection failed"}
        
        # Test query performance
        with engine.connect() as conn:
            result = conn.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
            table_count = result.scalar()
            
            if table_count < 10:  # Expected minimum number of tables
                return {"status": "unhealthy", "error": f"Only {table_count} tables found"}
        
        return {
            "status": "healthy",
            "connection": get_connection_info(),
            "tables": table_count
        }
        
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
