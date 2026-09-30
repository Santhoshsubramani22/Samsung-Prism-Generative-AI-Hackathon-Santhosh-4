from app.intelligence.decomposer import decompose

def test_multi_intent():
    r=decompose("What is the reimbursement limit, what documents are required, and what is the policy for international travel?")
    assert r["is_multi_intent"] is True
    assert len(r["sub_queries"]) >= 2
