from datetime import datetime, timezone, timedelta
import uuid
import sqlalchemy
import database

class CTest(database.Base):
    __tablename__ = "c_tests"
    test_id = sqlalchemy.Column("test_id", sqlalchemy.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    ctest_text = sqlalchemy.Column("ctest_text",sqlalchemy.String, index=True)
    original_text = sqlalchemy.Column("original_text",sqlalchemy.String, index=True)
    created_at = sqlalchemy.Column("created_at",sqlalchemy.DateTime(timezone=True), default=datetime.now(timezone.utc))
    expires_at  = sqlalchemy.Column("expires_at",sqlalchemy.DateTime(timezone=True), default=datetime.now(timezone.utc)+timedelta(days=7))
    answers = sqlalchemy.Column("answers", sqlalchemy.JSON)
    submissions = sqlalchemy.Column("submissions", sqlalchemy.ARRAY(sqlalchemy.Uuid(as_uuid=True), zero_indexes=True), default=[])


class Submission(database.Base):
    __tablename__ = "submissions"
    submission_id = sqlalchemy.Column("submission_id", sqlalchemy.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    test_id = sqlalchemy.Column("test_id", sqlalchemy.Uuid(as_uuid=True), index=True, unique=True)
    user_answers = sqlalchemy.Column("user_answers", sqlalchemy.JSON)
    score = sqlalchemy.Column("score", sqlalchemy.JSON)
    submitted_at = sqlalchemy.Column("submitted_at",sqlalchemy.DateTime(timezone=True), default=datetime.now(timezone.utc))
    