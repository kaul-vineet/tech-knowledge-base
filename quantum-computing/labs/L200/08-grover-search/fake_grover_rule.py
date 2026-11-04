"""Deterministic fake-model rule for agent_assist.py (used by tests and `--fake`; it is NOT a model).

Registers ONE route in the vendored fake server (labs/_shared/local_agent/fake_model_server.py) through its
EXTRA_RULES hook, keyed on the marker string "[[GROVER-ORACLE]]" in the last user message. The vendored
server file itself is unchanged. Replies imitate typical small-model output (prose + a fenced JSON proposal),
each with a plausible mistake for the code check to catch:
  "q0 = 1" in the request   -> writes the string in q0-first order ('110' instead of Qiskit's '011')
  "two 1s" in the request   -> right marked states, but reuses k=2 from the 1-marked case (overshoots)
  "even" in the request     -> right marked states for a problem where Grover cannot help (M = N/2)
  anything else             -> no proposal at all
"""
import json

MARKER = "[[GROVER-ORACLE]]"

PROPOSALS = {
    "q0 = 1": {"marked": ["110"], "iterations": 2},
    "two 1s": {"marked": ["101", "110"], "iterations": 2},
    "even": {"marked": ["00", "10"], "iterations": 1},
}


def reply(user_text):
    for key, proposal in PROPOSALS.items():
        if key in user_text:
            return f"Sure! Here is the oracle:\n```json\n{json.dumps(proposal)}\n```\nRun it and you will find the answer."
    return "I am not sure which states to mark."


def register(fake_server_module):
    """Add the rule once (idempotent, so several tests can call it)."""
    if all(marker != MARKER for marker, _ in fake_server_module.EXTRA_RULES):
        fake_server_module.EXTRA_RULES.append((MARKER, reply))
