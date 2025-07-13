from datetime import datetime, timezone, timedelta
import sqlalchemy
import database

class CTest(database.Base):
    __tablename__ = "c_tests"
    test_id = sqlalchemy.Column("test_id", sqlalchemy.Integer, primary_key=True, index=True)
    ctest_text = sqlalchemy.Column("ctest_text",sqlalchemy.String, index=True)
    original_text = sqlalchemy.Column("original_text",sqlalchemy.String, index=True)
    created_at = sqlalchemy.Column("created_at",sqlalchemy.DateTime, default=datetime.now(timezone.utc))
    expires_at  = sqlalchemy.Column("expires_at",sqlalchemy.DateTime, default=datetime.now(timezone.utc)+timedelta(days=7))
    answers = sqlalchemy.Column("answers", sqlalchemy.JSON)



