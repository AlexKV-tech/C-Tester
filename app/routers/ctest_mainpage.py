from app.dependencies import templates

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse



mainpage_router = APIRouter()


@mainpage_router.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    """
    Serves the application's main entry point.

    Args:
        request (Request): Incoming FastAPI request object

    Returns:
        TemplateResponse: Rendered HTML template for the main interface

    Notes:
        - Uses Jinja2 template located at frontend/templates/ctest-mainpage.html
        - Automatically injects request context into template
    """
    return templates.TemplateResponse("ctest-mainpage.html", {"request": request})