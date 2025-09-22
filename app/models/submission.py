from app.db import database

from datetime import datetime, timezone, timedelta
import uuid
import sqlalchemy





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
    