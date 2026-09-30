from app.grounding.verifier import verify_answer

def test_grounding():
    evidence=[{"chunk":{"document_id":"DOC_001","section":"Travel","chunk_id":"DOC_001_CH_0001","page":1,"chunk_text":"test"},"rrf_score":1}]
    r=verify_answer("Fact [DOC_001_CH_0001]", evidence)
    assert "DOC_001_CH_0001" in r["citations"][0]


def test_grounding_does_not_attach_arbitrary_citation():
    evidence = [{
        "chunk": {
            "document_id": "DOC_001",
            "section": "Travel",
            "chunk_id": "DOC_001_CH_0001",
            "page": 1,
            "chunk_text": "The domestic travel limit is 5000 INR."
        },
        "rrf_score": 1,
    }]
    r = verify_answer("The moon is made of cheese.", evidence)
    assert r["grounded"] is False
    assert r["citations"] == []
