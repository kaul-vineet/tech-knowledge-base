# 18 · Simulation-based optimisation: grid vs surrogate vs evolution, ranking & selection, common random numbers

Choose the cheapest (s, Q) reorder policy for the L200 lesson 11 bike shop, from 81 designs, under uncertain demand. Three optimisers get the same budget (324 simulation runs) and the same common random numbers: grid search, a GP-lite surrogate with expected improvement, and a (μ + λ) evolution strategy. A referee (`truth.json`, 100 replications per design on streams no optimiser sees) scores the design each one picks. The failure lab is the winner's curse. The fix is an OCBA selection stage on fresh streams, inside the same budget.

Read the concept note first: `../../../content/concepts/L400/18-sim-optimisation.md`. Needs Python 3.12 + numpy. It imports `labs/L200/11-supply-chain-inventory/inventory.py`.

## Run
```bash
python optimise.py         # about 1 minute here (15 optimisations x 324 runs); faster on the Mac mini / Windows PC
python make_truth.py       # optional: regenerates truth.json (8,100 runs, about 1 minute)
```

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux) - shipped file
```
81 (s, Q) designs; true best (25, 70) at 8.479/day (truth.json: 100 reps per design)
budget 324 runs per optimiser (0 reserved for selection), 5 macro-replications
method             mean gap worst gap  reported - true  runs
grid_search           0.049     0.117           -0.472   324   picks [(30, 80), (20, 80), (25, 90), (25, 80), (25, 80)]
surrogate_search      0.277     1.085           -0.412   324   picks [(25, 70), (30, 70), (30, 90), (10, 80), (25, 80)]
evolution             0.052     0.145           -0.299   324   picks [(25, 80), (35, 60), (30, 70), (20, 80), (30, 70)]
```
"gap" is the true cost of the picked design minus the true best, per day. "reported - true" is how optimistic the reported cost is.

## Failure lab: break it, see it, fix it
- **Fault (seeded, shipped in `optimise.py`):** `pick()` returns the design with the lowest search-phase mean and reports that mean as its cost. That design is partly the luckiest noise, so the report is 0.30-0.47/day too optimistic, and the grid's worst pick is 0.117/day off (beyond the 0.10 indifference zone).
- **Fix (your build task):** keep `RESERVE = 60` runs inside the budget. Re-run the top 5 finalists on fresh streams (index 500+, still common across finalists) with OCBA allocation (`ocba()` is provided), pick the best and report the fresh estimate (`solution/optimise.py`):
```
budget 324 runs per optimiser (60 reserved for selection), 5 macro-replications
method             mean gap worst gap  reported - true  runs
grid_search           0.042     0.088           -0.161   324   picks [(30, 60), (25, 80), (25, 60), (20, 80), (30, 70)]
surrogate_search      0.090     0.186           -0.188   324   picks [(25, 80), (35, 70), (25, 80), (20, 80), (35, 70)]
evolution             0.088     0.241           -0.295   324   picks [(25, 60), (30, 50), (25, 60), (30, 70), (25, 70)]
```
Over 12 macro-replications of the grid (`research/concept_examples_L400.py`), the bias went from -0.394 to -0.143, the mean gap from 0.070 to 0.043, and the worst gap from 0.260 to 0.088. The referee's own standard error is 0.085, shared by all designs, so with 5 macro-replications the bias column is noisy.
- **Proof:** `BUILD_TARGET=mine python -m unittest test_build_task` fails 2 of 2 on the shipped file and passes on the solution. `TestFailureLab` keeps the winner's curse reproducible (mean bias < -0.3).

## Design decision and fitness function
Decision: `decisions/0001-grid-plus-ocba.md`. Use grid + OCBA for this 2-D, 81-design problem, and revisit when designs exceed about budget / 3. Fitness function `test_fitness.py`: every optimiser spends ≤ 324 runs (budget fairness), the grid's mean gap is ≤ 0.06 and worst gap ≤ 0.10 over 5 macro-replications, and |reported - true| ≤ 0.15 over 12. Observed: `Ran 3 tests ... OK` on the solution, and `FAILED (failures=2)` on the shipped file with `BUILD_TARGET=mine` (worst gap 0.117; bias 0.394).

## Test
```bash
python -m unittest -v
```
Observed: `Ran 12 tests ... OK` (test_optimise 7, test_build_task 2 and test_fitness 3; about 1 minute here).

## Try it
```bash
python try_it.py
```
Observed:
```
grid + OCBA, CRN on : mean gap 0.042, worst 0.088, runs 324
grid + OCBA, CRN off: mean gap 0.200, worst 0.372, runs 324
evolution, fair budget 324: mean gap 0.088, worst 0.241, runs 324
evolution, budget 648     : mean gap 0.008, worst 0.021, runs 648
```
Without common random numbers, design differences drown in day-to-day demand noise. With twice the budget, any method "wins". That is why `Budget` raises an error instead of returning an extra result.

## Build it (design task)
Rewrite `pick(budget, data)` in `optimise.py` so that the winner and its reported cost come from a selection stage. Use `RESERVE` runs, the top `FINALISTS = 5` designs, fresh streams starting at index `FRESH = 500`, a first look of 5 runs each, then OCBA in steps of 5 until the budget is spent.

Hints:
- `optimise()` already hides `RESERVE` runs from the search (`budget.total = budget_total - RESERVE`), then restores the total before calling `pick()`.
- `ocba(means, sds, total)` returns the ideal runs per finalist. Give the next 5 runs to the finalist furthest below its share.
- Report the mean of the fresh runs only.

Check: `BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v` (PowerShell: `$env:BUILD_TARGET = "mine"`).

## Library equivalent (pending-ci)
`simpy_inventory.py` in L200 lesson 11 (SimPy 4.1.2) is the same model as processes. Optimisation itself needs no library here. scikit-optimize-style Bayesian optimisers and CMA-ES packages are listed as equivalents only.

## Files
- `optimise.py`: main lab (Budget, grid, GP-lite + EI, (μ+λ)-ES, `ocba()`). Ships the unfixed `pick()`.
- `make_truth.py` / `truth.json`: the referee (not part of any budget).
- `solution/optimise.py`: buildTask solution (selection stage).
- `try_it.py`, `test_optimise.py`, `test_build_task.py`, `test_fitness.py`.
- `decisions/0001-grid-plus-ocba.md`: the ADR.
