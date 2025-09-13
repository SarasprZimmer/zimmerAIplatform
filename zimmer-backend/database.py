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

# Get DATABASE_URL from environment, fallback to SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
if DATABASE_URL is None or DATABASE_URL.strip() == "":
    DATABASE_URL = "sqlite:///./dev.db"
    print("⚠️  No DATABASE_URL found in .env, using SQLite for development")

# Configure engine with highly optimized connection pooling
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration - highly optimized for performance
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "check_same_thread": False,
            "timeout": 10,  # Reduced timeout for faster failure detection
            "isolation_level": None  # Autocommit mode for better performance
        },
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
    # PostgreSQL configuration - highly optimized for performance
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=3,  # Further reduced pool size
        max_overflow=5,  # Further reduced overflow
        pool_pre_ping=True,
        pool_recycle=900,  # 15 minutes recycle (faster)
        future=True,
        echo=False,
        pool_timeout=10,  # Faster timeout
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
        raise e
    finally:
        db.close() 