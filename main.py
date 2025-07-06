from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from datetime import datetime, timedelta
from ctest_gen import generate_ctest
TEST_DB = {}

class TextInput(BaseModel):
    text:str
    difficulty:str

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate")
def generate(input: TextInput):
    try:
        output = generate_ctest(input.text, input.difficulty)
        test_id = uuid.uuid4().hex[:8]
        expires_at = datetime.utcnow() + timedelta(days=7)
        TEST_DB[test_id] = {
            "original_text": input.text,
            "difficulty": input.difficulty,
            "ctest_items": output,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at
        }
        return {"ctest": output, "link": f"/test/{test_id}"}
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=str(e))

    
@app.get("/test/{test_id}", response_class=HTMLResponse)
def get_ctest_form(request: Request, test_id: str):
    test = TEST_DB.get(test_id)

    if not test or test["expires_at"] < datetime.utcnow():
        return templates.TemplateResponse("expired.html", {"request": request})

    return templates.TemplateResponse("ctest_form.html", {
        "request": request,
        "test_id": test_id,
        "ctest_text": test["ctest_items"],
    })

