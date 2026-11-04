"""buildTask solution (lesson 15): a master that watches its own log metrics and halves the communication step.

python solution/guarded_master.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cosim  # noqa: E402


def healthy(m, max_swing=0.5, max_flips=2):
    """Oscillation detector on the logged metrics: a settled loop has a small last-hour swing and no on/off chatter."""
    return m["last_hour_swing_C"] <= max_swing and m["heater_flips"] <= max_flips


def run_guarded(h, min_h=30, log=print):
    while True:
        m = cosim.metrics(cosim.run(h))
        if healthy(m) or h / 2 < min_h:
            log(json.dumps({"event": "accepted" if healthy(m) else "gave_up", **m}))
            return h, m
        log(json.dumps({"event": "step_halved", "from_s": h, "to_s": h / 2, **m}))  # evidence for the decision
        h /= 2


if __name__ == "__main__":
    run_guarded(900)
