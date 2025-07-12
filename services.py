import database
from models import CTest


def add_tables():
    return database.Base.metadata.create_all(bind=database.engine)
add_tables()