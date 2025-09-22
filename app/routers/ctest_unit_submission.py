from app.models.ctest import CTest
from app.dependencies import get_db
from app.schemas.submission import Submission
from app.models.submission import Submission as dbSubmission
from app.services.ctest_unit_submission_service import calculate_score


from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse








"""FastAPI router for handling C-Test submissions."""

submission_router = APIRouter()


@submission_router.post("/submit-ctest")
async def submit_ctest(submission: Submission, db: Session = Depends(get_db)) -> JSONResponse:
    """
    Submit a C-Test and calculate scores.

    Args:
        submission (Submission): The student's test submission data.
        db (Session): SQLAlchemy database session (dependency injection).

    Returns:
        JSONResponse: Contains either:
            - Existing submission data (if test was already submitted)
            - New submission results (if first submission)
            - Error details (if test invalid/expired)

    Raises:
        HTTPException: 404 if test/answers not found
                     410 if test expired
                     400 for validation errors
                     500 for server errors
    """
    try:
        db_ctest = db.query(CTest).filter(CTest.ctest_id == submission.ctest_id).first()
        if not db_ctest:
            raise HTTPException(status_code=404, detail="Test not found")
        current_time = datetime.now(timezone.utc)
        
        if db_ctest.expires_at < current_time:
            raise HTTPException(status_code=410, detail="Test has expired")
        db_submission = db.query(dbSubmission).filter(dbSubmission.ctest_id == submission.ctest_id).first()
        if db_submission is not None:
            return JSONResponse({
            "was_in_db": True,
            "score_data": db_submission.score_data,
            "submission_id": str(db_submission.submission_id),
            "message": "Ihr C-Test wurde schon abgesendet"
            })
        correct_answers: dict[int, dict[str, str]] = db_ctest.correct_answers
        if not correct_answers:
            raise HTTPException(status_code=404, detail="Answers not found")
        score_data = await calculate_score(correct_answers, submission.student_answers)
        submission_data = {
            "ctest_id": str(submission.ctest_id),
            "student_answers": submission.student_answers,
            "given_hints": {
                key: "".join(map(lambda ch: "_" if ch is None else ch, value)) 
                    for key, value in submission.given_hints.items()
            },
            "score_data": score_data,
            "submitted_at": current_time
        }
        new_submission_entry = Submission(**submission_data)
        db.add(new_submission_entry)
        db.commit()
        db.refresh(new_submission_entry)
        return JSONResponse({
            "was_in_db": False,
            "score_data": score_data,
            "submission_id": str(new_submission_entry.submission_id),
            "message": "Ihr C-Test wurde erfolgreich abgesendet"
        })
    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail=str(ve),

        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Submission rendering service error: " + str(e)
        )


