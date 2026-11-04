"""Seeded results of every L100 lab, at the precision the lab READMEs print.

CI runs test_fingerprints.py on Linux, macOS (Apple silicon) and Windows: all three must reproduce golden.json.
python fingerprints.py           # print the fingerprints of this machine
python fingerprints.py --write   # overwrite golden.json (only after an intended change to a lab)
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GOLDEN = HERE / "golden.json"
for lab in ("01-setup-workbench", "02-monte-carlo", "03-discrete-event-queue", "04-time-stepped-physics",
            "05-agent-based-schelling", "06-verification-validation"):
    sys.path.insert(0, str(HERE.parent / lab))

import check_env  # noqa: E402
import des_queue  # noqa: E402
import falling  # noqa: E402
import monte_carlo  # noqa: E402
import numpy as np  # noqa: E402
import schelling  # noqa: E402
import vv  # noqa: E402


def compute():
    mean, hw, p = monte_carlo.summarise(monte_carlo.sample_totals(100_000, 42))
    waits, _ = des_queue.simulate(200_000, 1)
    euler_err = falling.run(falling.step_euler, 0.1, 3.0, False)[0] - (falling.H0 - 0.5 * falling.G * 9)
    t_drag, v_drag = falling.time_to_ground(falling.step_rk4, 0.001, True)
    grid, history = schelling.run(seed=42)
    vv_mean, vv_half = vv.replicate(0.8)
    return {
        "01 seed 42 draws": check_env.seeded_draws(42),
        "02 mean / CI half-width / P(<=20)": [f"{mean:.3f}", f"{hw:.3f}", f"{p:.3f}"],
        "03 M/M/1 simulated mean wait": f"{sum(waits) / len(waits):.3f}",
        "04 Euler error dt=0.1 / fall time / impact": [f"{euler_err:+.6f}", f"{t_drag:.2f}", f"{abs(v_drag):.2f}"],
        "05 Schelling % similar / steps / grid sha256": [
            f"{history[-1][0]:.1f}", len(history) - 1,
            hashlib.sha256(grid.astype(np.int8).tobytes()).hexdigest()[:12]],  # int8: same bytes on every OS
        "06 validation mean +/- half": [f"{vv_mean:.3f}", f"{vv_half:.3f}"],
    }


if __name__ == "__main__":
    result = compute()
    if "--write" in sys.argv:
        GOLDEN.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=1))
