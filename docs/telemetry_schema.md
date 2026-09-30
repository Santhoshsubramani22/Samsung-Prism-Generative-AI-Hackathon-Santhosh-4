# Telemetry Schema

| Field | Meaning |
|---|---|
| timestamp | Event time |
| session_id | Ephemeral session identifier |
| event | Event type |
| query | Query that triggered the event |
| retrieval_latency_ms | Retrieval elapsed time |
| answer_version | Current answer version |
| citations | Verified evidence references |
| late_constraint | Whether refinement was triggered |
| subqueries | Decomposed search queries |

Required future events should include transcript_received, controller_decision, retrieval_trigger, intent_decomposition, evidence_fusion, answer_generated, refinement, grounding_check and error.
