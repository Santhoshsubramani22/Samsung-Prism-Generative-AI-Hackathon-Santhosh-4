from pathlib import Path
import json

from app.intelligence.controller import decide
from app.session.state import SessionState


def test_metadata_controller():
    state = SessionState()
    assert decide("How many pages are there in the PDF?", state) == "METADATA"
    assert decide("What is the PDF filename?", state) == "METADATA"
