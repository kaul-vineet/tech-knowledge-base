"""Deterministic fake-model rule for agent_assist.py (used by tests and `--fake`; it is NOT a model).

Registers ONE route in the vendored fake server (labs/_shared/local_agent/fake_model_server.py) through its
EXTRA_RULES hook, keyed on the marker string "[[QASM-DRAFT]]" in the last user message. The vendored server
file itself is unchanged. Replies imitate typical small-model output (prose + a fenced program), sometimes
with a plausible bug, so the code check has something real to catch:
  "phase" in the request -> uses rz(pi/2): valid OpenQASM 3, but outside the lab parser's subset
  "GHZ"   in the request -> forgets the second cx (wrong circuit)
  "Bell"  in the request -> a correct Bell pair
  anything else          -> no program at all
"""
MARKER = "[[QASM-DRAFT]]"

HEADER = 'OPENQASM 3.0;\ninclude "stdgates.inc";\n'
BELL = HEADER + "qubit[2] q;\nbit[2] c;\nh q[0];\ncx q[0], q[1];\nc = measure q;\n"
BELL_PHASE = HEADER + "qubit[2] q;\nbit[2] c;\nh q[0];\nrz(pi/2) q[0];\ncx q[0], q[1];\nc = measure q;\n"
GHZ_BUGGY = HEADER + "qubit[3] q;\nbit[3] c;\nh q[0];\ncx q[0], q[1];\nc = measure q;\n"


def reply(user_text):
    text = user_text.lower()
    if "phase" in text:
        program = BELL_PHASE
    elif "ghz" in text:
        program = GHZ_BUGGY
    elif "bell" in text:
        program = BELL
    else:
        return "Sorry, I can only draft small textbook circuits."
    return f"Here is the circuit you asked for:\n```qasm\n{program}```\nIt should work on any OpenQASM 3 tool."


def register(fake_server_module):
    """Add the rule once (idempotent, so several tests can call it)."""
    if all(marker != MARKER for marker, _ in fake_server_module.EXTRA_RULES):
        fake_server_module.EXTRA_RULES.append((MARKER, reply))
