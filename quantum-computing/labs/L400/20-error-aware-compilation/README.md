# Lab 20 — Error-aware compilation: layout, routing and a depth budget

Lesson 14's 5-node QAOA circuit (12 CX, logical depth 17) compiled onto a fake 8-qubit ladder with seeded per-edge
errors; today's calibration drifted edge (1,2) to 15 %. Options are scored by ESP (product of gate and readout
fidelities), CX count and depth; `noisy_check.py` proves equivalence and simulates the noisy output. Depth budget 22.
Decision: `docs/adr/0001-noise-aware-compile.md`.

## Run
```bash
python compile_lab.py        # options A (trivial) and B (degree-based + cancel)
python solution_layout.py    # option C: noise-aware layout (brute force over 6720 placements)
python try_it.py
python -m unittest -v
python compile_qiskit.py     # Qiskit Target with the same error map, levels 0-3 (CI)
```

## Expected output
**`python compile_lab.py`** — observed locally (Python 3.12.15, numpy 2.5.3, cryptography 50.0.2; Linux sandbox, no quantum SDKs):
```
{"device": "calibrated", "option": "A trivial + hop routing", "layout": [0, 1, 2, 3, 4], "esp": 0.5763, "cx": 27, "depth": 32, "within_depth_budget": false}
{"device": "calibrated", "option": "B dense + hop routing + cancel", "layout": [1, 5, 2, 6, 3], "esp": 0.7315, "cx": 19, "depth": 24, "within_depth_budget": false}
{"device": "drifted (1,2) = 15%", "option": "A trivial + hop routing", "layout": [0, 1, 2, 3, 4], "esp": 0.2084, "cx": 27, "depth": 32, "within_depth_budget": false}
{"device": "drifted (1,2) = 15%", "option": "B dense + hop routing + cancel", "layout": [1, 5, 2, 6, 3], "esp": 0.3059, "cx": 19, "depth": 24, "within_depth_budget": false}
logical circuit: {'esp': 1.0, 'cx': 12, 'depth': 17}
```
**`python solution_layout.py`**:
```
{"device": "calibrated", "option": "C noise-aware layout + reliable routing + cancel", "layout": [2, 3, 6, 1, 5], "esp": 0.7925, "cx": 13, "depth": 18, "within_depth_budget": true}
{"device": "drifted (1,2) = 15%", "option": "C noise-aware layout + reliable routing + cancel", "layout": [5, 1, 6, 2, 3], "esp": 0.7835, "cx": 19, "depth": 21, "within_depth_budget": true}
```
**`python -m unittest`**: `Ran 13 tests ... OK (skipped=1)`; simulated output fidelity on the drifted device: trivial
0.8959, noise-aware 0.9878 (same ranking as ESP 0.2084 vs 0.7835).

**`python compile_qiskit.py`** — *pending CI*. Expected: level 3 ESP ≥ level 0 ESP on the same error map.

## Try it
```
other_drift  {'layout': [1, 2, 5, 0, 4], 'esp': 0.7503, 'cx': 13, 'depth': 18, 'uses_drifted_edge': False, 'noisy_fidelity': 0.9855}
tight_budget {'esp': 0.7835, 'cx': 19, 'depth': 21, 'within_budget': False}
```

## failureLab and build task — noise-aware layout
Fault: `choose_layout()` maps logical i → physical i and ignores today's drifted coupler.
Fix: search placements by ESP within the depth budget, reliable-path routing, CX cancellation (`my_layout.py`).
```bash
BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v        # your my_layout.py
BUILD_TASK_MODULE=compile_lab python -m unittest test_build_task test_fitness   # the shipped (unfixed) lab file: must fail
```
```powershell
$env:BUILD_TARGET = "mine"; python -m unittest test_build_task test_fitness -v; Remove-Item Env:BUILD_TARGET
```
Proof — observed locally on the shipped file:
```
FAIL: test_beats_the_trivial_layout_by_far (test_build_task.NoiseAwareLayout.test_beats_the_trivial_layout_by_far)
AssertionError: 0.5943 not greater than or equal to 0.75
FAIL: test_calibrated_device (test_fitness.CompiledCircuitFitness.test_calibrated_device)
AssertionError: 38 not less than or equal to 22
FAIL: test_drifted_device (test_fitness.CompiledCircuitFitness.test_drifted_device)
AssertionError: 50 not less than or equal to 22
Ran 5 tests in 0.656s
FAILED (failures=3)
```
Solution and `BUILD_TARGET=mine` with a correct file: `Ran 5 tests ... OK`.
