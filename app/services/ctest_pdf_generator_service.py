from app.services.ctest_unit_generator_service import BLANK_SYMBOL

from fpdf import FPDF, XPos, YPos
import os





FONT_PATH_REGULAR = os.path.join(os.getcwd(), "frontend", "fonts", "Tinos-Regular.ttf")
FONT_PATH_BOLD = os.path.join(os.getcwd(), "frontend", "fonts", "Tinos-Bold.ttf")



async def format_blanks(original_text: str) -> str:
    """
    Normalize blank symbol formatting in C-Test text.

    Args:
        original_text (str): The C-Test text containing blank symbols.

    Returns:
        str: Text with consistent spacing after each blank symbol.

    Example:
        >>> format_blanks("This is a_[test]")
        'This is a_ [test]'
    """
    return original_text.replace(BLANK_SYMBOL, f"{BLANK_SYMBOL} ")

async def create_pdf_test(ctest_text: str, original_text: str, path: str) -> None:
    """
    Generate a two-page PDF document containing test and answer key.

    Page 1:
    - Formatted C-Test with blanks for student completion
    - Uses regular font style

    Page 2:
    - Original text labeled "Lösungen" (Solutions)
    - Uses bold header with regular body text

    Args:
        ctest_text (str): Processed text with blank symbols
        original_text (str): Unmodified source text for answer key
        path (str): Absolute filesystem path for PDF output

    Raises:
        ValueError: If either text parameter is empty/whitespace
        IOError: If PDF file cannot be created at specified path

    Notes:
        - Requires Tinos font files in frontend/fonts/ directory
        - Sets consistent 12pt font size throughout
    """
    if not ctest_text.strip() or not original_text.strip():
        raise ValueError("Input text is not allowed to be empty.")

    formatted_text = await format_blanks(ctest_text)

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
        pdf.write(text=original_text)

        pdf.output(path)
    except Exception as e:
        raise IOError(f"Failed to create PDF: {e}")