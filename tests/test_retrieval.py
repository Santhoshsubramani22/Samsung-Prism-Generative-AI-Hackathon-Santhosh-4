from app.rag.fusion import reciprocal_rank_fusion

def test_rrf():
    chunk={"chunk_id":"A","chunk_text":"hello"}
    result=reciprocal_rank_fusion([
        [{"chunk":chunk,"rank":1,"score":1.0}]
    ])
    assert result[0]["chunk"]["chunk_id"]=="A"
