# Streaming Live RAG — State-Preserving Answer Refinement

A Flask-based hybrid RAG prototype designed around the challenge requirements:

- conversational/streaming responses using Server-Sent Events (SSE)
- multi-intent decomposition and per-intent retrieval
- dense FAISS + sparse BM25 retrieval
- Reciprocal Rank Fusion (RRF), reranking and evidence filtering
- state-preserving late-constraint refinement
- grounded citations and provenance checks
- telemetry for retrieval, answer versions and end-to-end latency
- deterministic fallback when Gemini is unavailable

## What was fixed in this version

### 1. Real incremental SSE answer delivery
`/api/stream` now emits separate events for:

```text
controller
retrieval
answer_delta
answer_correction (when grounding changes the answer)
final
[DONE]
```

When `GEMINI_API_KEY` is configured, the application uses Gemini's streaming generation API. Without an API key, the deterministic fallback is still emitted in multiple answer chunks, so the demo remains visibly incremental.

### 2. State-preserving late constraints
For a conversation such as:

```text
User: What is the reimbursement policy?
Assistant: Answer v1
User: The trip was international.
```

the second retrieval query becomes:

```text
What is the reimbursement policy? The trip was international.
```

The previous answer is supplied to the generator so the response can be refined rather than treated as an unrelated new conversation.

### 3. Stronger grounding
The verifier:

- recognizes valid citations from the provided evidence;
- adds a citation only when evidence supports the generated text;
- refuses to attach an arbitrary citation to unsupported content;
- reports `grounded` and `support_score` telemetry.

### 4. Better state handling
Constraints accumulate instead of replacing earlier constraints. Session access is protected by a lock, and presentation-only requests reuse the current answer without triggering retrieval.

## Project structure

```text
app.py
app/
  ai/gemini.py
  grounding/verifier.py
  intelligence/controller.py
  intelligence/decomposer.py
  rag/
    pipeline.py
    vector_search.py
    bm25_search.py
    fusion.py
    reranker.py
    evidence_filter.py
    ingestion.py
    metadata.py
  session/
    state.py
    refinement.py
  telemetry/logger.py
static/js/app.js
templates/
data/documents/
indexes/
benchmark/
tests/
```

## Windows setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Put PDF/TXT/DOCX files in:

```text
data\documents\
```

Build the indexes:

```powershell
py scripts\build_index.py
```

Run tests:

```powershell
pytest -q
```

Expected result in this updated project:

```text
12 passed
```

Run the server:

```powershell
py app.py
```

Open:

```text
http://127.0.0.1:5000/chat
```

## Gemini configuration

Edit `.env`:

```text
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```

The application still works without a key using the deterministic extractive fallback.

## Streaming API example

POST JSON to `/api/stream`:

```json
{"query":"What is the reimbursement policy?"}
```

The response is SSE. A normal successful trace looks conceptually like:

```text
controller → RETRIEVE
retrieval → evidence IDs + metrics
answer_delta → "The reimbursement..."
answer_delta → "...policy..."
answer_delta → "..."
final → answer + citations + answer version + grounding + latency
[DONE]
```

## State-preserving refinement demo

First:

```text
What is the reimbursement policy?
```

Then:

```text
The trip was international.
```

The UI should show:

```text
Answer v1
    ↓
late constraint detected
    ↓
targeted retrieval using original intent + new constraint
    ↓
Answer v2
```

## Required challenge demo cases

### 1. Single intent

```text
What is the reimbursement policy?
```

### 2. Multi-intent

```text
What is the reimbursement limit, what documents are required, and what is the policy for international travel?
```

Expected: multiple decomposed intents with separate retrieval queries.

### 3. Late constraint

```text
What is the reimbursement policy?
```
then:
```text
The trip was international.
```

Expected: targeted refinement, not a completely unrelated restart.

### 4. Presentation-only refinement

```text
Make the answer shorter.
```

Expected: `SUPPRESS` and reuse the current answer without another retrieval operation.

### 5. Unsupported fact

Ask for a fact that is absent from the supplied corpus.

Expected: no invented answer and no arbitrary citation.

## Evaluation

The included benchmark remains a controller/decomposition smoke benchmark. For a competition submission, additionally record retrieval precision/recall, groundedness, citation accuracy, latency, and a dense-only vs hybrid comparison over a labelled query set.

Run the smoke benchmark with:

```powershell
py benchmark\run_benchmark.py
```

## Docker

The Compose file uses `.env.example` by default so a clean checkout does not fail because `.env` is missing.

```powershell
docker compose up --build
```

Then open:

```text
http://127.0.0.1:5000/chat
```
