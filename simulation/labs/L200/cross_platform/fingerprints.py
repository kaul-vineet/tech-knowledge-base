"""Seeded results of every L200 lab, at the precision the lab READMEs print.

CI runs test_fingerprints.py on Linux, macOS (Apple silicon) and Windows: all three must reproduce golden.json.
python fingerprints.py           # print the fingerprints of this machine
python fingerprints.py --write   # overwrite golden.json (only after an intended change to a lab)
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GOLDEN = HERE / "golden.json"
for lab in ("07-input-modelling", "08-multi-server-queue", "09-adaptive-ode", "10-warmup-replications",
            "11-supply-chain-inventory"):
    sys.path.insert(0, str(HERE.parent / lab))

import adaptive_ode  # noqa: E402
import fit_inputs  # noqa: E402
import inventory  # noqa: E402
import mmc_queue  # noqa: E402
import numpy as np  # noqa: E402
import warmup  # noqa: E402


def compute():
    x = fit_inputs.load()
    ks = [f"{fit_inputs.ks_statistic(x, f(x)['cdf']):.3f}" for f in fit_inputs.FITTERS]
    wait = fit_inputs.queue_waits(fit_inputs.fit_lognormal(x)["sample"], 0.85 / x.mean()).mean()
    sim = mmc_queue.simulate(200_000)
    ts, ys, rej = adaptive_ode.solve(adaptive_ode.lotka_volterra, 0, [10.0, 5.0], 15, rtol=1e-6)
    runs = np.array([warmup.waits(5_000, seed) for seed in range(1, 21)])
    d, _ = warmup.warmup_point(warmup.welch(runs, window=50))
    crn = inventory.compare((30, 80), (30, 90))
    return {
        "07 KS D exp/normal/lognormal + lognormal-fed wait": ks + [f"{wait:.2f}"],
        "08 M/M/3 simulated Wq / Lq / util": [f"{sim['Wq']:.3f}", f"{sim['Lq']:.3f}", f"{sim['util']:.3f}"],
        "09 Lotka-Volterra steps / rejected / foxes(15)": [len(ts) - 1, rej, f"{ys[-1, 1]:.6f}"],
        "10 Welch warm-up proposal": d,
        "11 CRN cost difference +/- half-width": [f"{crn[0]:+.2f}", f"{crn[1]:.2f}"],
    }


if __name__ == "__main__":
    result = compute()
    if "--write" in sys.argv:
        GOLDEN.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=1))
