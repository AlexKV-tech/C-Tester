from datetime import datetime
import uuid
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from templates import templates
from database import TEST_DB
from schemas import CTestSubmission

submission_router = APIRouter()


@submission_router.post("/submit-ctest")
async def submit_ctest(submission: CTestSubmission):
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
    test = TEST_DB.get(submission.test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    if test["expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Test has expired")

    answers = test["answers"]
    score_data = calculate_score(answers, submission.answers)

    submission_id = uuid.uuid4().hex[:8]
    TEST_DB[submission.test_id].setdefault("submissions", {})
    TEST_DB[submission.test_id]["submissions"][submission_id] = {
        "user_answers": submission.answers,
        "score": score_data,
        "submitted_at": datetime.utcnow()
    }

    return JSONResponse({
        "score": score_data["correct"],
        "total_blanks": score_data["total"],
        "submission_id": submission_id,
        "message": "Ihr C-Test wurde erfolgreich abgesendet"
    })


def calculate_score(correct_answers: dict, user_answers: dict) -> dict:
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
        expected_answer, expected_length = correct_answers.get(position, ("", 0))

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
async def get_results(request: Request, test_id: str):
    """
    Displays all submissions for a given test.

    Args:
        request: FastAPI request
        test_id: ID of the test

    Returns:
        Renders results.html with all test submissions
    """
    test = TEST_DB.get(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    submissions = test.get("submissions")
    if not submissions:
        raise HTTPException(status_code=404, detail="No submissions for this test")

    return templates.TemplateResponse("results.html", {
        "request": request,
        "test_id": test_id,
        "submissions": submissions,
        "test_data": test
    })
