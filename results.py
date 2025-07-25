from datetime import datetime, timezone
from fastapi import APIRouter, Form, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from templates import templates
from database import get_db
from sqlalchemy.orm import Session
import models



results_router = APIRouter()

@results_router.get("/results_authorize/{test_id}", response_class=HTMLResponse)
async def get_res_auth(request: Request, test_id: str):
    return templates.TemplateResponse("auth.html", {"request": request, "test_id": test_id, "error": None})

@results_router.post("/results_authorize/{test_id}")
async def redirect_res_auth(request: Request, test_id: str, code: str = Form(...), db: Session = Depends(get_db)):
    otp_entry = db.query(models.CTest).filter_by(test_id=test_id).first()
    if otp_entry and otp_entry.teacher_code == code:
        request.session[f"res_auth_{test_id}"] = True
        
        return RedirectResponse(f"/results/{test_id}", status_code=302)
    else:
        return templates.TemplateResponse(
            "auth.html",
            {"request": request, "test_id": test_id, "error": "Ungültiger Code"},
            status_code=400,
        )


@results_router.get("/results/{test_id}", response_class=HTMLResponse)
async def get_results(request: Request, test_id: str, db: Session = Depends(get_db)):
    try:
        if not request.session.get(f"res_auth_{test_id}"):
            
            return RedirectResponse(f"/results_authorize/{test_id}", status_code=302)
        
        submission = db.query(models.Submission).filter(models.Submission.test_id == test_id).first()
        test = db.query(models.CTest).filter(models.CTest.test_id == test_id).first()
        if not submission or not test:
            return templates.TemplateResponse(
                "expired.html",
                {"request": request},
                status_code=410
            )

        
        blanks_metadata: dict[str, str] = {
            blank_id: blanks_info["length"] for blank_id, blanks_info in zip(test.answers.keys(), test.answers.values())
            }
        
        return templates.TemplateResponse(
            "results.html",
            {
                "request": request,
                "score": submission.score,
                "student_answers": submission.user_answers,
                "ctest_text": test.ctest_text,
                "blanks": blanks_metadata,
                "correct_answers": test.answers
            }
        )

    except Exception as e:
       
        raise HTTPException(
            status_code=500,
            detail="Test rendering service error: " + str(e)
        )