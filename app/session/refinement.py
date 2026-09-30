from app.intelligence.controller import is_presentation_only


def is_late_constraint(query, state):
    if not state.current_answer or not state.current_query:
        return False
    if is_presentation_only(query):
        return False

    q = query.lower().strip()
    markers = [
        "international", "domestic", "business trip", "personal trip",
        "employee", "manager", "urgent", "economy", "premium", "overnight",
        "only", "specifically", "except", "excluding", "for managers", "for employees"
    ]
    return any(m in q for m in markers) and len(q.split()) <= 15


def build_refinement_query(query, state):
    """Combine the original intent with the late constraint so retrieval targets the delta."""
    original = state.current_query.strip()
    constraint = query.strip()
    if not original:
        return constraint
    return f"{original} {constraint}"
