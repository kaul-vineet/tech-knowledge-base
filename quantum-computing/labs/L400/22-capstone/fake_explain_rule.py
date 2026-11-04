"""Deterministic fake-model rule for the capstone's agent_assist.py (tests and --fake; NOT a model).

Registers ONE route in the vendored fake server through its EXTRA_RULES hook, keyed on "[[QOPT-REPORT]]".
  "Explain" -> names the code's winner and quotes only numbers from the report (should be accepted)
  "Pitch"   -> claims qaoa-noisy wins with "quantum advantage" and an invented 99.9 % (should be rejected)
  "Brief"   -> says nothing checkable (should be rejected: no winner stated)
"""
MARKER = "[[QOPT-REPORT]]"
REPLIES = {
    "Explain": ("annealing wins. All three solvers reached the optimum cut of 10 in 5 of 5 runs (median ratio 1.0), "
                "so the tie-break is samples to the best cut: annealing needed 13, greedy 32, qaoa-noisy 1013. "
                "Readout mitigation moved the QAOA estimate of <C> from 6.774 to 6.8549 against a gate-noise-only "
                "value of 6.8418."),
    "Pitch": "qaoa-noisy wins and shows quantum advantage: it found the optimum with 99.9% reliability.",
    "Brief": "The service ran fine and the results look reasonable.",
}


def reply(user_text):
    for key, text in REPLIES.items():
        if key in user_text:
            return text
    return "No comment."


def register(fake_server_module):
    if all(marker != MARKER for marker, _ in fake_server_module.EXTRA_RULES):
        fake_server_module.EXTRA_RULES.append((MARKER, reply))
