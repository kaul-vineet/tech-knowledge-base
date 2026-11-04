"""tryIt experiments for lesson 18 (run: python try_it.py). Uses the fixed optimiser in solution/."""
import importlib.util
from pathlib import Path

import numpy as np

spec = importlib.util.spec_from_file_location("opt_fixed", Path(__file__).with_name("solution") / "optimise.py")
op = importlib.util.module_from_spec(spec)
spec.loader.exec_module(op)


def gaps(method, budget=op.BUDGET, macro=range(5)):
    rows = [op.optimise(method, m, budget) for m in macro]
    return f"mean gap {np.mean([r['gap'] for r in rows]):.3f}, worst {max(r['gap'] for r in rows):.3f}, runs {rows[0]['runs']}"


# 1. Switch OFF common random numbers: every design gets its own streams. Predict: same picks, or worse?
print("grid + OCBA, CRN on :", gaps(op.grid_search))
crn_run = op.Budget.run
op.Budget.run = lambda self, design, rep: crn_run(self, design, rep + 97 * op.DESIGNS.index(design))
print("grid + OCBA, CRN off:", gaps(op.grid_search))
op.Budget.run = crn_run

# 2. An unfair comparison: the evolution strategy quietly gets twice the budget. Predict: does it now 'win'?
print("evolution, fair budget 324:", gaps(op.evolution))
print("evolution, budget 648     :", gaps(op.evolution, budget=648))
