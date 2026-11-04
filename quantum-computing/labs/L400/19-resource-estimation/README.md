# Lab 19 — Resource estimation: logical vs physical qubits and feasibility

Logical counts for QAOA (validated against counted circuits) and Shor/RSA (Gidney & Ekerå formulas), a surface-code
model p_L(d) = 0.03 (p/0.01)^((d+1)/2) with ≈2d² physical qubits per logical qubit (data blocks only — a lower bound),
and a feasibility class per workload. Assumptions: p = 1e-3, 1 µs cycles, 1 % failure budget. Decision:
`docs/adr/0001-feasibility-gate.md`.

## Run
```bash
python estimate_lab.py        # shipped: fixed distance d = 3
python solution_distance.py   # distance from the error budget
python try_it.py
python -m unittest -v
python count_qiskit.py        # Qiskit counts (CI)
python estimate_qdk.py        # QDK qdk.qre estimator, separate venv: ../requirements-qdk.txt (CI job l400-qdk)
```

## Expected output
**`python estimate_lab.py`** — observed locally (Python 3.12.15, numpy 2.5.3, cryptography 50.0.2; Linux sandbox, no quantum SDKs):
```
{"workload": "qaoa n=20 p=1", "logical_qubits": 20, "cx": 60, "rotations": 50, "depth": 14, "t_count": 2350, "logical_cycles": 249, "distance": 3, "physical_qubits": 360, "runtime_s": 0.000747, "p_fail": 1.0, "class": "simulate"}
{"workload": "qaoa n=100 p=1", "logical_qubits": 100, "cx": 300, "rotations": 250, "depth": 14, "t_count": 13500, "logical_cycles": 284, "distance": 3, "physical_qubits": 1800, "runtime_s": 0.000852, "p_fail": 1.0, "class": "nisq-candidate"}
{"workload": "qaoa n=100 p=4", "logical_qubits": 100, "cx": 1200, "rotations": 1000, "depth": 53, "t_count": 60000, "logical_cycles": 1253, "distance": 3, "physical_qubits": 1800, "runtime_s": 0.003759, "p_fail": 1.0, "class": "fault-tolerant-feasible"}
{"workload": "qaoa n=1000 p=10", "logical_qubits": 1000, "cx": 30000, "rotations": 25000, "depth": 131, "t_count": 1850000, "logical_cycles": 3831, "distance": 3, "physical_qubits": 18000, "runtime_s": 0.01149, "p_fail": 1.0, "class": "fault-tolerant-feasible"}
{"workload": "rsa-1024", "logical_qubits": 3093, "toffoli": 327491256, "t_count": 2292438792, "depth": 534773760, "logical_cycles": 534773760, "distance": 3, "physical_qubits": 55674, "runtime_s": 1604.0, "p_fail": 1.0, "class": "fault-tolerant-feasible"}
{"workload": "rsa-2048", "logical_qubits": 6190, "toffoli": 2624225018, "t_count": 18369575126, "depth": 2143289344, "logical_cycles": 2143289344, "distance": 3, "physical_qubits": 111420, "runtime_s": 6430.0, "p_fail": 1.0, "class": "fault-tolerant-feasible"}
```
**`python solution_distance.py`**:
```
{"workload": "qaoa n=20 p=1", "logical_qubits": 20, "t_count": 2350, "logical_cycles": 249, "distance": 9, "physical_qubits": 3240, "runtime_s": 0.002241, "p_fail": 0.00149, "class": "simulate"}
{"workload": "qaoa n=100 p=1", "logical_qubits": 100, "t_count": 13500, "logical_cycles": 284, "distance": 9, "physical_qubits": 16200, "runtime_s": 0.002556, "p_fail": 0.00852, "class": "nisq-candidate"}
{"workload": "qaoa n=100 p=4", "logical_qubits": 100, "t_count": 60000, "logical_cycles": 1253, "distance": 11, "physical_qubits": 24200, "runtime_s": 0.01378, "p_fail": 0.00376, "class": "fault-tolerant-feasible"}
{"workload": "qaoa n=1000 p=10", "logical_qubits": 1000, "t_count": 1850000, "logical_cycles": 3831, "distance": 15, "physical_qubits": 450000, "runtime_s": 0.05746, "p_fail": 0.00115, "class": "fault-tolerant-feasible"}
{"workload": "rsa-1024", "logical_qubits": 3093, "t_count": 2292438792, "logical_cycles": 534773760, "distance": 25, "physical_qubits": 3866250, "runtime_s": 13370.0, "p_fail": 0.00496, "class": "infeasible (assumptions above)"}
{"workload": "rsa-2048", "logical_qubits": 6190, "t_count": 18369575126, "logical_cycles": 2143289344, "distance": 27, "physical_qubits": 9025020, "runtime_s": 57870.0, "p_fail": 0.00398, "class": "infeasible (assumptions above)"}
```
**`python -m unittest`**: `Ran 17 tests ... OK (skipped=2)` (Qiskit and QDK tests run in CI).

**`python estimate_qdk.py`** — *pending CI*. Expected: QDK's minimum physical qubits for QAOA n = 20, p = 1 at or above
our data-only 3240 (it adds magic-state factories), within 0.3–30×. **`python count_qiskit.py`** — *pending CI*: Qiskit
CX count and depth equal the counted circuit (n = 10, p = 2: 60 CX, depth 27).

## Try it
```
better_hardware {'distance': 13, 'physical_qubits': 2092220, 'runtime_s': 27860.0}
near_threshold  {0.001: (11, 24200), 0.005: (37, 273800), 0.009: 'no distance <= 101 meets budget 0.01', 0.011: 'physical error 0.011 is not below the threshold 0.01'}
```

## failureLab and build task — distance from the error budget
Fault: `choose_distance()` returns 3 for everything; RSA-2048 is called fault-tolerant-feasible with p_fail 1.0.
Fix: smallest odd d meeting the budget, `ValueError` at or above the 1 % threshold (`my_distance.py`).
```bash
BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v        # your my_distance.py
BUILD_TASK_MODULE=estimate_lab python -m unittest test_build_task test_fitness   # the shipped (unfixed) lab file: must fail
```
```powershell
$env:BUILD_TARGET = "mine"; python -m unittest test_build_task test_fitness -v; Remove-Item Env:BUILD_TARGET
```
Proof — observed locally on the shipped file:
```
FAIL: test_meets_the_budget_and_is_minimal (test_build_task.Distance.test_meets_the_budget_and_is_minimal)
AssertionError: 37.59 not less than or equal to 0.01
FAIL: test_refuses_above_threshold (test_build_task.Distance.test_refuses_above_threshold)
AssertionError: ValueError not raised
FAIL: test_rsa_2048_needs_distance_27 (test_build_task.Distance.test_rsa_2048_needs_distance_27)
AssertionError: 3 != 27
FAIL: test_decision_table (test_fitness.FeasibilityFitness.test_decision_table)
AssertionError: Lists differ: ['sim[76 chars]e', 'fault-tolerant-feasible', 'fault-tolerant-feasible'] != ['sim[76 chars]e', 'infeasible (assumptions above)', 'infeasi[20 chars]ve)']
FAIL: test_every_estimate_meets_the_error_budget (test_fitness.FeasibilityFitness.test_every_estimate_meets_the_error_budget)
AssertionError: False is not true : [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
Ran 7 tests in 0.470s
FAILED (failures=5)
```
Solution and `BUILD_TARGET=mine` with a correct file: `Ran 7 tests ... OK`.
