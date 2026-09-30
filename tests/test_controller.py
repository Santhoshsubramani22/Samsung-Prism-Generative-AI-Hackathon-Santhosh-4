from app.intelligence.controller import decide
from app.session.state import SessionState

def test_wait():
    assert decide("I need information about", SessionState()) == "WAIT"

def test_retrieve():
    assert decide("I need information about reimbursement", SessionState()) == "RETRIEVE"

def test_suppress():
    s=SessionState()
    s.current_answer="Previous answer"
    assert decide("Make the answer shorter.", s) == "SUPPRESS"
