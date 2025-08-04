from fastapi.responses import HTMLResponse
import test_generation.pdf_ctest_gen as pdf_ctest_gen
import test_generation.ctest_gen as ctest_gen
import user_handling.ctest_submissions as submissions
import user_handling.ctest_form as form
import user_handling.ctest_results as results
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from app_services.templates import templates
import os
from dotenv import load_dotenv

"""
C-Test Language Application - FastAPI Main Configuration

Core application setup including:
- Middleware configuration
- Router integration
- Static file serving
- Security settings
- Environment management
"""


load_dotenv()


app = FastAPI(
    title="C-Test Language Application",
    description="Web service for generating and evaluating C-Test language exercises",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],  
    allow_headers=["*"],
    allow_credentials=True
)


app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET"), 
    session_cookie="ctest_session",  # Cookie name for session tracking
    max_age=3600  # Session expires after 1 hour (in seconds)
)


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static" 
)

app.include_router(
    pdf_ctest_gen.pdf_generator_router,
    tags=["PDF Generation"]
)
app.include_router(
    ctest_gen.ctest_generator_router,
    tags=["Test Generation"]
)
app.include_router(
    submissions.submission_router,
    tags=["Submissions"]
)
app.include_router(
    form.form_router,
    tags=["Student Interface"]
)
app.include_router(
    results.results_router,
    tags=["Teacher Interface"]
)

@app.get("/", response_class=HTMLResponse)
def serve_home(request: Request):
    """
    Serves the application's main entry point.

    Args:
        request (Request): Incoming FastAPI request object

    Returns:
        TemplateResponse: Rendered HTML template for the main interface

    Notes:
        - Uses Jinja2 template located at static/templates/ctest-mainpage.html
        - Automatically injects request context into template
    """
    return templates.TemplateResponse("ctest-mainpage.html", {"request": request})