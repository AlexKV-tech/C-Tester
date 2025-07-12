import datetime 
import sqlalchemy
import database

class CTest(database.Base):
    __tablename__ = "c_tests"
    test_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    ctest_text = sqlalchemy.Column(sqlalchemy.String, index=True)
    original_text = sqlalchemy.Column(sqlalchemy.String, index=True)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.utcnow)
    expires_at  = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.utcnow)




