import os
import re
from typing import Iterator

try:
    from google import genai
except Exception:  # pragma: no cover
    genai = None


def _context(evidence):
    return "\n\n".join(
        f"[{e['chunk']['document_id']} | {e['chunk']['chunk_id']} | page {e['chunk']['page']}]\n"
        f"{e['chunk']['chunk_text']}"
        for e in evidence
    )


def build_prompt(query, evidence, previous_answer="", late_constraint=False):
    context = _context(evidence)
    refinement = "YES" if late_constraint else "NO"
    return f"""You are a concise, strictly grounded document QA system.
Answer the user's exact question using ONLY the evidence below.

Rules:
- Do not dump or reproduce whole evidence chunks.
- Do not mention unrelated evidence.
- Give the shortest complete answer, normally 1-4 sentences or a few bullets.
- Preserve names, numbers, dates and facts exactly as supported.
- If the evidence does not answer the question, say: "I couldn't find this information in the provided document."
- Never invent a person's role, identity, number, date, or other fact.
- Every factual answer must include one or more citations in this exact form: [DOCUMENT_ID | CHUNK_ID].
- If this is a refinement, preserve useful facts from the previous answer and change only what the new constraint requires.
- Do not claim that a fact is supported unless the provided evidence contains that fact.

Previous answer:
{previous_answer}

Late constraint/refinement: {refinement}

User question:
{query}

Relevant evidence:
{context}
"""


def synthesize(query, evidence, previous_answer="", late_constraint=False):
    chunks = list(synthesize_stream(query, evidence, previous_answer, late_constraint))
    text = "".join(chunks).strip()
    return text or extractive_answer(query, evidence, previous_answer, late_constraint)


def synthesize_stream(query, evidence, previous_answer="", late_constraint=False) -> Iterator[str]:
    """Yield answer deltas. Uses Gemini's streaming API when configured; otherwise streams fallback text."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    prompt = build_prompt(query, evidence, previous_answer, late_constraint)

    if api_key and genai is not None:
        try:
            client = genai.Client(api_key=api_key)
            stream = client.models.generate_content_stream(
                model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                contents=prompt,
            )
            emitted = False
            for response in stream:
                text = getattr(response, "text", None) or ""
                if text:
                    emitted = True
                    yield text
            if emitted:
                return
        except Exception:
            # Fall through to deterministic local streaming.
            pass

    fallback = extractive_answer(query, evidence, previous_answer, late_constraint)
    for piece in _stream_text(fallback):
        yield piece


def _stream_text(text, chunk_size=24):
    """Small deterministic chunks make the no-API demo visibly incremental."""
    text = text or ""
    for i in range(0, len(text), chunk_size):
        yield text[i:i + chunk_size]


def extractive_answer(query, evidence, previous_answer="", late_constraint=False):
    if not evidence:
        return "I couldn't find this information in the provided document."

    q = query.lower()
    # Name/person lookup: extract a compact sentence/line rather than dumping chunks.
    if q.startswith(("who ", "who is ", "who was ")):
        for e in evidence:
            text = e["chunk"]["chunk_text"]
            for sentence in text.replace("\n", ". ").split("."):
                s = sentence.strip()
                if any(k in s.lower() for k in ["name:", "named ", "author", "prepared by", "submitted by"]):
                    return f"{s}. [{e['chunk']['document_id']} | {e['chunk']['chunk_id']}]"

    # Refinement: keep the previous answer when the new evidence does not contain a better fact.
    if late_constraint and previous_answer:
        best = _best_sentence(query, evidence)
        if best:
            return f"{best} [{best[1]} | {best[2]}]"
        return previous_answer

    best = _best_sentence(query, evidence)
    if best:
        return f"{best[0]}. [{best[1]} | {best[2]}]"

    c = evidence[0]["chunk"]
    text = c["chunk_text"].strip()
    sentences = [s.strip() for s in re.split(r"[.!?]+", text.replace("\n", ". ")) if s.strip()]
    selected = ". ".join(sentences[:2])
    return f"{selected}. [{c['document_id']} | {c['chunk_id']}]"


def _best_sentence(query, evidence):
    q_tokens = set(re.findall(r"[a-z0-9]+", query.lower()))
    best = None
    best_score = 0
    for e in evidence:
        c = e["chunk"]
        for sentence in re.split(r"[.!?]+", c["chunk_text"].replace("\n", ". ")):
            s = sentence.strip()
            if not s:
                continue
            tokens = set(re.findall(r"[a-z0-9]+", s.lower()))
            score = len(q_tokens & tokens) / max(1, len(q_tokens))
            if score > best_score:
                best_score = score
                best = (s, c["document_id"], c["chunk_id"])
    return best
