from datetime import datetime, timezone, timedelta
import uuid
import sqlalchemy
import database

class CTest(database.Base):
    __tablename__ = "c_tests"
    test_id = sqlalchemy.Column("test_id", sqlalchemy.Uuid(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    ctest_text = sqlalchemy.Column("ctest_text",sqlalchemy.String, nullable=False)
    original_text = sqlalchemy.Column("original_text",sqlalchemy.String, nullable=False)
    created_at = sqlalchemy.Column("created_at",sqlalchemy.DateTime(timezone=True), default=datetime.now(timezone.utc))
    expires_at  = sqlalchemy.Column("expires_at",sqlalchemy.DateTime(timezone=True), default=datetime.now(timezone.utc)+timedelta(days=7))
    answers = sqlalchemy.Column("answers", sqlalchemy.JSON,nullable=False)
    submissions = sqlalchemy.Column("submissions", sqlalchemy.ARRAY(sqlalchemy.Uuid(as_uuid=True), zero_indexes=True), default=[])
    code = sqlalchemy.Column(sqlalchemy.String(6), nullable=False)


class Submission(database.Base):
    __tablename__ = "submissions"
    submission_id = sqlalchemy.Column("submission_id", sqlalchemy.Uuid(as_uuid=True), unique=True, primary_key=True, default=uuid.uuid4)
    test_id = sqlalchemy.Column("test_id", sqlalchemy.Uuid(as_uuid=True), unique=True, nullable=False)
    user_answers = sqlalchemy.Column("user_answers", sqlalchemy.JSON, nullable=False)
    score = sqlalchemy.Column("score", sqlalchemy.JSON, nullable=False)
    submitted_at = sqlalchemy.Column("submitted_at",sqlalchemy.DateTime(timezone=True), default=datetime.now(timezone.utc))
    