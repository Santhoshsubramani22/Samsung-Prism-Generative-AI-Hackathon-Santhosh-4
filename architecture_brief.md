# Architecture Brief

## Objective
Demonstrate incremental retrieval rather than waiting for the complete user utterance.

## Core pipeline
Incoming stream → Controller → Intent Decomposer → FAISS/BM25 → RRF → Reranker → Session Synthesis → Grounding → Stream → Telemetry.

## Controller
- WAIT: intent incomplete.
- RETRIEVE: stable enough to search.
- SUPPRESS: presentation-only request with an existing answer.

## Hybrid retrieval
FAISS captures semantic similarity. BM25 captures lexical matches and exact policy terms. RRF combines rankings without requiring the two systems to share score scales.

## Session refinement
A late constraint is detected against an existing session. Targeted retrieval is performed and the answer version increments without clearing session state.

## Grounding
Every generated response is checked against retrieved chunk IDs. Unknown citations are not accepted as valid evidence.

## Telemetry
Retrieval, answer version, latency, subqueries, citations and refinement state are logged.

## Evaluation
Run `benchmark/run_benchmark.py` and the test suite. Report measured values only; the specification's G1–G6 thresholds are targets.
