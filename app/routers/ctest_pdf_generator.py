from app.schemas.text_input import TextInput
from app.services.ctest_unit_generator_service import create_ctest_unit
from app.services.ctest_pdf_generator_service import create_pdf_test

import os
import tempfile
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, HTMLResponse










"""PDF generation router for creating printable C-Test documents."""



pdf_generator_router = APIRouter()


@pdf_generator_router.post("/create_pdf", response_class=HTMLResponse)
async def get_pdf_reply(input: TextInput, background_tasks: BackgroundTasks):
    """
    Endpoint for generating and serving C-Test PDFs.

    Workflow:
    1. Validates input text
    2. Generates C-Test content
    3. Creates temporary PDF file
    4. Schedules file cleanup
    5. Returns PDF download

    Args:
        input (TextInput): {
            original_text: str,
            difficulty: Optional[int]
        }
        background_tasks (BackgroundTasks): FastAPI background task handler

    Returns:
        FileResponse: PDF download with:
            - filename: printable.pdf
            - application/pdf media type

    Raises:
        HTTPException: 
            - 400 for empty input or validation errors
            - 500 for PDF generation failures

    Security:
        - Uses tempfile for secure temporary file handling
        - Guaranteed file cleanup via background tasks
    """

    try:
        if not input.original_text.strip():
            raise HTTPException(status_code=400, detail="Input text is required.")

        ctest_text, _ = await create_ctest_unit(input.original_text , input.difficulty)

    
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp_file.close()

        await create_pdf_test(ctest_text, input.original_text, tmp_file.name)
        background_tasks.add_task(os.remove, tmp_file.name)

        return FileResponse(tmp_file.name, filename="printable.pdf", media_type="application/pdf")

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create PDF. " + str(e))
