"""
Database Configuration

Supports both SQLite (development) and MySQL (production)
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Import settings from config
from app.core.config import settings

# Base class for models
Base = declarative_base()


def get_database_url() -> str:
    """
    Get database URL based on configuration
    
    Returns:
        Database connection URL
    """
    if settings.DB_TYPE == "mysql":
        # MySQL URL
        url = (
            f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
            f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
            f"?charset=utf8mb4"
        )
        return url
    else:
        # SQLite URL (default)
        db_path = Path(settings.SQLITE_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{db_path}"


# Create engine
DATABASE_URL = get_database_url()

engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Database session dependency
    
    Usage in FastAPI:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database (create tables)
    Call this on application startup
    """
    Base.metadata.create_all(bind=engine)


def check_db_connection() -> bool:
    """
    Check if database connection is working
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))  
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False