from datetime import datetime, timezone, timedelta
import uuid
import sqlalchemy
from . import database

"""
Database models for C-Test application.

Contains SQLAlchemy ORM classes representing:
- C_Tests: Generated language tests with solutions
- Submissions: Student responses to tests
"""

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


class Submission(database.Base):
    """
    Represents a student's test submission.

    Attributes:
        submission_id (UUID): Primary key, auto-generated
        ctest_id (UUID): Foreign key to CTest
        student_answers (JSON): {
            position: str  # Student's answer
        }
        given_hints (JSON): {
            position: str  # Hint that was used
        }
        score_data (JSON): {
            "correct_count": int,
            "total_count": int,
            "percentage": float,
            "detailed_results": {
                position: {
                    "student_answer": str,
                    "expected_answer": str,
                    "is_correct": bool
                }
            }
        }
        submitted_at (DateTime): Submission timestamp (UTC)

    Relationships:
        - Belongs to one CTest (one-to-one)
    """
    __tablename__ = "submissions"
    submission_id = sqlalchemy.Column("submission_id", sqlalchemy.Uuid(as_uuid=True), unique=True, primary_key=True, default=uuid.uuid4)
    ctest_id = sqlalchemy.Column("ctest_id", sqlalchemy.Uuid(as_uuid=True), unique=True, nullable=False)
    student_answers = sqlalchemy.Column("student_answers", sqlalchemy.JSON, nullable=False)
    given_hints  = sqlalchemy.Column("given_hints", sqlalchemy.JSON, nullable=False) 
    score_data = sqlalchemy.Column("score_data", sqlalchemy.JSON, nullable=False)
    submitted_at = sqlalchemy.Column("submitted_at",sqlalchemy.DateTime(timezone=True), default=datetime.now(timezone.utc))
    