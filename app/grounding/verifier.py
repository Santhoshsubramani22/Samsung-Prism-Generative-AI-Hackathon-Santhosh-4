import re


STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "to", "of", "and", "or",
    "in", "on", "for", "with", "this", "that", "it", "be", "as", "at", "by"
}

def _tokens(text):
    return {t for t in re.findall(r"[A-Za-z0-9][A-Za-z0-9._-]*", (text or "").lower()) if t not in STOPWORDS}


def verify_answer(answer, evidence):
    """Validate citations and basic claim/evidence overlap.

    If the model omitted a citation, add one only when the answer has measurable
    lexical support in an evidence chunk. If it has no support, replace it with
    a deterministic extractive answer rather than attaching a misleading citation.
    """
    if not evidence:
        return {"answer": answer, "citations": [], "grounded": False, "support_score": 0.0}

    valid_ids = {e["chunk"]["chunk_id"]: e["chunk"] for e in evidence}
    cited_ids = []
    for cid in valid_ids:
        if cid in (answer or ""):
            cited_ids.append(cid)

    factual_text = re.sub(r"\[[^\]]+\]", "", answer or "").strip()
    answer_tokens = _tokens(factual_text)
    best_chunk = None
    best_score = 0.0
    for e in evidence:
        c = e["chunk"]
        overlap = len(answer_tokens & _tokens(c.get("chunk_text", "")))
        score = overlap / max(1, len(answer_tokens))
        if score > best_score:
            best_score = score
            best_chunk = c

    # An explicit valid citation is a direct provenance signal from the model.
    if cited_ids:
        citations = [
            f"{valid_ids[cid]['document_id']} | {valid_ids[cid].get('section') or 'Section N/A'} | {cid}"
            for cid in cited_ids
        ]
        return {"answer": answer, "citations": citations, "grounded": True, "support_score": round(best_score, 3)}

    # No citation: attach only if evidence actually supports the answer.
    if best_chunk is not None and best_score >= 0.15:
        cid = best_chunk["chunk_id"]
        clean = re.sub(r"\[[^\]]+\]", "", answer or "").strip().rstrip(".")
        grounded = f"{clean}. [{best_chunk['document_id']} | {cid}]"
        return {
            "answer": grounded,
            "citations": [f"{best_chunk['document_id']} | {best_chunk.get('section') or 'Section N/A'} | {cid}"],
            "grounded": True,
            "support_score": round(best_score, 3),
        }

    # Do not attach an arbitrary citation to unsupported text.
    return {
        "answer": "I couldn't verify that answer against the provided document.",
        "citations": [],
        "grounded": False,
        "support_score": round(best_score, 3),
    }
