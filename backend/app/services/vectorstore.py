
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
import os
import shutil

DB_PATH = "backend/faiss_index"
embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def create_new_db():
    db = FAISS.from_texts(["init"], embedding)
    db.save_local(DB_PATH)
    return db

# Initialize vector DB
if os.path.exists(DB_PATH):
    try:
        db = FAISS.load_local(DB_PATH, embedding, allow_dangerous_deserialization=True)
    except Exception as e:
        print(f"[WARNING] Failed to load FAISS index. Recreating... Reason: {e}")
        shutil.rmtree(DB_PATH, ignore_errors=True)
        db = create_new_db()
else:
    db = create_new_db()

def store_chunks(chunks):
    texts = [c["text"] for c in chunks]
    meta = [{"doc_id": c["doc_id"], "page": c["page"]} for c in chunks]
    db.add_texts(texts, meta)
    db.save_local(DB_PATH)

def query_chunks(query):
    return db.similarity_search(query, k=5)

def delete_chunks():
    """Deletes all vector store chunks and resets index"""
    global db
    shutil.rmtree(DB_PATH, ignore_errors=True)
    db = create_new_db()
