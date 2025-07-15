from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from templates import templates
from database import get_db
from sqlalchemy.orm import Session
import models



form_router = APIRouter()
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