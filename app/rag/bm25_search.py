from pathlib import Path
import pickle
from rank_bm25 import BM25Okapi
from config import TOP_K

INDEX_FILE = Path("indexes/bm25_index.pkl")

def build_bm25(chunks):
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    tokenized = [c["chunk_text"].lower().split() for c in chunks]
    model = BM25Okapi(tokenized)
    with INDEX_FILE.open("wb") as f:
        pickle.dump({"model": model, "chunks": chunks}, f)

def search_bm25(query, top_k=TOP_K):
    if not INDEX_FILE.exists():
        return []
    with INDEX_FILE.open("rb") as f:
        data = pickle.load(f)
    scores = data["model"].get_scores(query.lower().split())
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
    return [
        {"chunk": data["chunks"][i], "score": float(score), "rank": rank + 1}
        for rank, (i, score) in enumerate(ranked)
    ]
