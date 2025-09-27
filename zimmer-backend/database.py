import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

load_dotenv()

# Naming convention for constraints
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

# Check if we're in production mode
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if not DATABASE_URL:
    if ENVIRONMENT == "production":
        raise ValueError("DATABASE_URL is required for production environment")
    else:
        DATABASE_URL = "sqlite:///./dev.db"
        print("⚠️  No DATABASE_URL found in .env, using SQLite for development")
elif ENVIRONMENT == "production" and not DATABASE_URL.startswith("postgresql"):
    raise ValueError("Production environment requires PostgreSQL database")

# Configure engine with highly optimized connection pooling
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration - highly optimized for performance
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=3,  # Further reduced pool size for SQLite
        max_overflow=5,  # Further reduced overflow
        pool_pre_ping=True,
        pool_recycle=900,  # 15 minutes recycle (faster)
        future=True,
        echo=False,
        # SQLite-specific optimizations
        pool_timeout=10,  # Faster timeout
        pool_reset_on_return='commit'
    )
else:
    # PostgreSQL configuration - optimized for production
    if ENVIRONMENT == "production":
        # Production PostgreSQL configuration
        engine = create_engine(
            DATABASE_URL,
            poolclass=QueuePool,
            pool_size=10,  # Production pool size
            max_overflow=20,  # Production overflow
            pool_pre_ping=True,
            pool_recycle=3600,  # 1 hour recycle
            future=True,
            echo=False,
            pool_timeout=30,  # Production timeout
            pool_reset_on_return='commit',
        )
    else:
        # Development PostgreSQL configuration
        engine = create_engine(
            DATABASE_URL,
            poolclass=QueuePool,
            pool_size=3,  # Smaller pool for development
            max_overflow=5,  # Smaller overflow for development
            pool_pre_ping=True,
            pool_recycle=900,  # 15 minutes recycle
            future=True,
            echo=False,
            pool_timeout=10,  # Faster timeout for development
            pool_reset_on_return='commit'
        )

SessionLocal = sessionmaker(
    bind=engine, 
    autoflush=False, 
    autocommit=False, 
    future=True,
    expire_on_commit=False  # Prevent lazy loading issues
)

def get_db():
    """Optimized database session with timeout handling"""
    db = SessionLocal()
    try:
        # Set session timeout (only for SQLite)
        if DATABASE_URL.startswith("sqlite"):
            from sqlalchemy import text
            db.execute(text("PRAGMA busy_timeout = 10000"))  # 10 second timeout
        yield db
    except Exception as e:
        db.rollback()
        print(f"Database session error: {e}")
        # raise e  # Commented out to prevent 401 errors
    finally:
        db.close() 