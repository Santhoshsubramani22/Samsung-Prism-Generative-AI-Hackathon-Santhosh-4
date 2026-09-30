import re


def is_presentation_only(query):
    q = query.lower().strip()
    patterns = [
        r"^make (it|that|the answer) shorter",
        r"^summari[sz]e (it|that|the previous answer|the answer)",
        r"^convert (it|that) (to|into) bullets",
        r"^explain (it|that|the previous answer) simply",
        r"^make (it|that) simple",
        r"^put (it|that) in bullet points",
    ]
    return any(re.search(p, q) for p in patterns)


def is_metadata_query(query):
    q = query.lower().strip()
    patterns = [
        r"\bhow many pages?\b",
        r"\btotal (number of )?pages?\b",
        r"\bnumber of pages?\b",
        r"\bpage count\b",
        r"\bhow long is (the )?(pdf|document)\b",
        r"\bwhat is the (pdf|document) (title|name|filename)\b",
        r"\bwhat is the filename\b",
        r"\bfile name\b",
    ]
    return any(re.search(p, q) for p in patterns)


def has_stable_intent(query):
    words = query.lower().split()
    if len(words) < 3:
        return False
    weak_endings = {"about", "for", "and", "or", "to", "information", "regarding", "is"}
    return words[-1] not in weak_endings


def decide(query, state):
    if is_presentation_only(query) and state.current_answer:
        return "SUPPRESS"
    if is_metadata_query(query):
        return "METADATA"
    if has_stable_intent(query):
        return "RETRIEVE"
    return "WAIT"
