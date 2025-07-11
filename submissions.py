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
    Receives user's C-Test submission, grades it, stores the submission data into database
    Returns achieved score, total number of blanks, submission id and message indicating whther the request was successful
    """

    # Fetch the test data(including answers, original text, etc.) related to the test id from the DB - will be replaced by real DB when deploying
    test = TEST_DB.get(submission.test_id)
    
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    if test["expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Test has expired")
    
    
    users_answers = submission.answers
    answers = test["answers"]
    score = calculate_score(answers, users_answers)
    
    # Store the submission results in the DB - will be replaced by real DB when deploying
    submission_id = uuid.uuid4().hex[:8]
    TEST_DB[submission.test_id]["submissions"] = TEST_DB[submission.test_id].get("submissions", {})
    TEST_DB[submission.test_id]["submissions"][submission_id] = {
        
        "users_answers": users_answers,
        "score": score,
        "submitted_at": datetime.utcnow()
    }
    
    return JSONResponse({
        "score": score,
        "total_blanks": len(users_answers),
        "submission_id": submission_id,
        "message": "Ihr C-Test wurde erfolgreich abgesendet"
    }, status_code=200)

def calculate_score(answers, users_answers):
    """
    Calculates achieved score comparing sample answers with user's answers
    Returns number of correct answers, number of blanks in total, percentage 
    of correct answers and map detailed_results, which for each word with missed part contains: 
    user answer, expected anser, expected length of the answer, bool variable indicating whether 
    the answer was correct
    """
    correct_answers = 0
    total_blanks = len(users_answers)
    detailed_results = {}
    

    for position, users_answer in users_answers.items():
        
        expected_answer = answers[position][0]  # expected answer
        expected_length = answers[position][1]   # expected length of the answer
        
        # Answers are case and whitespace insensitive
        users_answer = users_answer.lower().strip()
        expected_answer = expected_answer.lower().strip()

        is_correct = users_answer == expected_answer
        if is_correct:
            correct_answers += 1
        
        detailed_results[position] = {
            "user_answer": users_answer,
            "expected_answer": expected_answer,
            "expected_length": expected_length,
            "is_correct": is_correct
        }
    
    percentage = (correct_answers * 100 / total_blanks) if total_blanks > 0 else 0
    
    return {
        "correct": correct_answers,
        "total": total_blanks,
        "percentage": percentage,
        "detailed_results": detailed_results
    }

@submission_router.get("/results/{test_id}", response_class=HTMLResponse)
async def get_results(request: Request, test_id: str):
    """
    Accepts test id
    Returns information corresponding to submission for requested test id
    """
    test = TEST_DB.get(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    submissions = test.get("submissions", {})
    return templates.TemplateResponse("results.html", {
        "request": request,
        "test_id": test_id,
        "submissions": submissions,
        "test_data": test
    })


    

