from app.db import database

from datetime import datetime, timezone, timedelta
import uuid
import sqlalchemy




class CTest(database.Base):
    """
    Represents a generated C-Test language exercise.

    Attributes:
        ctest_id (UUID): Primary key, auto-generated
        ctest_text (str): The test text with blanks
        original_text (str): Unmodified source text
        created_at (DateTime): Creation timestamp (UTC)
        expires_at (DateTime): Automatic expiration (7 days after creation)
        correct_answers (JSON): {
            position: {
                "answer": str,  # Correct word
                "length": str   # Blank length
            }
        }
        submissions (ARRAY[UUID]): List of related submission IDs
        student_code (str): 6-digit access code for students
        teacher_code (str): 6-digit access code for teachers

    Relationships:
        - Has many Submissions (one-to-many)
    """
    __tablename__ = "c_tests"
    ctest_id = sqlalchemy.Column("ctest_id", sqlalchemy.Uuid(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    ctest_text = sqlalchemy.Column("ctest_text",sqlalchemy.String, nullable=False)
    original_text = sqlalchemy.Column("original_text",sqlalchemy.String, nullable=False)
    created_at = sqlalchemy.Column("created_at",sqlalchemy.DateTime(timezone=True), default=datetime.now(timezone.utc))
    expires_at  = sqlalchemy.Column("expires_at",sqlalchemy.DateTime(timezone=True), default=datetime.now(timezone.utc)+timedelta(days=7))
    correct_answers = sqlalchemy.Column("correct_answers", sqlalchemy.JSON,nullable=False)
    submissions = sqlalchemy.Column("submissions", sqlalchemy.ARRAY(sqlalchemy.Uuid(as_uuid=True), zero_indexes=True), default=[])
    student_code = sqlalchemy.Column(sqlalchemy.String(6), nullable=False)
    teacher_code = sqlalchemy.Column(sqlalchemy.String(6), nullable=False)