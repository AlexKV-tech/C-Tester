from fpdf import FPDF
from fpdf import XPos, YPos
from ctest_gen import BLANK_SYMBOL


def format_blanks(text: str):
    """
    Formats the text(text:str) by ensuring that each blank symbol is followed by a space.
    """
    return text.replace(BLANK_SYMBOL, BLANK_SYMBOL + " ")

def generate_pdf_ctest(ctest_text: str, orig_text: str, path: str):
    """
    Generates a PDF file from the provided text(text: str), 
    inserts answers(orig_text: str) at the end of the file 
    and saves it to the specified path(path: str).
    """
    text = format_blanks(ctest_text)
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Times New Roman", fname="static/fonts/Tinos-Regular.ttf")
    pdf.add_font("Times New Roman", "B", fname="static/fonts/Tinos-Bold.ttf")
    pdf.set_font("Times New Roman", size=12)
    pdf.write(text=text)
    pdf.add_page()
    pdf.set_font("Times New Roman", "B", size=12)
    pdf.cell(text="Lösungen", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Times New Roman", size=12)
    pdf.write(text=orig_text)
    pdf.output(path)

