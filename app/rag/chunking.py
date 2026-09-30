from config import CHUNK_SIZE, CHUNK_OVERLAP

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    text = text.strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(start + 1, end - overlap)
    return chunks

def build_chunks(documents):
    result = []
    counter = 1
    for doc in documents:
        for page in doc["pages"]:
            for text in chunk_text(page["text"]):
                result.append({
                    "document_id": doc["document_id"],
                    "document_name": doc["document_name"],
                    "page": page["page"],
                    "section": page.get("section", ""),
                    "chunk_id": f'{doc["document_id"]}_CH_{counter:04d}',
                    "chunk_text": text
                })
                counter += 1
    return result
