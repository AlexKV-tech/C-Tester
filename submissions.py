from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy import exists
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, JSONResponse
from templates import templates
from database import get_db
from schemas import CTestSubmission
import models

submission_router = APIRouter()


@submission_router.post("/submit-ctest")
async def submit_ctest(submission: CTestSubmission, db: Session = Depends(get_db)) -> JSONResponse:
    """
    Evaluates and stores a user's C-Test submission.

    - Validates test existence and expiration
    - Compares user answers against the solution key
    - Stores the result in the temporary database
    - Returns score and submission ID

    Args:
        submission: User's completed C-Test form

    Returns:
        JSON with score, total blanks, and confirmation message
    """
    try:
        test = db.query(models.CTest).filter(models.CTest.test_id == submission.test_id).first()
        if not test:
            raise HTTPException(status_code=404, detail="Test not found")
        current_time = datetime.now(timezone.utc)
        
        if test.expires_at < current_time:
            raise HTTPException(status_code=410, detail="Test has expired")
        db_submission = db.query(models.Submission).filter(models.Submission.test_id == submission.test_id).first()
        if db_submission is not None:
            return JSONResponse({
            "present": True,
            "score": db_submission.score,
            "submission_id": str(db_submission.submission_id),
            "message": "Ihr C-Test wurde schon abgesendet"
            })
        answers: dict[int, dict[str, str]] = test.answers
        if not answers:
            raise HTTPException(status_code=404, detail="Answers not found")
        score_data = calculate_score(answers, submission.answers)
        

        submission_data = {
            "test_id": str(submission.test_id),
            "user_answers": submission.answers,
            "score": score_data,
            "submitted_at": current_time
        }
        

        new_submission_entry = models.Submission(**submission_data)
        db.add(new_submission_entry)
        db.commit()
        db.refresh(new_submission_entry)
        return JSONResponse({
            "present": False,
            "score": score_data,
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


def calculate_score(correct_answers: dict, user_answers: dict):
    """
    Compares submitted answers against the correct ones.

    Args:
        correct_answers: Mapping of blank positions to (solution, expected_length)
        user_answers: Mapping of blank positions to user's input

    Returns:
        dict with:
            - correct: Number of correct responses
            - total: Total number of blanks
            - percentage: % of correct responses
            - detailed_results: Per-blank correctness and feedback
    """
    detailed_results = {}
    correct_count = 0
    
    for position, user_input in user_answers.items():
        expected_answer = ""
        expected_length = "0"
        answer_map = correct_answers.get(str(position))
        if answer_map:
            expected_answer = answer_map.get("answer", "")
            expected_length = answer_map.get("length", "0")
        else:
            raise ValueError(f"Answer on position {position} not found")

        normalized_user = user_input.lower().strip()
        normalized_expected = expected_answer.lower().strip()

        is_correct = normalized_user == normalized_expected
        if is_correct:
            correct_count += 1

        detailed_results[position] = {
            "user_answer": normalized_user,
            "expected_answer": normalized_expected,
            "expected_length": expected_length,
            "is_correct": is_correct
        }

    total = len(user_answers)
    percentage = (correct_count / total * 100) if total > 0 else 0

    return {
        "correct": correct_count,
        "total": total,
        "percentage": percentage,
        "detailed_results": detailed_results
    }


@submission_router.get("/results/{test_id}", response_class=HTMLResponse)
async def get_results(request: Request, test_id: str, db: Session = Depends(get_db)):
    """
    Displays all submissions for a given test.

    Args:
        request: FastAPI request
        test_id: ID of the test

    Returns:
        Renders results.html with all test submissions
    """
    try:
        test = db.query(models.CTest).filter(models.CTest.test_id == test_id).first()
        if not test:
            raise HTTPException(status_code=404, detail="Test not found")

        submissions = test.submissions
        submissions_length = sum(1 for _ in submissions)
        if not submissions_length:
            raise HTTPException(status_code=404, detail="No submissions for this test")

        return templates.TemplateResponse("results.html", {
            "request": request,
            "test_id": str(test_id),
            "submissions": [str(uuid) for uuid in submissions],
            "test_data": test
        })
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Result calculation service error: " + str(e)
        )
