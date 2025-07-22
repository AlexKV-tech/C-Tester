from fastapi.responses import HTMLResponse
import pdf_gen
import test_gen
import submissions
import form_gen
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from templates import templates
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET"))
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(pdf_gen.generator_router)
app.include_router(test_gen.generator_router)
app.include_router(submissions.submission_router)
app.include_router(form_gen.form_router)

@app.get("/", response_class=HTMLResponse)
def serve_home(request: Request):
    """Serves the main C-Test generator page to users."""
    return templates.TemplateResponse("index.html", {"request": request})


    



