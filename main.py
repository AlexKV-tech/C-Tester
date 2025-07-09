from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from datetime import datetime, timedelta
from typing import Dict
from ctest_gen import generate_ctest
from pdf_gen import generate_pdf_ctest
import tempfile, os

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
    text: str # text to be modified
    difficulty: str # difficulty of ther test either easy, medium or hard

class CTestSubmission(BaseModel):
    test_id: str 
    answers: Dict[int, str]  # answers of a user in form <index of answer>: <answer>
    original_text: str # original text that was blanked 



@app.get("/", response_class=HTMLResponse)
def serve_home(request: Request):
    """ 
    Serve user to main page - generator of C-Tests
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate")
async def generate(input: CTestTextInput):
    """
    Accept original text(input: CTestTextInput) and generate C-Test from it. 
    Original text, generated C-Test, creation date, expiring data, answers and submission are written into database
    """
    output, answers = generate_ctest(input.text, input.difficulty)
    test_id = uuid.uuid4().hex[:8]
    created_at = datetime.utcnow()
    time_delta = timedelta(days=7) # time span after which the link for a created test will expire -> all information related to the test_id will be deleted from the DB
    expires_at = created_at + time_delta
    # Write C-Test data into database
    TEST_DB[test_id] = {
        "ctest_text": output,
        "created_at": created_at,
        "expires_at": expires_at,
        "answers": answers,
        "original_text": input.text,
        "submissions": {}
    }
    return {"ctest_text": output, "link": f"/test/{test_id}", "answers": answers}
    

@app.get("/test/{test_id}", response_class=HTMLResponse)
async def get_ctest_form(request: Request, test_id: str):
    """
    Accepts test_id: str -- id of the test
    Returns either page noting expiration of 
    the test(failure) or page rendered corresponding to the test_id(success)("blanks" helps rendering blanks in JS part)
    """
    test = TEST_DB.get(test_id)
    if not test or test["expires_at"] < datetime.utcnow():
        return templates.TemplateResponse("expired.html", {"request": request}, status_code=410)

    return templates.TemplateResponse("ctest_form.html", {
        "request": request,
        "test_id": test_id,
        "ctest_text": test["ctest_text"],
        "blanks": {blank_id: blanks_info[1] for blank_id, blanks_info in zip(test["answers"].keys(), test["answers"].values())}
    })

@app.post("/submit-ctest")
async def submit_ctest(submission: CTestSubmission):
    """
    Receives user's C-Test submission, grades it, stores the submission data into database
    Returns achieved score, total number of blanks, submission id and message indicating whther the request was successful
    """

    # Fetch the test data(including answers, original text, etc.) related to the test id from the DB
    test = TEST_DB.get(submission.test_id)
    
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    if test["expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Test has expired")
    
    
    users_answers = submission.answers
    original_text = submission.original_text
    answers = test["answers"]
    
    print(f"Test ID: {submission.test_id}")
    print(f"User answers: {users_answers}")
    print(f"Original text: {original_text}")
    print(f"Blanks dict: {answers}")
    
    
    score = calculate_score(answers, users_answers)
    
    # Store the submission results in the DB
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

@app.get("/results/{test_id}", response_class=HTMLResponse)
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

@app.post("/generate_pdf", response_class=HTMLResponse)
async def get_printable_pdf(input: CTestTextInput, background_tasks: BackgroundTasks):
    """
    Accept original text(input: CTestTextInput) and generate C-Test from it. 

    """
    
    output, _ = generate_ctest(input.text, input.difficulty)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.close()
    generate_pdf_ctest(output, tmp.name)
    
    background_tasks.add_task(os.remove, tmp.name)
    return FileResponse(tmp.name, filename="printable.pdf", media_type="application/pdf")
    
    


'''
from fastapi import FastAPI, Form, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fpdf import FPDF
import tempfile, os

app = FastAPI()

# 👇 This trick lets you use Pydantic with Form data!
class FormModel(BaseModel):
    message: str

    @classmethod
    def as_form(cls, message: str = Form(...)):
        return cls(message=message)

@app.post("/generate-pdf")
def generate_pdf(
    form_data: FormModel = Depends(FormModel.as_form),
    background_tasks: BackgroundTasks = Depends()
):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=14)
    pdf.multi_cell(0, 10, f"💬 User input:\n\n{form_data.message}")
    pdf.output(tmp.name)

    background_tasks.add_task(os.remove, tmp.name)
    return FileResponse(tmp.name, filename="generated.pdf", media_type="application/pdf")



'''