from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from fastapi.templating import Jinja2Templates
import os

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Template engine instance configured to look in 'frontend/templates' directory
templates = Jinja2Templates(directory=os.path.join(os.getcwd(), "frontend", "templates"))