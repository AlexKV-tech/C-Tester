from fastapi.responses import HTMLResponse
import pdf_gen
import test_gen
import submissions
import form_gen
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from templates import templates


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(pdf_gen.generator_router)
app.include_router(test_gen.generator_router)
app.include_router(submissions.submission_router)
app.include_router(form_gen.form_router)

@app.get("/", response_class=HTMLResponse)
def serve_home(request: Request):
    """ 
    Serve user to main page - generator of C-Tests
    """
    return templates.TemplateResponse("index.html", {"request": request})


    



