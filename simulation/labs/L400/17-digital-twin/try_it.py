"""tryIt experiments for lesson 17 (run: python try_it.py). Uses the fixed twin in solution/."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("twin_fixed", Path(__file__).with_name("solution") / "twin.py")
tw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tw)


def summary(**overrides):
    saved = {k: getattr(tw, k) for k in overrides}
    for k, v in overrides.items():
        setattr(tw, k, v)
    try:
        twin, errors = tw.run()
    finally:
        for k, v in saved.items():
            setattr(tw, k, v)
    alarms = [e["t_min"] for e in twin.events if e["event"] == "drift_alarm"]
    rejected = sum(e["event"] == "rejected" for e in twin.events)
    first = next((t - 2500 for t in alarms if t >= 2500), None)
    return (f"false alarms {sum(t < 2500 for t in alarms)}, detection delay {first} min, rejected {rejected}, "
            f"last-day RMSE {tw.rmse(errors, 2880):.3f} C")


# 1. CUSUM threshold h: 8 (shipped) vs 4 (NIST's rule of thumb for k = 0.5). Predict: faster detection, any cost?
for h in (8.0, 4.0):
    print(f"h={h}: {summary(CUSUM_H=h)}")
# 2. A tighter innovation gate (2.5 sigma instead of 5). Predict: safer, or does the twin lose touch?
for gate in (5.0, 2.5):
    print(f"gate={gate}: {summary(GATE=gate)}")
