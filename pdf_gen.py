import os
import tempfile
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fpdf import FPDF, XPos, YPos
from test_gen import BLANK_SYMBOL, generate_ctest_unit
from schemas import CTestTextInput

FONT_PATH_REGULAR = "static/fonts/Tinos-Regular.ttf"
FONT_PATH_BOLD = "static/fonts/Tinos-Bold.ttf"

generator_router = APIRouter()


def format_blanks(text: str) -> str:
    """
    Ensure consistent spacing after each blank symbol in the text.

    Args:
        text (str): Input text containing blank symbols.

    Returns:
        str: Text with a space added after every blank symbol.
    """
    return text.replace(BLANK_SYMBOL, f"{BLANK_SYMBOL} ")

def generate_pdf_test(ctest_text: str, orig_text: str, path: str) -> None:
    """
    Generates a PDF document with the C-Test and its answer key.

    The PDF includes:
    - Page 1: C-Test with blanks.
    - Page 2: Original text (answers) labeled as "Lösungen".

    Args:
        ctest_text (str): Text containing blanks for the test.
        orig_text (str): Original unmodified text (used as answer key).
        path (str): File system path where the PDF will be saved.

    Raises:
        IOError: If the file cannot be saved to the given path.
        ValueError: If either input text is empty.
    """
    if not ctest_text.strip() or not orig_text.strip():
        raise ValueError("Input text is not allowed to be empty.")

    formatted_text = format_blanks(ctest_text)

    try:
        pdf = FPDF()
        pdf.add_page()

        pdf.add_font("TimesNewRoman", fname=FONT_PATH_REGULAR)
        pdf.add_font("TimesNewRoman", style="B", fname=FONT_PATH_BOLD)
        pdf.set_font("TimesNewRoman", size=12)
        pdf.write(text=formatted_text)

        pdf.add_page()
        pdf.set_font("TimesNewRoman", style="B", size=12)
        pdf.cell(text="Lösungen", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_font("TimesNewRoman", size=12)
        pdf.write(text=orig_text)

        pdf.output(path)
    except Exception as e:
        raise IOError(f"Failed to generate PDF: {e}")

@generator_router.post("/generate_pdf", response_class=HTMLResponse)
async def get_pdf_reply(input: CTestTextInput, background_tasks: BackgroundTasks):
    """
    Creates a downloadable PDF C-Test from user input.

    This endpoint:
    - Generates a C-Test from the original source text.
    - Writes it to a temporary PDF file.
    - Serves the file to the user.
    - Deletes the temporary file in the background.

    Args:
        input (CTestTextInput): Object containing user-submitted text and optional parameters.
        background_tasks (BackgroundTasks): FastAPI tool for deferred cleanup.

    Returns:
        FileResponse: The downloadable PDF file.

    Raises:
        HTTPException: 400 for invalid input or 500 for generation errors.
    """
    try:
        if not input.text.strip():
            raise HTTPException(status_code=400, detail="Input text is required.")

        ctest_text, _ = generate_ctest_unit(input.text, input.difficulty)

    
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp_file.close()

        generate_pdf_test(ctest_text, input.text, tmp_file.name)
        background_tasks.add_task(os.remove, tmp_file.name)

        return FileResponse(tmp_file.name, filename="printable.pdf", media_type="application/pdf")

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate PDF. " + str(e))
