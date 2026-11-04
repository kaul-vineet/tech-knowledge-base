# Lab 18 — Benchmarking honestly against classical solvers

MaxCut on seeded 3-regular graphs (n = 8, 12, 16): exact enumeration (reference), greedy local search, simulated
annealing and QAOA p = 1 on the noiseless simulator. The budget unit is a **sample** (one candidate bitstring evaluated:
a flip evaluation or a shot). The shipped `compare()` is biased; the fair harness (`solution_fair.py`) gives every solver
the same budget and seeds, reports medians and rejects over-spending. Decision: `docs/adr/0001-fair-benchmark.md`.

## Run
```bash
python bench_lab.py         # biased method
python solution_fair.py     # fair harness
python try_it.py
python -m unittest -v
python bench_qiskit.py      # SDK path (CI)
```

## Expected output
**`python bench_lab.py`** — observed locally (Python 3.12.15, numpy 2.5.3, cryptography 50.0.2; Linux sandbox, no quantum SDKs); `local_s` varies by machine:
```
{"n": 8, "solver": "greedy", "budget": 200, "runs": 1, "median_ratio": 1.0, "success": 1.0, "median_first_best": 32, "tts99_samples": 200, "local_s": …}
{"n": 8, "solver": "annealing", "budget": 200, "runs": 1, "median_ratio": 0.8, "success": 0.0, "median_first_best": 3, "tts99_samples": null, "local_s": …}
{"n": 8, "solver": "qaoa", "budget": 200, "runs": 1, "median_ratio": 1.0, "success": 1.0, "median_first_best": 412, "tts99_samples": 200, "local_s": …}
{"n": 8, "winner": "greedy", "method": "naive (unequal budget, best seed)"}
{"n": 12, "solver": "greedy", "budget": 200, "runs": 1, "median_ratio": 0.8, "success": 0.0, "median_first_best": 48, "tts99_samples": null, "local_s": …}
{"n": 12, "solver": "annealing", "budget": 200, "runs": 1, "median_ratio": 0.8667, "success": 0.0, "median_first_best": 25, "tts99_samples": null, "local_s": …}
{"n": 12, "solver": "qaoa", "budget": 200, "runs": 1, "median_ratio": 1.0, "success": 1.0, "median_first_best": 426, "tts99_samples": 200, "local_s": …}
{"n": 12, "winner": "qaoa", "method": "naive (unequal budget, best seed)"}
{"n": 16, "solver": "greedy", "budget": 200, "runs": 1, "median_ratio": 0.9545, "success": 0.0, "median_first_best": 48, "tts99_samples": null, "local_s": …}
{"n": 16, "solver": "annealing", "budget": 200, "runs": 1, "median_ratio": 1.0, "success": 1.0, "median_first_best": 24, "tts99_samples": 200, "local_s": …}
{"n": 16, "solver": "qaoa", "budget": 200, "runs": 1, "median_ratio": 1.0, "success": 1.0, "median_first_best": 450, "tts99_samples": 200, "local_s": …}
{"n": 16, "winner": "annealing", "method": "naive (unequal budget, best seed)"}
```
**`python solution_fair.py`**:
```
{"n": 8, "solver": "greedy", "budget": 200, "runs": 10, "median_ratio": 1.0, "success": 1.0, "median_first_best": 36, "tts99_samples": 200, "local_s": …}
{"n": 8, "solver": "annealing", "budget": 200, "runs": 10, "median_ratio": 1.0, "success": 1.0, "median_first_best": 33, "tts99_samples": 200, "local_s": …}
{"n": 8, "solver": "qaoa", "budget": 200, "runs": 10, "median_ratio": 1.0, "success": 1.0, "median_first_best": 111, "tts99_samples": 200, "local_s": …}
{"n": 8, "winner": "annealing", "method": "fair (same budget, same 10 seeds, medians)"}
{"n": 12, "solver": "greedy", "budget": 200, "runs": 10, "median_ratio": 0.9333, "success": 0.4, "median_first_best": 66, "tts99_samples": 1803, "local_s": …}
{"n": 12, "solver": "annealing", "budget": 200, "runs": 10, "median_ratio": 0.9333, "success": 0.3, "median_first_best": 62, "tts99_samples": 2582, "local_s": …}
{"n": 12, "solver": "qaoa", "budget": 200, "runs": 10, "median_ratio": 0.9667, "success": 0.5, "median_first_best": 115, "tts99_samples": 1329, "local_s": …}
{"n": 12, "winner": "qaoa", "method": "fair (same budget, same 10 seeds, medians)"}
{"n": 16, "solver": "greedy", "budget": 200, "runs": 10, "median_ratio": 1.0, "success": 0.9, "median_first_best": 136, "tts99_samples": 400, "local_s": …}
{"n": 16, "solver": "annealing", "budget": 200, "runs": 10, "median_ratio": 1.0, "success": 0.8, "median_first_best": 85, "tts99_samples": 572, "local_s": …}
{"n": 16, "solver": "qaoa", "budget": 200, "runs": 10, "median_ratio": 1.0, "success": 0.6, "median_first_best": 141, "tts99_samples": 1005, "local_s": …}
{"n": 16, "winner": "greedy", "method": "fair (same budget, same 10 seeds, medians)"}
```
**`python -m unittest`**: `Ran 15 tests ... OK (skipped=1)`.

**`python bench_qiskit.py`** — *pending CI*. Expected: TVD < 0.05 between Qiskit's sampled cut distribution and numpy's.

## Try it
```
other_instances {1: 'annealing', 2: 'greedy', 3: 'qaoa', 4: 'annealing', 5: 'annealing'}
exact_in_budget ({'greedy': 1.0, 'annealing': 1.0, 'qaoa': 1.0, 'exact': 1.0}, 'greedy')
```

## failureLab and build task — a fair harness
Fault: QAOA gets 4× budget and its best of 10 seeds; the baselines run once at a quarter budget; `used` is never checked;
every row still claims budget 200. Fix: `compare(n, solvers, budget, seeds, edges=None)` in `my_fair.py`.
```bash
BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v        # your my_fair.py
BUILD_TASK_MODULE=bench_lab python -m unittest test_build_task test_fitness   # the shipped (unfixed) lab file: must fail
```
```powershell
$env:BUILD_TARGET = "mine"; python -m unittest test_build_task test_fitness -v; Remove-Item Env:BUILD_TARGET
```
Proof — observed locally on the shipped file:
```
FAIL: test_over_budget_solver_is_rejected (test_build_task.FairHarness.test_over_budget_solver_is_rejected)
AssertionError: RuntimeError not raised
FAIL: test_rows_summarise_every_run (test_build_task.FairHarness.test_rows_summarise_every_run)
AssertionError: Lists differ: [1, 1] != [4, 4]
FAIL: test_same_budget_and_seeds_for_every_solver (test_build_task.FairHarness.test_same_budget_and_seeds_for_every_solver)
AssertionError: Lists differ: [(25, 1)] != [(100, 1), (100, 2), (100, 3)]
FAIL: test_reference_config (test_fitness.ComparisonMethodFitness.test_reference_config)
AssertionError: Items in the first set but not the second:
Ran 6 tests in 3.137s
FAILED (failures=4)
```
Solution and `BUILD_TARGET=mine` with a correct file: `Ran 6 tests ... OK`.
