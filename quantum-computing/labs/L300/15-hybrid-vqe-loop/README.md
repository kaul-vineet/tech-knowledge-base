# Lab 15 — A hybrid variational loop (VQE) with shot noise and JSON-lines logs

VQE for a toy 2-qubit "H2-like" Pauli sum. The estimator measures two groups (Z basis: II, ZI, IZ, ZZ; X basis: XX) with a fixed number of shots. Every iteration is logged as one JSON line in `logs/`. A finite-difference optimizer converges perfectly on the exact simulator, then diverges once shot noise appears. SPSA fixes it. An optional agent reads the log and proposes settings; code checks every claim.

## Run
```bash
python vqe_lab.py
python try_it.py
python solution_spsa.py
python agent_assist.py --fake
python -m unittest -v
python vqe_qiskit.py         # SDK path: Qiskit primitives + scipy COBYLA (needs ../requirements.txt; CI)
```

## Expected output

**`python vqe_lab.py`** — observed locally (Python 3.12.15, numpy 2.5.3):
```
exact ground energy E0 = -1.8405
{"optimizer": "gd", "shots": null, "error": 0.0, "log": "vqe_gd_exact.jsonl", "iters": 100, "best_energy_est": -1.84046, "final_energy_est": -1.84046, "evals": 900, "tail_energy_std": 0.0001, "tail_grad_norm_median": 0.007}
{"optimizer": "gd", "shots": 1000, "error": 1.5645, "log": "vqe_gd_1000.jsonl", "iters": 100, "best_energy_est": -1.77348, "final_energy_est": -0.27276, "evals": 900, "tail_energy_std": 0.3912, "tail_grad_norm_median": 15.5125}
```
First lines of `logs/vqe_gd_1000.jsonl` (observed):
```
{"optimizer": "gd", "shots": 1000, "iter": 0, "energy_est": -1.03512, "grad_norm": 9.907, "evals": 9}
{"optimizer": "gd", "shots": 1000, "iter": 1, "energy_est": -1.5862, "grad_norm": 26.537, "evals": 18}
{"optimizer": "gd", "shots": 1000, "iter": 2, "energy_est": -1.23532, "grad_norm": 8.852, "evals": 27}
```
Read the log on macOS: `python -c "import json,pathlib;[print(json.loads(l)['grad_norm']) for l in pathlib.Path('logs/vqe_gd_1000.jsonl').read_text(encoding='utf-8').splitlines()[-5:]]"` (same command in PowerShell).

**`python vqe_qiskit.py`** — *pending CI*. Expected: exact energy at t = 0.1 equal to numpy (-1.04384); COBYLA and SPSA at 4000 shots both end with error < 0.05; logs in `logs/vqe_qiskit_*.jsonl`.

**`python -m unittest`** — observed locally without SDKs: `Ran 17 tests ... OK (skipped=3)` (includes try-it, build-task and agent-assist tests).

## Try it
**`python try_it.py`** — observed locally:
```
more_shots_same_optimizer {1000: {'error': 1.5645, 'total_shots': 1800000}, 100000: {'error': 0.9195, 'total_shots': 180000000}, 1000000: {'error': 0.0076, 'total_shots': 1800000000}}
spsa_cost (for comparison) {'error': 0.0064, 'total_shots': 900000}
below_the_ground_energy   {'E0': -1.8405, 'best_energy_est': -1.84964, 'rows_below_E0': 8, 'rows': 150}
```

## failureLab and build task — SPSA
Fault: shot noise (1000 shots per group, seeded) under a finite-difference gradient with h = 1e-3. Symptom: error 1.5645, tail gradient-norm median 15.5 in the log. Fix: `vqe()` uses SPSA (a = 1.0, c = 0.2, A = 10, α = 0.602, γ = 0.101, 150 iterations).

Reference **`python solution_spsa.py`** — observed locally:
```
{"optimizer": "spsa", "shots": 1000, "error": 0.0064, "log": "vqe_spsa_1000.jsonl", "iters": 150, "best_energy_est": -1.84964, "final_energy_est": -1.8256, "evals": 450, "tail_energy_std": 0.0065, "tail_grad_norm_median": null}
errors over seeds 0-5: [0.0064, 0.0154, 0.0123, 0.0033, 0.0114, 0.0188]
```
Proof — observed locally:
```
$ BUILD_TASK_MODULE=vqe_lab python -m unittest test_build_task      # finite differences
FAIL: test_converges_under_shot_noise ... AssertionError: 1.5645 not less than 0.03 : seed 0
FAILED (failures=1)
$ python -m unittest test_build_task                               # solution_spsa
Ran 2 tests ... OK
```

## Agent assist — the model reads the log, code decides
The model gets the log summary plus the last 5 lines and returns `{"diagnosis", "best_energy", "proposal"}`. Code checks the number against the log, compares the diagnosis with its own rule, checks setting ranges and the shot budget (2,000,000), then **runs** the proposal (seeded) and accepts only if the error is < 0.03.

**`python agent_assist.py --fake`** — observed locally (deterministic fake server, `fake_vqe_rule.py`):
```
diagnose ACCEPT  code ran spsa @ 1000 shots: error 0.0064
report   REJECT  best_energy -1.8405 is not in the log (log min -1.77348); diagnosis 'learning_rate_too_high' != code rule 'shot_noise'; code ran gd @ 1000 shots: error 0.7429
costly   REJECT  proposal needs 1,800,000,000 shots > budget 2,000,000 (not run)
```
With a real model: `python agent_assist.py --show` (Ollama at `http://localhost:11434/v1`; set `LOCAL_MODEL`). Not run here.
