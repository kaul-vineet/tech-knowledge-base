"""Try it 2: ask for a tighter answer (half-width 0.2 min) with the same session budget.

Predict first: does the pipeline overspend, crash, or stop and say so? python try_it/tighter_target.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pipeline  # noqa: E402
import registry  # noqa: E402

ARGS = {"baseline": {"lam": 0.8, "mu": 1.0}, "candidate": {"lam": 0.8, "mu": 1.05}, "replications": 3, "seed": 13}

if __name__ == "__main__":
    for h in (0.3, 0.2):
        pl = pipeline.Pipeline(registry.Registry(), pipeline.SimBudget(250_000), half_width=h)  # 300k minus Morris
        r = pl.submit("run_experiment", ARGS)
        hw = r["difference"]["half_width"]
        print(f"target +/- {h}: n = {r['replications']} (required {r['required_replications']}), half-width {hw:.3f}, verdict {r['verdict']}, "
              f"budget_limited {r['budget_limited']}, spent {pl.budget.spent:,} of 250,000")
