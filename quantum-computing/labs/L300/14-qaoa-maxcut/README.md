# Lab 14 — QAOA on MaxCut

QAOA for a 5-node, 6-edge graph (the graph from IBM's QAOA tutorial) on an exact numpy statevector: brute-force optimum, p = 1 landscape on a grid, p = 2 optimisation, approximation ratio. Then an unlucky (seeded) start leaves the optimiser stuck in a local minimum *worse than p = 1*; fix it with a warm start and restarts.

## Run
```bash
python qaoa_lab.py
python try_it.py
python solution_restarts.py
python -m unittest -v
python qaoa_qiskit.py        # SDK path: Qiskit StatevectorEstimator + scipy COBYLA (needs ../requirements.txt; CI)
```

## Expected output

**`python qaoa_lab.py`** — observed locally (Python 3.12.15, numpy 2.5.3):
```
brute force: max cut 5 by ['01001', '01011', '10100', '10110']
{"p": 1, "method": "grid 41x21", "gamma": 0.6283, "beta": 0.3927, "ratio": 0.8188}
{"p": 1, "method": "grid + descent", "ratio": 0.822}
{"p": 2, "method": "random start seed 0", "ratio": 0.7002, "params": [2.067, 0.909, -0.493, 0.029]}
most likely bitstring 01101 (cut 4), P(any optimal cut) = 0.1137
```

**`python qaoa_qiskit.py`** — *pending CI*. Expected: Qiskit ⟨C⟩ at the p = 2 optimum = numpy value (4.6234, exact); COBYLA ratio from the warm start ≥ 0.92; from random seed 0 it may also stop in a local minimum.

**`python -m unittest`** — observed locally without SDKs: `Ran 12 tests ... OK (skipped=2)`.

## Try it
**`python try_it.py`** — observed locally:
```
random_starts     {'ratios': [0.7002, 0.8352, 0.9247, 0.9247, 0.7009, 0.8329, 0.7002, 0.8329], 'hits': 2}
sample_the_answer {'P_optimal': 0.707, 'best_sampled_cut': 5, 'optimal_samples': 13}
```

## failureLab and build task — warm start + restarts
Fault: one random start (seed 0) for p = 2. Symptom: ratio 0.7002, below the p = 1 grid (0.8188); more steps do not move it. Fix: `solve()` starts from the p = 1 grid optimum interpolated to [γ/2, γ, β, β/2] plus 3 seeded random restarts, and keeps the best.

Reference **`python solution_restarts.py`** — observed locally:
```
{"p": 1, "method": "warm start + 3 restarts", "ratio": 0.822, "params": [0.649, 0.354]}
{"p": 2, "method": "warm start + 3 restarts", "ratio": 0.9247, "params": [0.585, 1.029, 0.517, 0.309]}
```
Proof — observed locally:
```
$ BUILD_TASK_MODULE=qaoa_lab python -m unittest test_build_task           # one random start
FAIL: test_p1_reaches_grid_quality ... AssertionError: np.float64(0.6997) not greater than or equal to 0.82
FAIL: test_p2_reaches_best_known_ratio ... AssertionError: np.float64(0.7002) not greater than or equal to 0.92
FAILED (failures=2)
$ python -m unittest test_build_task                                     # solution_restarts
Ran 3 tests ... OK
```
