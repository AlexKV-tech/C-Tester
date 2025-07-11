from datetime import datetime
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from templates import templates
from database import TEST_DB


form_router = APIRouter()
@form_router.get("/test/{test_id}", response_class=HTMLResponse)
async def get_ctest_form(request: Request, test_id: str):
    """
    Accepts test_id: str -- id of the test
    Returns either page noting expiration of 
    the test(failure) or page rendered corresponding to the test_id(success)("blanks" helps rendering blanks in JS part)
    """
    # Fetch the test data(including answers, original text, etc.) related to the test id from the DB - will be replaced by real DB when deploying
    test = TEST_DB.get(test_id) 
    if not test or test["expires_at"] < datetime.utcnow():
        return templates.TemplateResponse("expired.html", {"request": request}, status_code=410)

    return templates.TemplateResponse("ctest_form.html", {
        "request": request,
        "test_id": test_id,
        "ctest_text": test["ctest_text"],
        "blanks": {blank_id: blanks_info[1] for blank_id, blanks_info in zip(test["answers"].keys(), test["answers"].values())}
    })