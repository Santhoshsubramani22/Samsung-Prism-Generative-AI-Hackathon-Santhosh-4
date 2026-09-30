import time
from .vector_search import search_faiss
from .bm25_search import search_bm25
from .fusion import reciprocal_rank_fusion
from .reranker import rerank
from .evidence_filter import filter_evidence
from .metadata import answer_metadata
from app.ai.gemini import synthesize, synthesize_stream
from app.grounding.verifier import verify_answer
from app.telemetry.logger import log_event
from app.session.refinement import build_refinement_query


def retrieve_evidence(query):
    start = time.perf_counter()
    dense = search_faiss(query)
    sparse = search_bm25(query)
    fused = reciprocal_rank_fusion([dense, sparse])
    reranked = rerank(query, fused)
    filtered = filter_evidence(query, reranked, max_items=3)
    latency = round((time.perf_counter() - start) * 1000, 2)
    return filtered, {
        "faiss": len(dense),
        "bm25": len(sparse),
        "rrf": len(fused),
        "reranker": len(reranked),
        "evidence_filter": len(filtered),
        "latency_ms": latency,
    }


def _unique_evidence(items, limit=6):
    unique = {}
    for e in items:
        cid = e["chunk"]["chunk_id"]
        if cid not in unique or e.get("relevance_score", 0) > unique[cid].get("relevance_score", 0):
            unique[cid] = e
    return sorted(unique.values(), key=lambda x: x.get("relevance_score", 0), reverse=True)[:limit]


def prepare_retrieval(query, state, decomposition=None, late_constraint=False):
    intents = (decomposition or {}).get(
        "sub_queries", [{"id": "intent_1", "query": query, "intent": "general"}]
    )
    all_evidence = []
    per_intent = []
    metrics_list = []

    for item in intents:
        retrieval_query = item["query"]
        if late_constraint:
            retrieval_query = build_refinement_query(retrieval_query, state)
        evidence, metrics = retrieve_evidence(retrieval_query)
        all_evidence.extend(evidence)
        metrics_list.append(metrics)
        per_intent.append({
            "id": item["id"],
            "query": item["query"],
            "retrieval_query": retrieval_query,
            "intent": item["intent"],
            "evidence_ids": [e["chunk"]["chunk_id"] for e in evidence],
        })

    evidence = _unique_evidence(all_evidence)
    total_latency = round(sum(m["latency_ms"] for m in metrics_list), 2)
    retrieval = {
        "executed": True,
        "faiss": sum(m["faiss"] for m in metrics_list),
        "bm25": sum(m["bm25"] for m in metrics_list),
        "rrf": sum(m["rrf"] for m in metrics_list),
        "reranker": sum(m["reranker"] for m in metrics_list),
        "evidence_filter": len(evidence),
        "latency_ms": total_latency,
        "intent_count": len(per_intent),
        "refinement": late_constraint,
    }
    return per_intent, evidence, retrieval


def _commit_answer(query, state, answer, citations, evidence, intents, late_constraint, retrieval):
    constraints = [query] if late_constraint else None
    state.update(
        query=query,
        answer=answer,
        citations=citations,
        evidence=evidence,
        intents=intents,
        constraints=constraints,
    )
    event = {
        "event": "answer_version",
        "session_id": state.session_id,
        "query": query,
        "answer_version": state.answer_version,
        "retrieval_latency_ms": retrieval.get("latency_ms", 0),
        "citations": citations,
        "late_constraint": late_constraint,
        "subqueries": [x["query"] for x in intents],
        "evidence_count": len(evidence),
    }
    log_event(event)


def answer_query(query, state, decomposition=None, late_constraint=False):
    intents, evidence, retrieval = prepare_retrieval(query, state, decomposition, late_constraint)
    if not evidence:
        answer = "I couldn't find this information in the provided document."
        citations = []
        grounded = False
        support_score = 0.0
    else:
        answer = synthesize(query, evidence, state.current_answer, late_constraint)
        verified = verify_answer(answer, evidence)
        answer = verified["answer"]
        citations = verified["citations"]
        grounded = verified.get("grounded", False)
        support_score = verified.get("support_score", 0.0)

    _commit_answer(query, state, answer, citations, evidence, intents, late_constraint, retrieval)
    return {
        "answer": answer,
        "citations": citations,
        "intents": intents,
        "retrieval": retrieval,
        "answer_version": state.answer_version,
        "evidence": evidence,
        "grounding": {"grounded": grounded, "support_score": support_score},
    }


def stream_answer_query(query, state, decomposition=None, late_constraint=False):
    """Yield structured events for a real SSE streaming response."""
    started = time.perf_counter()
    intents, evidence, retrieval = prepare_retrieval(query, state, decomposition, late_constraint)

    yield {
        "type": "retrieval",
        "executed": True,
        "intents": intents,
        "metrics": retrieval,
        "evidence_ids": [e["chunk"]["chunk_id"] for e in evidence],
        "refinement": late_constraint,
    }

    if not evidence:
        final_answer = "I couldn't find this information in the provided document."
        citations = []
        grounded = False
        support_score = 0.0
        yield {"type": "answer_delta", "text": final_answer}
    else:
        pieces = []
        for piece in synthesize_stream(query, evidence, state.current_answer, late_constraint):
            pieces.append(piece)
            yield {"type": "answer_delta", "text": piece}

        raw_answer = "".join(pieces).strip()
        verified = verify_answer(raw_answer, evidence)
        final_answer = verified["answer"]
        citations = verified["citations"]
        grounded = verified.get("grounded", False)
        support_score = verified.get("support_score", 0.0)

        # If verification had to replace the model output, stream the corrected final text.
        if final_answer != raw_answer:
            yield {"type": "answer_correction", "text": final_answer}

    _commit_answer(query, state, final_answer, citations, evidence, intents, late_constraint, retrieval)
    total_latency = round((time.perf_counter() - started) * 1000, 2)
    yield {
        "type": "final",
        "answer": final_answer,
        "citations": citations,
        "answer_version": state.answer_version,
        "evidence": evidence,
        "grounding": {"grounded": grounded, "support_score": support_score},
        "latency_ms": total_latency,
        "retrieval": retrieval,
        "refinement": late_constraint,
    }


def answer_metadata_query(query, state):
    result = answer_metadata(query)
    state.update(
        query=query,
        answer=result["answer"],
        citations=result["citations"],
        evidence=[],
        intents=[{"id": "metadata_1", "query": query, "intent": "document_metadata", "evidence_ids": []}],
    )
    log_event({
        "event": "metadata_query",
        "session_id": state.session_id,
        "query": query,
        "answer_version": state.answer_version,
    })
    return {
        "answer": result["answer"],
        "citations": result["citations"],
        "intents": [{"id": "metadata_1", "query": query, "intent": "document_metadata", "evidence_ids": []}],
        "retrieval": {"executed": False, "reason": "document_metadata"},
        "answer_version": state.answer_version,
    }
