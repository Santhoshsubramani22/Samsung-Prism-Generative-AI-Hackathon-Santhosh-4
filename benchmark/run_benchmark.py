import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.intelligence.controller import decide
from app.intelligence.decomposer import decompose
from app.session.state import SessionState

queries = [
    "I need information about",
    "I need information about reimbursement",
    "What is the reimbursement limit, what documents are required, and what is the policy for international travel?",
    "Make the answer shorter."
]

state = SessionState()
rows = []

for q in queries:
    decision = decide(q, state)
    dec = decompose(q)
    rows.append({
        "query": q,
        "controller": decision,
        "is_multi_intent": dec["is_multi_intent"],
        "intent_count": len(dec["sub_queries"])
    })

results = {
    "note": "Controller/decomposition smoke benchmark. This is not a Samsung gate result.",
    "queries": rows
}

Path("benchmark").mkdir(exist_ok=True)
Path("benchmark/results.json").write_text(
    json.dumps(results, indent=2),
    encoding="utf-8"
)
print(json.dumps(results, indent=2))
