import sqlalchemy
import sqlalchemy.ext.declarative as declarative
import sqlalchemy.orm as orm

"""
Basic PostgreSQL database configuration for C-Test application.

Provides:
- SQLAlchemy engine configuration
- Session factory setup
- Base class for ORM models
- Database connection management
"""

# Database connection URL (format: postgresql://user:password@host/database)
DB_URL = "postgresql://postgres:password@localhost/ctests_db"

# SQLAlchemy engine instance (main interface to database)
engine = sqlalchemy.create_engine(DB_URL)

# Session factory for creating individual database sessions
SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models to inherit from
Base = declarative.declarative_base()

def get_db():
    """
    Dependency generator for database sessions.
    
    Yields:
        Session: A new database session
    
    Ensures:
        - Session is properly closed after use
        - Session is available for a single request
        - Cleanup happens even if exceptions occur
    
    Usage:
        >>> db = next(get_db())  # In FastAPI endpoints use Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
