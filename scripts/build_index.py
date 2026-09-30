from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.rag.ingestion import ingest_directory
from app.rag.chunking import build_chunks
from app.rag.vector_search import build_faiss
from app.rag.bm25_search import build_bm25

DOCS = Path("data/documents")
OUT = Path("data/processed")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    documents = ingest_directory(DOCS)
    chunks = build_chunks(documents)

    if not documents:
        raise SystemExit("No documents found. Add PDF/TXT/DOCX files to data/documents/.")

    (OUT / "chunks.json").write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "metadata.json").write_text(
        json.dumps([{k: c[k] for k in c if k != "chunk_text"} for c in chunks], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUT / "documents.json").write_text(
        json.dumps([
            {
                "document_id": d["document_id"],
                "document_name": d["document_name"],
                "file_type": d["file_type"],
                "total_pages": d["total_pages"],
            }
            for d in documents
        ], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    build_faiss(chunks)
    build_bm25(chunks)

    print(f"Documents indexed: {len(documents)}")
    for d in documents:
        print(f"- {d['document_name']}: {d['total_pages']} pages")
    print(f"Chunks created: {len(chunks)}")
    print("FAISS, BM25 and document metadata created successfully.")


if __name__ == "__main__":
    main()
