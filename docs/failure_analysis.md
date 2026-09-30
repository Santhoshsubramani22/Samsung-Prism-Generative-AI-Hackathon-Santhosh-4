# Failure Analysis

## 1. Premature retrieval
Cause: controller may classify a short phrase as stable.
Impact: unnecessary retrieval and latency.
Detection: compare controller decision with transcript completeness.
Mitigation: strengthen stability rules and evaluate on a labeled stream set.

## 2. Late constraint
Cause: important context arrives after Answer v1.
Impact: an earlier answer may contain a claim that no longer applies.
Handling: preserve session state, retrieve using the late constraint, increment answer version, and keep unaffected evidence.

## 3. Insufficient evidence
Cause: corpus does not contain the requested fact.
Impact: unsupported generation risk.
Handling: the pipeline returns an explicit insufficient-evidence message when retrieval returns no evidence, and grounding limits citations to retrieved chunks.
