import pdfplumber

def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        return [
            {"page": i+1, "text": page.extract_text() or ""}
            for i, page in enumerate(pdf.pages)
        ]