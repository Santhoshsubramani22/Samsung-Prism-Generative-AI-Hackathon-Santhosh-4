from config import RRF_K

def reciprocal_rank_fusion(result_lists, k=RRF_K):
    fused = {}
    for results in result_lists:
        for item in results:
            cid = item["chunk"]["chunk_id"]
            fused.setdefault(cid, {"chunk": item["chunk"], "rrf_score": 0.0})
            fused[cid]["rrf_score"] += 1.0 / (k + item["rank"])
    return sorted(fused.values(), key=lambda x: x["rrf_score"], reverse=True)
