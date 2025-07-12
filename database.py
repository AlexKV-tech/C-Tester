# During deployment, this will be replaced by a real database.
TEST_DB = {}
import sqlalchemy
import sqlalchemy.ext.declarative as declarative
import sqlalchemy.orm as orm


DB_URL = "postgresql://postgres:password@localhost/ctests_db"
engine = sqlalchemy.create_engine(DB_URL)
SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative.declarative_base()



