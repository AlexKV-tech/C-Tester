from app.models.ctest import CTest
from app.dependencies import get_db, templates

from datetime import datetime, timezone
from fastapi import APIRouter, Form, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session


"""FastAPI router for student authentication and C-Test form handling."""


form_router = APIRouter()

@form_router.get("/student_authorize/{ctest_id}", response_class=HTMLResponse)
async def get_form_auth(request: Request, ctest_id: str):
    """
    Display student authentication page for C-Test access.
    
    Args:
        request (Request): FastAPI request object containing client information
        ctest_id (str): Unique identifier for the C-Test being accessed
        
    Returns:
        TemplateResponse: Renders ctest-auth.html template with:
            - request: Current request context
            - ctest_id: Test identifier for form submission
            - error: Initial null error state
    """
    return templates.TemplateResponse("ctest-auth.html", {"request": request, "ctest_id": ctest_id, "error": None})

@form_router.post("/student_authorize/{ctest_id}")
async def redirect_form_auth(request: Request, ctest_id: str, code: str = Form(...), db: Session = Depends(get_db)):
    """
    Process student authentication and grant test access.
    
    Args:
        request (Request): FastAPI request object
        ctest_id (str): Unique test identifier from URL
        code (str): Student access code from form submission
        db (Session): Active database session
        
    Returns:
        RedirectResponse: To test form on successful authentication (302)
        TemplateResponse: Re-renders auth page with error message on failure (400)
        
    Behavior:
        - Validates student code against database record
        - Sets session authentication flag if successful
        - Maintains test context during redirects
    """
    otp_entry = db.query(CTest).filter_by(ctest_id=ctest_id).first()
    if otp_entry and otp_entry.student_code == code:
        request.session[f"/api/ctest_auth_{ctest_id}"] = True
        return RedirectResponse(f"/api/ctest/{ctest_id}", status_code=302)
    else:
        return templates.TemplateResponse(
            "ctest-auth.html",
            {"request": request, "ctest_id": ctest_id, "error": "Ungültiger Code"},
            status_code=400,
        )


@form_router.get("/ctest/{ctest_id}", response_class=HTMLResponse)
async def get_ctest_form(request: Request, ctest_id: str, db: Session = Depends(get_db)):
    """
    Serve the C-Test form after validation checks.
    
    Args:
        request (Request): FastAPI request object
        ctest_id (str): Unique test identifier from URL
        db (Session): Active database session
        
    Returns:
        TemplateResponse: One of:
            - ctest-form.html with test data (200)
            - not-found.html for invalid/expired tests (410)
        RedirectResponse: To auth page if unauthorized (302)
        
    Template Context (ctest-form.html):
        ctest_text: Original text with gaps for student completion
        correct_answers: Dictionary of correct solutions
        ctest_id: Test identifier for form submission
        
    Raises:
        HTTPException: 500 for server/database errors
    """
    try:
        if not request.session.get(f"/api/ctest_auth_{ctest_id}"):
            return RedirectResponse(f"/api/student_authorize/{ctest_id}", status_code=302)
        test = db.query(CTest).filter(CTest.ctest_id == ctest_id).first()
        if not test or test.expires_at < datetime.now(timezone.utc):
            return templates.TemplateResponse(
                "not-found.html",
                {"request": request},
                status_code=410
            )
        return templates.TemplateResponse(
            "ctest-form.html",
            {
                "request": request,
                "ctest_text": test.ctest_text,
                "correct_answers": test.correct_answers,
                "ctest_id": str(test.ctest_id)
            }
        )

    except Exception as e:
       
        raise HTTPException(
            status_code=500,
            detail="Test rendering service error: " + str(e)
        )