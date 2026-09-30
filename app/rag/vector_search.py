from pathlib import Path
import json
import faiss
from .embeddings import embed_texts
from config import TOP_K

INDEX_DIR = Path("indexes/faiss_index")
INDEX_FILE = INDEX_DIR / "index.faiss"
META_FILE = INDEX_DIR / "metadata.json"

def build_faiss(chunks):
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    if not chunks:
        raise ValueError("No chunks were created from the corpus.")
    vectors = embed_texts([c["chunk_text"] for c in chunks])
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    faiss.write_index(index, str(INDEX_FILE))
    META_FILE.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")

def search_faiss(query, top_k=TOP_K):
    if not INDEX_FILE.exists() or not META_FILE.exists():
        return []
    index = faiss.read_index(str(INDEX_FILE))
    chunks = json.loads(META_FILE.read_text(encoding="utf-8"))
    q = embed_texts([query])
    scores, ids = index.search(q, min(top_k, len(chunks)))
    return [
        {"chunk": chunks[i], "score": float(score), "rank": rank + 1}
        for rank, (i, score) in enumerate(zip(ids[0], scores[0]))
        if i >= 0
    ]
