"""Deterministic fake-model rule for agent_assist.py (used by tests and `--fake`; it is NOT a model).

Registers ONE route in the vendored fake server (labs/_shared/local_agent/fake_model_server.py) through its
EXTRA_RULES hook, keyed on the marker "[[VQE-LOG]]" in the last user message. The vendored server is unchanged.
Replies imitate typical small-model output (prose + a fenced proposal), each with something for code to check:
  "Diagnose"  -> right diagnosis, right best energy, sensible SPSA proposal (should be accepted)
  "Report"    -> copies the exact ground energy as "best energy" (not in the log), blames the learning rate,
                 proposes gradient descent with a smaller step (should be rejected)
  "regardless of cost" -> right diagnosis, but proposes 1,000,000 shots per term with the same optimizer
  anything else -> no proposal
"""
import json

MARKER = "[[VQE-LOG]]"

PROPOSALS = {
    "Diagnose": {"diagnosis": "shot_noise", "best_energy": -1.77348,
                 "proposal": {"optimizer": "spsa", "shots": 1000, "a": 1.0, "c": 0.2}},
    "Report": {"diagnosis": "learning_rate_too_high", "best_energy": -1.8405,
               "proposal": {"optimizer": "gd", "shots": 1000, "lr": 0.1}},
    "regardless of cost": {"diagnosis": "shot_noise", "best_energy": -1.77348,
                           "proposal": {"optimizer": "gd", "shots": 1000000}},
}


def reply(user_text):
    for key, proposal in PROPOSALS.items():
        if key in user_text:
            return f"Looking at the log, here is my assessment:\n```\n{json.dumps(proposal)}\n```\nHope this helps!"
    return "The log looks fine to me."


def register(fake_server_module):
    """Add the rule once (idempotent, so several tests can call it)."""
    if all(marker != MARKER for marker, _ in fake_server_module.EXTRA_RULES):
        fake_server_module.EXTRA_RULES.append((MARKER, reply))
