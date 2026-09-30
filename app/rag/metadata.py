from pathlib import Path
import json

METADATA_FILE = Path("data/processed/documents.json")


def load_documents():
    if not METADATA_FILE.exists():
        return []
    try:
        return json.loads(METADATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def answer_metadata(query):
    docs = load_documents()
    if not docs:
        return {
            "answer": "I couldn't read document metadata. Please rebuild the index first.",
            "citations": [],
            "document_metadata": [],
        }

    q = query.lower()
    pdf_docs = [d for d in docs if d.get("file_type") == "pdf"]
    target_docs = pdf_docs or docs

    if any(x in q for x in ["title", "name", "filename", "file name"]):
        if len(target_docs) == 1:
            d = target_docs[0]
            return {
                "answer": f"The document is named {d['document_name']}.",
                "citations": [f"{d['document_id']} | document metadata"],
                "document_metadata": target_docs,
            }
        names = ", ".join(d["document_name"] for d in target_docs)
        return {
            "answer": f"The available documents are: {names}.",
            "citations": [f"{d['document_id']} | document metadata" for d in target_docs],
            "document_metadata": target_docs,
        }

    if len(target_docs) == 1:
        d = target_docs[0]
        return {
            "answer": f"The PDF contains {d['total_pages']} pages.",
            "citations": [f"{d['document_id']} | document metadata"],
            "document_metadata": target_docs,
        }

    lines = [f"{d['document_name']}: {d['total_pages']} pages" for d in target_docs]
    return {
        "answer": "The available documents contain:\n" + "\n".join(f"- {x}" for x in lines),
        "citations": [f"{d['document_id']} | document metadata" for d in target_docs],
        "document_metadata": target_docs,
    }
