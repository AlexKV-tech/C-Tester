from fpdf import FPDF
from ctest_gen import BLANK_SYMBOL, generate_ctest


def format_blanks(text: str):
    return text.replace(BLANK_SYMBOL, BLANK_SYMBOL + " ")

def generate_pdf_ctest(text: str, path: str):
    text = format_blanks(text)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Times New Roman", fname="static/fonts/Tinos-Regular.ttf")
    pdf.set_font("Times New Roman", size=12)
    pdf.write(text=text)
    pdf.output(path)

