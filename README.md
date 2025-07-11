# 🧠 Scalable RAG-Based Document Research & Theme Identification Chatbot
RAGStack is an AI-powered platform designed to process, index, and analyze large volumes of documents using Retrieval-Augmented Generation (RAG). It enables intelligent document upload, OCR-based text extraction, semantic chunking, vector embedding, and natural language querying — all powered by cutting-edge LLMs (Groq LLM).

Ideal for legal research, academic summarization, enterprise document analysis, and knowledge discovery.

---

##  Features

-  Upload and process 75+ PDF documents with automatic OCR (PyMuPDF / pdfplumber).
-  Chunk, embed, and store documents using vector databases (ChromaDB / FAISS).
-  Ask natural language questions and get answers grounded in document content.
-  Cross-document semantic search using OpenAI/Groq embeddings.
-  Citations returned with `doc_id` and page numbers (e.g., `[doc_1 - Page 4]`).
-  Track uploaded documents and delete specific ones.
-  Fully asynchronous FastAPI backend with modular services.
-  Theme identification and document context summarization (LLM-based).
-  Clean UI (optional React/HTML frontend) with real-time querying.

---

## 📂 Project Structure
```bash
├── backend/
│   ├── main.py
│   ├── app/
│   │   ├── core/
│   │   │   ├── ocr.py
│   │   │   └── chunking.py
│   │   └── services/
│   │       ├── vectorstore.py
│   │       └── groq_llm.py
│   └── data/  ← stores uploaded PDFs
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── static/
│       ├── styles.css
├── requirements.txt
└── README.md
```

---

## 🧠 How It Works

1. **Document Upload**  
   → PDFs are parsed and chunked into small segments.  
   → Each chunk is embedded using an LLM (Groq/OpenAI).  

2. **Storage**  
   → Chunks + metadata are stored in a vector database.

3. **Querying**  
   → User inputs a natural question.  
   → Relevant chunks are retrieved semantically.  
   → Prompt sent to the LLM with context for an answer.  
   → Response includes references like `[doc_id - Page X]`.

---

## ⚙️ Tech Stack

| Layer      | Tool/Library                  |
|------------|-------------------------------|
| Backend    | Python, FastAPI, Uvicorn      |
| Embeddings | Groq AI / OpenAI Embeddings   |
| Vector DB  | ChromaDB / FAISS              |
| OCR/PDF    | PyMuPDF / pdfplumber          |
| LLM Prompt | Groq (Mixtral, LLaMA3, etc.)  |
| Frontend   | HTML/CSS/JS or React (Optional) |

---

## ✅ Setup Instructions

1. **Clone the Repo**
```bash
git clone https://github.com/himanshupardhi14/RAGStack.git
cd RAGStack/backend
```
2. **Create a '.env' file in the backend folder and add your API key:**
```bash
GROQ_API_KEY=your_groq_api_key_here
```
3. **Install Dependencies**
```bash
pip install -r requirements.txt
```
4. **Run the FastAPI Server**
```bash
uvicorn app.main:app --reload
```
5. **Open the API Docs**
```bash
Navigate to: http://127.0.0.1:8000/docs
```
---

## 📈 Demo / Use Case
Upload multiple research papers, internal reports, or legal documents — then ask:

:-"What are the key themes in Q2 reports?"

:-"Did any document mention GDPR compliance?"

:-"Summarize marketing insights from uploaded PDFs."

---
## Sample Query Flow
```bash
POST /query
Content-Type: application/x-www-form-urlencoded
question=What insights are mentioned in document_3?

Response:
{
  "answer": "Document_3 mentions customer growth insights on [doc_3 - Page 2]."
}
```
---
##  Future Enhancements

 :Frontend UI for seamless upload + querying

 :User authentication & file persistence

 :Summary + theme extraction for dashboards

 :RAG pipelines using LangChain

---
