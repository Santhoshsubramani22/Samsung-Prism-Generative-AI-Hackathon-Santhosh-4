import re


def rerank(query, evidence):
    q = set(re.findall(r"\w+", query.lower()))
    scored = []
    for item in evidence:
        text = item["chunk"]["chunk_text"].lower()
        words = set(re.findall(r"\w+", text))
        overlap = len(q & words)
        exact_phrases = 0
        for term in re.findall(r"[A-Za-z0-9][A-Za-z0-9._-]+", query.lower()):
            if len(term) >= 4 and term in text:
                exact_phrases += 1
        score = overlap + exact_phrases * 2 + item.get("rrf_score", 0)
        copy = dict(item)
        copy["rerank_score"] = score
        scored.append(copy)
    scored.sort(key=lambda x: x["rerank_score"], reverse=True)
    return scored
