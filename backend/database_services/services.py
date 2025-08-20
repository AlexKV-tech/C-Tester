from . import database
import backend.database_services.models

"""Database table initialization utility."""

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
    return database.Base.metadata.create_all(bind=database.engine)
