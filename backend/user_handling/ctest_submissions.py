from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from backend.database_services.database import get_db
from backend.app_services.schemas import CTestSubmission
import backend.database_services.models as models

"""FastAPI router for handling C-Test submissions."""

submission_router = APIRouter()


@submission_router.post("/submit-ctest")
async def submit_ctest(submission: CTestSubmission, db: Session = Depends(get_db)) -> JSONResponse:
    """
    Submit a C-Test and calculate scores.

    Args:
        submission (CTestSubmission): The student's test submission data.
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
        db_ctest = db.query(models.CTest).filter(models.CTest.ctest_id == submission.ctest_id).first()
        if not db_ctest:
            raise HTTPException(status_code=404, detail="Test not found")
        current_time = datetime.now(timezone.utc)
        
        if db_ctest.expires_at < current_time:
            raise HTTPException(status_code=410, detail="Test has expired")
        db_submission = db.query(models.Submission).filter(models.Submission.ctest_id == submission.ctest_id).first()
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
        new_submission_entry = models.Submission(**submission_data)
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


async def calculate_score(correct_answers: dict, student_answers: dict):
    """
    Calculate scoring metrics by comparing student answers with correct solutions.

    Args:
        correct_answers (dict): {
            position: {
                "answer": str, 
                "length": str
            }
        }
        student_answers (dict): {position: student_input}

    Returns:
        dict: Score report containing:
            - correct_count (int)
            - total_count (int)
            - percentage (float)
            - detailed_results (dict per position)

    Raises:
        ValueError: If any answer position is missing in correct_answers
    """    
    detailed_results = {}
    correct_count = 0
    
    for position, student_input in student_answers.items():
        expected_answer = ""
        expected_length = "0"
        correct_answer_map = correct_answers.get(str(position))
        if correct_answer_map:
            expected_answer = correct_answer_map.get("answer", "")
            expected_length = correct_answer_map.get("length", "0")
        else:
            raise ValueError(f"Answer on position {position} not found")

        normalized_student_answer = student_input.lower().strip()
        normalized_expected_answer = expected_answer.lower().strip()

        is_correct = normalized_student_answer == normalized_expected_answer
        if is_correct:
            correct_count += 1

        detailed_results[position] = {
            "student_answer": normalized_student_answer,
            "expected_answer": normalized_expected_answer,
            "expected_length": expected_length,
            "is_correct": is_correct
        }

    total_count = len(student_answers)
    percentage = (correct_count / total_count * 100) if total_count > 0 else 0

    return {
        "correct_count": correct_count,
        "total_count": total_count,
        "percentage": percentage,
        "detailed_results": detailed_results
    }


