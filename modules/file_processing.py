from PyPDF2 import PdfReader
import docx

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ''
    return text.strip()

def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    return "\n".join(para.text for para in doc.paragraphs).strip()
