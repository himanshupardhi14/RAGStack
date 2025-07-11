
import os
from typing import List
import fitz  # for PDFs
from docx import Document  # for DOCX

def extract_text_from_pdf(file_path: str) -> List[str]:
    text_pages = []
    with fitz.open(file_path) as doc:
        for page in doc:
            text_pages.append(page.get_text())
    return text_pages

def extract_text_from_docx(file_path: str) -> List[str]:
    doc = Document(file_path)
    paragraphs = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    # Chunk paragraphs into groups
    CHUNK_SIZE = 10
    return ['\n'.join(paragraphs[i:i+CHUNK_SIZE]) for i in range(0, len(paragraphs), CHUNK_SIZE)]

def extract_text_from_txt(file_path: str) -> List[str]:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Chunk the content every 1000 characters
    return [content[i:i+1000] for i in range(0, len(content), 1000)]

def extract_text_from_file(file_path: str) -> List[str]:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError("Unsupported file format. Only PDF, DOCX, and TXT are allowed.")
