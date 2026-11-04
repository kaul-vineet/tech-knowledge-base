# Lab 13 — Error mitigation

Readout-error mitigation (calibration matrix and its inverse) and zero-noise extrapolation (fold every CX into CX·CX·CX, extrapolate to zero noise). Then watch the plain inverse return *negative probabilities* that crash downstream code, and fix it with constrained least squares plus a sensible shot budget.

## Run
```bash
python mitigation_lab.py
python try_it.py
python solution_constrained.py
python -m unittest -v
python mitiq_zne.py          # SDK path: Mitiq 1.1.0 + Cirq (needs ../requirements-extras.txt; CI job l300-extras)
```

## Expected output

**`python mitigation_lab.py`** — observed locally (Python 3.12.15, numpy 2.5.3):
```
{"cal_shots": 4000, "shots": 4000, "raw": [0.4768, 0.0422, 0.0398, 0.4412], "mitigated": [0.5038, 0.0003, -0.0105, 0.5064], "min": -0.0105, "tvd_raw": 0.082, "tvd_mitigated": 0.0105}
  downstream sampling failed: Probabilities are not non-negative
{"cal_shots": 100, "shots": 200, "raw": [0.46, 0.04, 0.04, 0.46], "mitigated": [0.5072, -0.0241, -0.0126, 0.5294], "min": -0.0241, "tvd_raw": 0.08, "tvd_mitigated": 0.0367}
  downstream sampling failed: Probabilities are not non-negative
{"scale": 1, "cx_count": 4, "P000": 0.9039}
{"scale": 3, "cx_count": 12, "P000": 0.7474}
{"scale": 5, "cx_count": 20, "P000": 0.6234}
ideal 1.0 | raw 0.9039 | linear ZNE 0.9687 | Richardson ZNE 0.9944
```

**`python mitiq_zne.py`** — *pending CI*. Expected: raw P(000) 0.9039 (numpy 0.9039), Richardson [1,3,5] ≈ 0.9944, linear ≈ 0.9687, REM inverse check `True` (Cirq's simulator is float32: agreement to ~1e-4).

**`python -m unittest`** — observed locally without Mitiq: `Ran 12 tests ... OK (skipped=1)`.

## Try it
**`python try_it.py`** — observed locally:
```
zne_shot_noise       {'raw_mean': 0.9041, 'raw_std': 0.0069, 'richardson_mean': 0.9942, 'richardson_std': 0.017}
clip_vs_constrained  {'clip': 0.0436, 'constrained': 0.0426}
```

## failureLab and build task — constrained readout mitigation
Fault: too few calibration/run shots (seeded). Symptom: quasi-probabilities down to −0.0241 and `numpy.random.choice` raises. Fix: `mitigate()` solves min ‖M·p − p_noisy‖ subject to p ≥ 0, Σp = 1 (projected gradient on the simplex), and calibration and runs use at least 4000 shots each.

Reference **`python solution_constrained.py`** — observed locally:
```
cal 4000/run 4000: [0.4991, 0.0, 0.0, 0.5009] min 0.0000 sampling ok: True
cal 100/run 200: [0.4779, 0.0182, 0.0429, 0.4609] min 0.0182 sampling ok: True
mean TVD over 200 seeds, cal 100/run 200: raw-inverse 0.055 constrained 0.0426
mean TVD over 200 seeds, cal 4000/run 4000: raw-inverse 0.0107 constrained 0.008
```
Proof — observed locally:
```
$ BUILD_TASK_MODULE=mitigation_lab python -m unittest test_build_task     # plain inverse
FAIL: test_always_a_probability_distribution ... AssertionError: np.float64(-0.008180304680361005) not greater than or equal to 0.0 : (100, 200)
FAILED (failures=1)
$ python -m unittest test_build_task                                      # solution_constrained
Ran 3 tests ... OK
```
