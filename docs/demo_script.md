# 5-Minute Demo Script

## 0:00–0:40 — Problem
Explain why traditional RAG waits for the complete query and can repeat retrieval when constraints arrive later.

## 0:40–1:20 — Early retrieval
Type the streaming transcript:
“I need” → “I need information about” → “I need information about reimbursement” → “...for international travel”.
Show WAIT on incomplete input and RETRIEVE when intent stabilizes.

## 1:20–2:10 — Multi-intent
Use:
“What is the reimbursement limit, what documents are required, and what is the policy for international travel?”
Show multiple detected intents and hybrid retrieval.

## 2:10–3:00 — Late constraint
Ask:
“What is the reimbursement policy?”
Then:
“The trip was international.”
Show Answer v1 → targeted retrieval → Answer v2.

## 3:00–3:35 — Suppression
Say:
“Make the answer shorter.”
Show SUPPRESS and no retrieval.

## 3:35–4:20 — Grounding
Show citations with document/chunk IDs and explain that evidence comes only from the local corpus.

## 4:20–5:00 — Telemetry
Open the dashboard and show session events, answer versions, citations and evidence.
