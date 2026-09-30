import re

def decompose(query):
    parts = re.split(r"\s*(?:,|;|\band\b|\balso\b)\s*", query, flags=re.I)
    parts = [p.strip(" .?") for p in parts if p.strip(" .?")]

    if len(parts) <= 1:
        return {
            "is_multi_intent": False,
            "sub_queries": [{
                "id": "intent_1",
                "query": query.strip(),
                "intent": "general"
            }]
        }

    sub = []
    for i, part in enumerate(parts, 1):
        intent = infer_intent(part)
        sub.append({
            "id": f"intent_{i}",
            "query": part,
            "intent": intent
        })
    return {"is_multi_intent": True, "sub_queries": sub}

def infer_intent(text):
    q = text.lower()
    if "document" in q or "required" in q:
        return "requirements"
    if "limit" in q or "amount" in q or "maximum" in q:
        return "limit"
    if "international" in q:
        return "international_policy"
    if "cancellation" in q:
        return "cancellation"
    if "catering" in q:
        return "catering"
    if "capacity" in q:
        return "capacity"
    return "general"
