from fastapi import APIRouter, Form, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from backend.app_services.templates import templates
from backend.database_services.database import get_db
from sqlalchemy.orm import Session
import backend.database_services.models as models

"""FastAPI router for handling C-Test results authorization and display."""


results_router = APIRouter()

@results_router.get("/results_authorize/{ctest_id}", response_class=HTMLResponse)
async def get_res_auth(request: Request, ctest_id: str):
    """
    Display authorization page for viewing test results.

    Args:
        request (Request): FastAPI request object
        ctest_id (str): Unique identifier of the C-Test

    Returns:
        TemplateResponse: Rendered ctest-auth.html template with:
            - request context
            - ctest_id
            - error=None (initial state)
    """
    return templates.TemplateResponse("ctest-auth.html", {"request": request, "ctest_id": ctest_id, "error": None})

@results_router.post("/results_authorize/{ctest_id}")
async def redirect_res_auth(request: Request, ctest_id: str, code: str = Form(...), db: Session = Depends(get_db)):
    """
    Validate teacher code and authorize results access.

    Args:
        request (Request): FastAPI request object
        ctest_id (str): Unique identifier of the C-Test
        code (str): Teacher authorization code from form
        db (Session): SQLAlchemy database session

    Returns:
        RedirectResponse: To results page if code valid (sets session auth)
        TemplateResponse: Re-renders auth page with error if code invalid

    Behavior:
        - Sets session flag on successful authorization
        - Returns 400 status for invalid codes
    """
    otp_entry = db.query(models.CTest).filter_by(ctest_id=ctest_id).first()
    if otp_entry and otp_entry.teacher_code == code:
        request.session[f"/api/res_auth_{ctest_id}"] = True
        return RedirectResponse(f"/api/results/{ctest_id}", status_code=302)
    else:
        return templates.TemplateResponse(
            "ctest-auth.html",
            {"request": request, "ctest_id": ctest_id, "error": "Ungültiger Code"},
            status_code=400,
        )


@results_router.get("/results/{ctest_id}", response_class=HTMLResponse)
async def get_results(request: Request, ctest_id: str, db: Session = Depends(get_db)):
    """
    Display test results after authorization.

    Args:
        request (Request): FastAPI request object
        ctest_id (str): Unique identifier of the C-Test
        db (Session): SQLAlchemy database session

    Returns:
        TemplateResponse: Rendered ctest-results.html with:
            - Score data
            - Student answers
            - Original test text
            - Correct answers
            - Given hints
        RedirectResponse: To auth page if unauthorized
        TemplateResponse: not-found.html if test/submission not found (410)

    Raises:
        HTTPException: 500 for server errors during rendering
    """
    try:
        if not request.session.get(f"/api/res_auth_{ctest_id}"):
            return RedirectResponse(f"/api/results_authorize/{ctest_id}", status_code=302)
        db_submission = db.query(models.Submission).filter(models.Submission.ctest_id == ctest_id).first()
        db_test = db.query(models.CTest).filter(models.CTest.ctest_id == ctest_id).first()
        if not db_submission or not db_test:
            return templates.TemplateResponse(
                "not-found.html",
                {"request": request},
                status_code=410
            )        
        return templates.TemplateResponse(
            "ctest-results.html",
            {
                "request": request,
                "score_data": db_submission.score_data,
                "student_answers": db_submission.student_answers,
                "ctest_text": db_test.ctest_text,
                "correct_answers": db_test.correct_answers,
                "given_hints": db_submission.given_hints,
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Test rendering service error: " + str(e)
        )