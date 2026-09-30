from pathlib import Path
from pypdf import PdfReader
from docx import Document

SUPPORTED = {".pdf", ".txt", ".docx"}


def clean_text(text):
    return " ".join((text or "").replace("\x00", " ").split())


def extract_pdf(path):
    reader = PdfReader(str(path))
    pages = []
    for n, page in enumerate(reader.pages, 1):
        pages.append({
            "page": n,
            "section": "",
            "text": clean_text(page.extract_text() or "")
        })
    return pages, len(reader.pages)


def extract_txt(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    return [{"page": 1, "section": "", "text": clean_text(text)}], 1


def extract_docx(path):
    doc = Document(str(path))
    text = "\n".join(p.text for p in doc.paragraphs)
    return [{"page": 1, "section": "", "text": clean_text(text)}], 1


def ingest_document(path):
    path = Path(path)
    ext = path.suffix.lower()
    if ext == ".pdf":
        pages, page_count = extract_pdf(path)
    elif ext == ".txt":
        pages, page_count = extract_txt(path)
    elif ext == ".docx":
        pages, page_count = extract_docx(path)
    else:
        raise ValueError(f"Unsupported type: {ext}")

    return {
        "document_id": path.stem.upper().replace(" ", "_"),
        "document_name": path.name,
        "file_type": ext.lstrip("."),
        "total_pages": page_count,
        "pages": pages,
    }


def ingest_directory(directory):
    directory = Path(directory)
    if not directory.exists():
        return []
    return [
        ingest_document(p)
        for p in sorted(directory.iterdir())
        if p.is_file() and p.suffix.lower() in SUPPORTED
    ]
