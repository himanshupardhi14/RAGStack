
from fastapi import FastAPI, UploadFile, Form, File, BackgroundTasks,HTTPException,status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse,JSONResponse


import os
from typing import List

from app.core.ocr import extract_text_from_pdf
from app.core.chunking import chunk_text
from app.services.vectorstore import store_chunks, query_chunks,delete_chunks
from app.services.groq_llm import ask_groq

app = FastAPI()

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set upload and frontend paths
BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, "..", "..", "backend", "data")
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "..", "frontend")
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")
INDEX_PATH = os.path.join(FRONTEND_DIR, "index.html")

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount static files (JS, CSS, etc.)
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Serve frontend index.html at root
@app.get("/")
def read_root():
    if os.path.exists(INDEX_PATH):
        return FileResponse(INDEX_PATH, media_type="text/html")
    return {"message": "Frontend not found. FastAPI is running."}

# Background task to process a file
def process_file(file_path: str, filename: str):
    pages = extract_text_from_pdf(file_path)
    chunks = chunk_text(filename, pages)
    store_chunks(chunks)

# File upload endpoint for multiple files
@app.post("/upload")
async def upload_files(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    for file in files:
        save_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(save_path, "wb") as f:
            f.write(await file.read())
        background_tasks.add_task(process_file, save_path, file.filename)
    return {"msg": f"{len(files)} files received and processing started in background."}

# Question answering endpoint
@app.post("/query")
async def query(question: str = Form(...)):
    docs = query_chunks(question)

    # Filter out docs missing essential metadata (likely the dummy "init" entry)
    filtered_docs = [
        d for d in docs if "doc_id" in d.metadata and "page" in d.metadata
    ]

    if not filtered_docs:
        return {"answer": "No documents found in the system. Please upload documents first."}

    context = "\n\n".join(
        [f"[{d.metadata.get('doc_id')} - Page {d.metadata.get('page')}] {d.page_content}" for d in filtered_docs]
    )

    prompt = f"""
You are an intelligent document assistant. Use the following retrieved context from user-uploaded documents to answer the question.
context:
{context}

Question:
{question}
Answer concisely, citing document ID and page number like this: [doc_id - page X].
If the answer is not found, respond: "Sorry, I couldn’t find an answer in the documents."
"""
    answer = ask_groq(prompt)
    return {"answer": answer}



# List uploaded documents
@app.get("/documents")
def list_documents():
    files = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
    return {"documents": files}

@app.delete("/documents/{filename}")
def delete_document(filename: str):
    path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    # Remove file
    os.remove(path)

    #  If no documents left, clear vector store
    remaining = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
    if len(remaining) == 0:
        delete_chunks()

    return {"msg": f"{filename} deleted successfully from disk and vector store."}