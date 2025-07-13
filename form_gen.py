from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from templates import templates
from database import TEST_DB


form_router = APIRouter()
@form_router.get("/test/{test_id}", response_class=HTMLResponse)
async def get_ctest_form(request: Request, test_id: str):
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

    Notes:
        - `TEST_DB` is a placeholder for database logic.
        - Blanks metadata is 1-indexed for frontend JavaScript compatibility.
    """
    try:
        # Retrieve test data from mock database (replace with real DB query in production)
        test = TEST_DB.get(test_id)

        
        if not test or test["expires_at"] < datetime.now(timezone.utc):
            return templates.TemplateResponse(
                "expired.html",
                {"request": request},
                status_code=410
            )

        # Prepare blank metadata: maps blank IDs to their lengths for JavaScript rendering
        blanks_metadata: dict[str, str] = {
            blank_id: blanks_info["length"] for blank_id, blanks_info in zip(test["answers"].keys(), test["answers"].values())
            }

       
        return templates.TemplateResponse(
            "ctest_form.html",
            {
                "request": request,
                "test_id": test_id,
                "ctest_text": test["ctest_text"],
                "blanks": blanks_metadata,
            }
        )

    except Exception as e:
       
        raise HTTPException(
            status_code=500,
            detail="Test rendering service unavailable " + str(e)
        )