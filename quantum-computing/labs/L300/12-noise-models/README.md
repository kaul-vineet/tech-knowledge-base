# Lab 12 — Noise models

Run a Bell pair and GHZ states through a seeded noise model (depolarizing, amplitude damping, readout flips) on a numpy density-matrix simulator. Watch fidelity and success fall with noise level and size. Then see the L100-style check "only 00 and 11 may appear" fail on a *correct* circuit, and harden it.

## Run
```bash
python noise_lab.py
python try_it.py
python solution_tolerant_check.py
python -m unittest -v
python noise_aer.py          # SDK path: Qiskit Aer NoiseModel (needs ../requirements.txt; CI)
```

## Expected output

**`python noise_lab.py`** — observed locally (Python 3.12.15, numpy 2.5.3). One JSON line per (n, p2):
```
ideal Bell counts: {'00': 998, '11': 1002}
noisy Bell counts: {'00': 962, '01': 82, '10': 70, '11': 886}
{"n": 2, "p2": 0.0, "fidelity": 0.9866, "success": 0.9337, "p_all0": 0.4862, "p_all1": 0.4475}
{"n": 2, "p2": 0.01, "fidelity": 0.9793, "success": 0.9294, "p_all0": 0.484, "p_all1": 0.4454}
{"n": 2, "p2": 0.02, "fidelity": 0.9719, "success": 0.925, "p_all0": 0.4818, "p_all1": 0.4433}
{"n": 2, "p2": 0.05, "fidelity": 0.9498, "success": 0.912, "p_all0": 0.4751, "p_all1": 0.4369}
{"n": 2, "p2": 0.1, "fidelity": 0.913, "success": 0.8904, "p_all0": 0.4641, "p_all1": 0.4263}
{"n": 3, "p2": 0.0, "fidelity": 0.9769, "success": 0.8966, "p_all0": 0.4756, "p_all1": 0.421}
{"n": 3, "p2": 0.01, "fidelity": 0.9612, "success": 0.8858, "p_all0": 0.47, "p_all1": 0.4159}
{"n": 3, "p2": 0.02, "fidelity": 0.9456, "success": 0.8752, "p_all0": 0.4644, "p_all1": 0.4108}
{"n": 3, "p2": 0.05, "fidelity": 0.8997, "success": 0.8439, "p_all0": 0.448, "p_all1": 0.3959}
{"n": 3, "p2": 0.1, "fidelity": 0.8261, "success": 0.7934, "p_all0": 0.4215, "p_all1": 0.3719}
{"n": 4, "p2": 0.0, "fidelity": 0.9673, "success": 0.8622, "p_all0": 0.466, "p_all1": 0.3962}
{"n": 4, "p2": 0.01, "fidelity": 0.9434, "success": 0.8456, "p_all0": 0.4572, "p_all1": 0.3885}
{"n": 4, "p2": 0.02, "fidelity": 0.92, "success": 0.8293, "p_all0": 0.4484, "p_all1": 0.3809}
{"n": 4, "p2": 0.05, "fidelity": 0.8521, "success": 0.7818, "p_all0": 0.4229, "p_all1": 0.3588}
{"n": 4, "p2": 0.1, "fidelity": 0.7473, "success": 0.7073, "p_all0": 0.383, "p_all1": 0.3242}
naive bell_check on ideal counts: True
naive bell_check on noisy counts: False <- the fault: a correct circuit fails
```
Read it: fidelity < 1 even at p2 = 0 (p1, damping); success < fidelity (readout); P(all 0) > P(all 1) (damping and p10 > p01).

**`python noise_aer.py`** — *pending CI*. Expected: Aer success within ±0.02 of the numpy column for every line (same channels, Aer's own RNG).

**`python -m unittest`** — observed locally without SDKs: `Ran 15 tests ... OK (skipped=3)`.

## Try it
**`python try_it.py`** — observed locally:
```
symmetric_noise       {'p_all0': 0.4454, 'p_all1': 0.4454}
readout_vs_gate_noise {'readout_only': 0.8145, 'cx_only': 0.9037}
```

## failureLab and build task — a noise-aware check
Fault: the seeded `NOISE` model. Symptom: `bell_check` (only `00`/`11` allowed) is False for a correct Bell pair. Fix: compare observed success with the model's prediction minus 4 binomial standard errors **and** check the all-1 share, so a missing H or CX still fails.

Reference **`python solution_tolerant_check.py`** — observed locally:
```
noisy Bell counts: {'00': 962, '01': 82, '10': 70, '11': 886} -> tolerant check: True
ideal Bell counts -> tolerant check: True
GHZ-3, 200 seeds on the noisy model: 200/200 pass
```
Proof (fails before, passes after) — observed locally:
```
$ BUILD_TASK_MODULE=noise_lab python -m unittest test_build_task      # naive check
FAIL: test_correct_circuit_passes_on_noisy_device ... AssertionError: False is not true : n=2 seed=0
FAILED (failures=1)
$ python -m unittest test_build_task                                   # solution_tolerant_check
Ran 5 tests ... OK
```
Windows: `$env:BUILD_TASK_MODULE = "noise_lab"; python -m unittest test_build_task` (then `Remove-Item Env:BUILD_TASK_MODULE`).
