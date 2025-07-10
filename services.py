import database

def add_tables():
    return database.Base.metadata.create_all(bind=database.engine)
