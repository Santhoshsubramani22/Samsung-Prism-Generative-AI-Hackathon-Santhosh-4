from app.rag.evidence_filter import filter_evidence


def test_filters_unrelated_chunks():
    evidence = [
        {"chunk": {"chunk_id": "A", "chunk_text": "Name: Mayuri M Shine. Batch XXI."}, "rrf_score": 0.1},
        {"chunk": {"chunk_id": "B", "chunk_text": "The activity diagram shows room reservation and checkout."}, "rrf_score": 0.9},
        {"chunk": {"chunk_id": "C", "chunk_text": "Recommended RAM is 8 GB."}, "rrf_score": 0.8},
    ]
    out = filter_evidence("Who is Mayuri?", evidence, max_items=3)
    assert out
    assert out[0]["chunk"]["chunk_id"] == "A"
