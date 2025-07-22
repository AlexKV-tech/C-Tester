from datetime import datetime, timezone
from fastapi import APIRouter, Form, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from templates import templates
from database import get_db
from sqlalchemy.orm import Session
import models



form_router = APIRouter()

@form_router.get("/authorize/{test_id}", response_class=HTMLResponse)
async def get_test_auth(request: Request, test_id: str):
    return templates.TemplateResponse("form_auth.html", {"request": request, "test_id": test_id, "error": None})

@form_router.post("/authorize/{test_id}")
async def redirect_form_auth(request: Request, test_id: str, code: str = Form(...), db: Session = Depends(get_db)):
    print("HUI")
    otp_entry = db.query(models.CTest).filter_by(test_id=test_id).first()
    if otp_entry and otp_entry.code == code:
        request.session[f"authorized_for_{test_id}"] = True
        return RedirectResponse(f"/test/{test_id}", status_code=302)
    else:
        return templates.TemplateResponse(
            "form_auth.html",
            {"request": request, "test_id": test_id, "error": "Ungültiger Code"},
            status_code=400,
        )


@form_router.get("/test/{test_id}", response_class=HTMLResponse)
async def get_ctest_form(request: Request, test_id: str, db: Session = Depends(get_db)):
    """
    Render the C-Test input form or show an expiration notice.

    This endpoint serves the student-facing C-Test form if the test is valid and not expired.
    Otherwise, it renders an expiration page. In production, test data will be fetched from a
    PostgreSQL database.

    Args:
        request (Request): FastAPI request object.
        test_id (str): Unique test identifier (e.g., 'ct_ab12cd34').

    Returns:
        HTMLResponse:
            - 200 with ctest_form.html if test is active.
            - 410 with expired.html if test is missing or expired.

    Raises:
        HTTPException: 500 if there is a server/database error.
    """
    try:
        if not request.session.get(f"authorized_for_{test_id}"):
            return RedirectResponse(f"/authorize/{test_id}", status_code=302)
        test = db.query(models.CTest).filter(models.CTest.test_id == test_id).first()
        if not test or test.expires_at < datetime.now(timezone.utc):
            return templates.TemplateResponse(
                "expired.html",
                {"request": request},
                status_code=410
            )

        # Prepare blank metadata: maps blank IDs to their lengths for JavaScript rendering
        blanks_metadata: dict[str, str] = {
            blank_id: blanks_info["length"] for blank_id, blanks_info in zip(test.answers.keys(), test.answers.values())
            }

        return templates.TemplateResponse(
            "ctest_form.html",
            {
                "request": request,
                "ctest_text": test.ctest_text,
                "blanks": blanks_metadata,
                "test_id": str(test.test_id)
            }
        )

    except Exception as e:
       
        raise HTTPException(
            status_code=500,
            detail="Test rendering service error: " + str(e)
        )