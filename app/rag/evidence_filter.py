import re

STOPWORDS = {
    "who", "what", "where", "when", "why", "how", "is", "are", "was", "were",
    "the", "a", "an", "of", "to", "in", "on", "for", "and", "or", "does", "do",
    "did", "this", "that", "these", "those", "document", "pdf", "please", "tell",
    "me", "about", "can", "you", "give", "explain", "information"
}


def tokens(text):
    return [x for x in re.findall(r"[A-Za-z0-9][A-Za-z0-9._-]*", text.lower()) if x not in STOPWORDS]


def filter_evidence(query, evidence, max_items=3):
    q_tokens = set(tokens(query))
    if not evidence:
        return []

    scored = []
    for item in evidence:
        text = item["chunk"]["chunk_text"]
        t_tokens = set(tokens(text))
        overlap = len(q_tokens & t_tokens)
        phrase = 0
        normalized_q = " ".join(tokens(query))
        normalized_t = " ".join(tokens(text))
        if normalized_q and normalized_q in normalized_t:
            phrase = 3
        lexical = overlap / max(1, len(q_tokens))
        score = (phrase * 2.0) + lexical + float(item.get("rerank_score", item.get("rrf_score", 0)))
        copy = dict(item)
        copy["relevance_score"] = score
        scored.append(copy)

    scored.sort(key=lambda x: x["relevance_score"], reverse=True)

    # For fact/name lookups, require at least one meaningful query token match.
    if q_tokens:
        meaningful = [x for x in scored if len(q_tokens & set(tokens(x["chunk"]["chunk_text"]))) > 0]
        if meaningful:
            scored = meaningful
        else:
            return []

    return scored[:max_items]
