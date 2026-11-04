"""Shared helpers for the question-bank data modules (tools/qbank_L*.py) and tools/build_qbank.py.

Q(...) records one question with the CORRECT option first; build_qbank.py moves it to a balanced position.
Calculation values are computed in the data modules with numpy / labs/_shared/qsim, never typed in by hand;
research/qbank_checks.py recomputes each of them independently.
"""
import sys
from pathlib import Path

TOPIC = Path(__file__).resolve().parent.parent
SHARED = TOPIC / "labs" / "_shared"
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))


def Q(qid, lesson, qtype, difficulty, question, options, explanation, source, code=None):
    assert len(options) == 4, qid
    q = {"id": qid, "lesson": lesson, "type": qtype, "difficulty": difficulty, "question": question,
         "options": list(options), "explanation": explanation, "source": source}
    if code is not None:
        q["code"] = code.strip("\n")
    return q


def fmt(x, nd=4):
    """Round for display; -0.0 becomes 0.0."""
    return round(float(x), nd) + 0.0
