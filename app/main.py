from app.db.database import add_tables
from app.routers.ctest_pdf_generator import pdf_generator_router
from app.routers.ctest_unit_generator import ctest_generator_router
from app.routers.ctest_unit_submission import submission_router
from app.routers.ctest_unit_form import form_router
from app.routers.ctest_unit_result import results_router
from app.routers.ctest_mainpage import mainpage_router
from app.dependencies import templates

from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
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
    "/frontend",
    StaticFiles(directory=os.path.join(os.getcwd(), "frontend")),
    name="frontend",
    
)

app.include_router(
    pdf_generator_router,
    tags=["PDF Generation"],
    prefix="/api" 
)
app.include_router(
    ctest_generator_router,
    tags=["Test Generation"],
    prefix="/api" 
)
app.include_router(
    submission_router,
    tags=["Submissions"],
    prefix="/api" 
)
app.include_router(
    form_router,
    tags=["Student Interface"],
    prefix="/api" 
)
app.include_router(
    results_router,
    tags=["Teacher Interface"],
    prefix="/api" 
)
app.include_router(
    mainpage_router,
    tags=["Homepage"]
)


@app.on_event("startup")
async def on_startup():
    print("Creating tables if they do not exist")
    add_tables()