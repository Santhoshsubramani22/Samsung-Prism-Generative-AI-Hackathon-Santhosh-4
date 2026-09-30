import json
import threading

from flask import Flask, render_template, request, jsonify, Response
from app.session.state import SessionState
from app.intelligence.controller import decide
from app.intelligence.decomposer import decompose
from app.rag.pipeline import answer_query, answer_metadata_query, stream_answer_query
from app.session.refinement import is_late_constraint
from app.telemetry.logger import get_events

app = Flask(__name__)
sessions = {}
sessions_lock = threading.Lock()


def get_session():
    sid = request.cookies.get("session_id")
    with sessions_lock:
        if not sid or sid not in sessions:
            state = SessionState()
            sessions[state.session_id] = state
            sid = state.session_id
        return sessions[sid], sid


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat")
def chat():
    return render_template("chat.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/state")
def state_api():
    state, sid = get_session()
    response = jsonify(state.to_dict())
    response.set_cookie("session_id", sid, httponly=True, samesite="Lax")
    return response


@app.route("/api/query", methods=["POST"])
def query_api():
    data = request.get_json(force=True)
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "Query is required"}), 400

    state, sid = get_session()
    decision = decide(query, state)
    late = is_late_constraint(query, state)

    if decision == "METADATA":
        result = answer_metadata_query(query, state)
        result.update({"controller": decision, "session_id": sid, "refinement": False})
    elif decision == "SUPPRESS":
        answer = state.current_answer or "There is no previous answer to restructure."
        result = {
            "session_id": sid,
            "controller": decision,
            "answer": answer,
            "citations": state.citations,
            "intents": state.detected_intents,
            "answer_version": state.answer_version,
            "retrieval": {"executed": False, "reason": "presentation_only"},
            "refinement": False,
            "grounding": {"grounded": True, "support_score": 1.0},
        }
    elif decision == "WAIT":
        result = {
            "session_id": sid,
            "controller": decision,
            "answer": "Please complete the question so I can retrieve the right evidence.",
            "citations": [],
            "intents": [],
            "answer_version": state.answer_version,
            "retrieval": {"executed": False, "reason": "incomplete_intent"},
            "refinement": False,
        }
    else:
        decomposition = decompose(query)
        result = answer_query(query, state, decomposition, late_constraint=late)
        result.update({"controller": decision, "session_id": sid, "refinement": late})

    response = jsonify(result)
    response.set_cookie("session_id", sid, httponly=True, samesite="Lax")
    return response


@app.route("/api/stream", methods=["POST"])
def stream_api():
    data = request.get_json(force=True)
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "Query is required"}), 400

    state, sid = get_session()
    decision = decide(query, state)
    late = is_late_constraint(query, state)

    def events():
        yield f"data: {json.dumps({'type': 'controller', 'value': decision}, ensure_ascii=False)}\n\n"

        if decision == "WAIT":
            payload = {
                "type": "final",
                "controller": decision,
                "answer": "Please complete the question so I can retrieve the right evidence.",
                "answer_version": state.answer_version,
                "retrieval": {"executed": False, "reason": "incomplete_intent"},
                "session_id": sid,
            }
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
        elif decision == "METADATA":
            result = answer_metadata_query(query, state)
            result.update({"controller": decision, "session_id": sid})
            yield f"data: {json.dumps({'type': 'final', **result}, ensure_ascii=False)}\n\n"
        elif decision == "SUPPRESS":
            payload = {
                "type": "final",
                "controller": decision,
                "answer": state.current_answer or "No previous answer is available.",
                "citations": state.citations,
                "answer_version": state.answer_version,
                "retrieval": {"executed": False, "reason": "presentation_only"},
                "refinement": False,
                "session_id": sid,
            }
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
        else:
            decomposition = decompose(query)
            for event in stream_answer_query(query, state, decomposition, late_constraint=late):
                event["controller"] = decision
                event["session_id"] = sid
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

        yield "data: [DONE]\n\n"

    response = Response(events(), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    response.headers["Connection"] = "keep-alive"
    response.set_cookie("session_id", sid, httponly=True, samesite="Lax")
    return response


@app.route("/api/telemetry")
def telemetry_api():
    return jsonify(get_events())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
