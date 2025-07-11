
from fastapi import FastAPI, UploadFile, Form, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

import os
import json
from datetime import datetime
from typing import List, Optional

from app.core.ocr import extract_text_from_file
from app.core.chunking import chunk_text
from app.services.vectorstore import store_chunks, query_chunks, delete_chunks
from app.services.groq_llm import ask_groq

# Feedback Model
class FeedbackRequest(BaseModel):
    doc_id: str
    helpful: bool
    comments: Optional[str] = None

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, "..", "..", "backend", "data")
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "..", "frontend")
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")
INDEX_PATH = os.path.join(FRONTEND_DIR, "index.html")

os.makedirs(UPLOAD_DIR, exist_ok=True)

if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def read_root():
    if os.path.exists(INDEX_PATH):
        return FileResponse(INDEX_PATH, media_type="text/html")
    return {"message": "Frontend not found. FastAPI is running."}

# Process file
def process_file(file_path: str, filename: str):
    try:
        pages = extract_text_from_file(file_path)
        chunks = chunk_text(filename, pages)
        store_chunks(chunks)
    except ValueError as e:
        print(f"[ERROR] Skipped {filename}: {e}")

# Upload documents
@app.post("/upload")
async def upload_files(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    allowed_exts = [".pdf", ".docx", ".txt"]

    for file in files:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in allowed_exts:
            raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are allowed.")

        save_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(save_path, "wb") as f:
            f.write(await file.read())
        background_tasks.add_task(process_file, save_path, file.filename)

    return {"msg": f"{len(files)} files received and processing started in background."}

# Query documents
@app.post("/query")
async def query(question: str = Form(...), role: str = Form("default")):
    docs = query_chunks(question)

    filtered_docs = [
        d for d in docs if "doc_id" in d.metadata and "page" in d.metadata
    ]

    if not filtered_docs:
        return {"answer": "No documents found in the system. Please upload documents first."}

    context = "\n\n".join(
        [f"[{d.metadata.get('doc_id')} - Page {d.metadata.get('page')}] {d.page_content}" for d in filtered_docs]
    )

    answer = ask_groq(question=question, context=context, role=role)
    return {
        "answer": answer,
        "source_refs": [f"{d.metadata.get('doc_id')} - Page {d.metadata.get('page')}" for d in filtered_docs]
    }

# Submit feedback
@app.post("/feedback")
async def feedback_user(feedback: FeedbackRequest):
    feedback_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "doc_id": feedback.doc_id,
        "helpful": feedback.helpful,
        "comments": feedback.comments
    }

    feedback_file = os.path.join(UPLOAD_DIR, "feedback_log.json")
    with open(feedback_file, "a") as f:
        f.write(json.dumps(feedback_data) + "\n")

    return {"message": "Feedback recorded. Thank you!"}

# GET feedback route (this was missing)
@app.get("/feedback")
def get_feedback():
    feedback_file = os.path.join(UPLOAD_DIR, "feedback_log.json")
    if not os.path.exists(feedback_file):
        return {"feedback": []}

    feedback_list = []
    with open(feedback_file, "r") as f:
        for line in f:
            try:
                feedback_list.append(json.loads(line))
            except:
                continue
    return {"feedback": feedback_list}

# List documents
@app.get("/documents")
def list_documents():
    files = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
    return {"documents": files}

# Delete document
@app.delete("/documents/{filename}")
def delete_document(filename: str):
    path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    os.remove(path)

    remaining = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
    if len(remaining) == 0:
        delete_chunks()

    return {"msg": f"{filename} deleted successfully from disk and vector store."}
