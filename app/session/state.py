import uuid
from datetime import datetime


class SessionState:
    def __init__(self):
        self.session_id = "S-" + uuid.uuid4().hex[:8].upper()
        self.current_query = ""
        self.previous_query = ""
        self.current_answer = ""
        self.answer_version = 0
        self.citations = []
        self.retrieved_evidence = []
        self.detected_intents = []
        self.constraints = []
        self.telemetry = []

    def update(self, query, answer, citations, evidence, intents, constraints=None):
        self.previous_query = self.current_query
        self.current_query = query
        self.current_answer = answer
        self.answer_version += 1
        self.citations = citations
        self.retrieved_evidence = evidence
        self.detected_intents = intents
        if constraints:
            for constraint in constraints:
                if constraint not in self.constraints:
                    self.constraints.append(constraint)
        self.telemetry.append({
            "timestamp": datetime.now().isoformat(),
            "event": "answer_version",
            "version": self.answer_version,
        })

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "current_query": self.current_query,
            "previous_query": self.previous_query,
            "current_answer": self.current_answer,
            "answer_version": self.answer_version,
            "citations": self.citations,
            "retrieved_evidence": [e["chunk"]["chunk_id"] for e in self.retrieved_evidence],
            "detected_intents": self.detected_intents,
            "constraints": self.constraints,
            "telemetry": self.telemetry,
        }
