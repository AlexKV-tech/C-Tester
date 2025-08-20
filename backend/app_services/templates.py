from fastapi.templating import Jinja2Templates
import os

"""
Jinja2 template configuration for FastAPI application.

Initializes and configures template engine for:
- HTML response rendering
- Dynamic content injection
- Template inheritance
""" 

# Template engine instance configured to look in 'frontend/templates' directory
templates = Jinja2Templates(directory=os.path.join(os.getcwd(), "frontend", "templates"))