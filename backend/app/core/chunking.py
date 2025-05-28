from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_text(doc_id, pages):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = []

    for page in pages:
        page_text = page.get("text", "").strip()
        page_number = page.get("page", None)

        # Skip empty or missing content
        if not page_text:
            continue

        split_chunks = splitter.split_text(page_text)
        for chunk in split_chunks:
            if chunk.strip():  # Avoid empty chunks
                chunks.append({
                    "doc_id": doc_id,
                    "page": page_number,
                    "text": chunk.strip()
                })

    return chunks
