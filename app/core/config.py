import sqlalchemy.ext.declarative as declarative
import sqlalchemy.orm as orm
import os

"""
Basic PostgreSQL database configuration for C-Test application.

Provides:
- SQLAlchemy engine configuration
- Session factory setup
- Base class for ORM models
- Database connection management
"""

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/db")


