from app.core.config import DB_URL

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



engine = create_engine(DB_URL)

# Session factory for creating individual database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models to inherit from
Base = declarative_base()

def add_tables():
    """
    Creates all defined database tables in the connected database.

    This function:
    - Uses SQLAlchemy's metadata system
    - Creates tables for all models that inherit from Base
    - Binds to the engine defined in the database module
    - Is typically called once during application startup

    Note:
    - Safe to call multiple times (won't recreate existing tables)
    - Only creates tables that don't already exist
    - Requires proper database connection configuration
    """
    return Base.metadata.create_all(bind=engine)
