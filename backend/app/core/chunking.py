from langchain.text_splitter import RecursiveCharacterTextSplitter


def chunk_text(doc_id: str, pages: list):
    chunks = []

    for i, page in enumerate(pages):
        # Handle both dict and string cases
        if isinstance(page, dict):
            page_text = page.get("text", "").strip()
        elif isinstance(page, str):
            page_text = page.strip()
        else:
            continue  # skip unknown format

        if not page_text:
            continue

        chunk = {
            "doc_id": doc_id,
            "page": i + 1,
            "text": page_text,
        }
        chunks.append(chunk)

    return chunks
