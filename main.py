from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from datetime import datetime, timedelta
from typing import Dict
from ctest_gen import generate_ctest

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
TEST_DB = {}

class CTestTextInput(BaseModel):
    text: str # blanked test
    difficulty: str # difficulty of ther test either easy, medium or hard

class CTestSubmission(BaseModel):
    test_id: str 
    answers: Dict[int, str]  # answers of a user in form <index of answer>: <answer>
    original_text: str # original text that was blanked 



@app.get("/", response_class=HTMLResponse)
def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate")
def generate(input: CTestTextInput):
    try:
        output, answers = generate_ctest(input.text, input.difficulty)
        test_id = uuid.uuid4().hex[:8]
        created_at = datetime.utcnow()
        time_delta = timedelta(days=7) # time span after which the link for a created test will expire -> all information related to the test_id will be deleted from the DB
        expires_at = created_at + time_delta
        TEST_DB[test_id] = {
            "ctest_text": output,
            "created_at": created_at,
            "expires_at": expires_at,
            "answers": answers,
            "original_text": input.text,
            "submissions": {}
        }
        return {"ctest_text": output, "link": f"/test/{test_id}", "answers": answers}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/test/{test_id}", response_class=HTMLResponse)
def get_ctest_form(request: Request, test_id: str):
    test = TEST_DB.get(test_id)
    if not test or test["expires_at"] < datetime.utcnow():
        return templates.TemplateResponse("expired.html", {"request": request})

    return templates.TemplateResponse("ctest_form.html", {
        "request": request,
        "test_id": test_id,
        "ctest_text": test["ctest_text"],
        "blanks": {blank_id: blanks_info[1] for blank_id, blanks_info in zip(test["answers"].keys(), test["answers"].values())}
    })

@app.post("/submit-ctest")
async def submit_ctest(submission: CTestSubmission):
    # Fetch the test data(including answers, original text, etc.) related to the test id from the DB
    test = TEST_DB.get(submission.test_id)
    
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    if test["expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Test has expired")
    
    # Process the user's answers
    users_answers = submission.answers
    original_text = submission.original_text
    answers = test["answers"]
    
    print(f"Test ID: {submission.test_id}")
    print(f"User answers: {users_answers}")
    print(f"Original text: {original_text}")
    print(f"Blanks dict: {answers}")
    
    # Calculate score
    score = calculate_score(answers, users_answers)
    
    # Store the submission results in the DB
    submission_id = uuid.uuid4().hex[:8]
    TEST_DB[submission.test_id]["submissions"] = TEST_DB[submission.test_id].get("submissions", {})
    TEST_DB[submission.test_id]["submissions"][submission_id] = {
        "users_answers": users_answers,
        "score": score,
        "submitted_at": datetime.utcnow()
    }
    
    return {
        "status": "success",
        "score": score,
        "total_blanks": len(users_answers),
        "submission_id": submission_id,
        "message": "Ihr C-Test wurde erfolgreich abgesendet"
    }

def calculate_score(answers, users_answers):
    correct_answers = 0
    total_blanks = len(users_answers)
    detailed_results = {}
    
    # Compare user's answers with correct answers
    for position, users_answer in users_answers.items():
        # Find the corresponding blank information(the answer and the length) in blanks_dict
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

@app.get("/results/{test_id}", response_class=HTMLResponse)
def get_results(request: Request, test_id: str):
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