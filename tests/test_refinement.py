from app.session.state import SessionState
from app.session.refinement import is_late_constraint

def test_late_constraint():
    s=SessionState()
    s.current_query="What is the reimbursement policy?"
    s.current_answer="Answer v1"
    assert is_late_constraint("The trip was international.", s) is True


def test_refinement_query_contains_original_and_constraint():
    from app.session.refinement import build_refinement_query
    s = SessionState()
    s.current_query = "What is the reimbursement policy?"
    assert build_refinement_query("The trip was international.", s) == (
        "What is the reimbursement policy? The trip was international."
    )
