from app.ai.gemini import _stream_text


def test_fallback_stream_is_incremental():
    parts = list(_stream_text("abcdefghijklmnopqrstuvwxyz", chunk_size=5))
    assert len(parts) > 1
    assert "".join(parts) == "abcdefghijklmnopqrstuvwxyz"
