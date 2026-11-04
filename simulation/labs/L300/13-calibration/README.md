# 13 · Calibration: fit to data, validate on data you did not fit

An office cools down overnight; three models (one-exponential, two-exponential, degree-6 polynomial) are calibrated by least squares on 0-8 h and validated on 8-12 h.

Read the concept note first: `../../../content/concepts/L300/13-calibration.md`. Main lab: Python 3.12 + numpy only. The library equivalents need the L300 pins: `python -m pip install -r ../requirements.txt` (same command on macOS and Windows; adds SALib 1.6.0 and FMPy 0.3.32 to the L100 pins).

## Run
```bash
python calibrate.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L300\13-calibration` on Windows, `cd labs/L300/13-calibration` on macOS).

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux)
Seeded, identical on every run.
```
73 readings, 49 for calibration (0-8 h), 24 held out (8-12 h); sensor noise sd 0.15
  model           RMSE on calibration data   RMSE on holdout   prediction at 12 h (measured 13.33)
  one-exp (3 p)        0.175 C                  0.434 C         13.65 C
  two-exp (5 p)        0.152 C                  0.161 C         13.10 C
  poly-6 (7 p)         0.148 C                 12.517 C        -19.60 C
select() picks poly-6 (7 p); its holdout RMSE is 12.517 C
```

## Failure lab: break it, see it, fix it
- **Fault (seeded, shipped in `calibrate.py`):** `select()` scores every model on the 0-8 h data it was fitted to: the 7-parameter polynomial wins (0.148 C) but forecasts -19.60 C at 12 h (holdout RMSE 12.517 C). The table shows both columns, so you can see it.
- **Fix (your build task):** score on the unseen last 4 hours (time-ordered split): `select()` picks the two-exponential model, holdout RMSE 0.161 C (noise sd 0.15) (`solution/calibrate.py`).
- **Proof:** `test_build_task.py` - both tests FAIL with `BUILD_TARGET=mine` on the shipped file (11 failures counting the 10 seed subtests), both PASS on the solution (two-exp with < 0.2 C, never poly-6 for seeds 20-29). `TestFailureLab` in `test_calibrate.py` keeps the fault reproducible. `research/failure_proofs_L300.py`: shipped file FAIL, solution PASS.

## Test
```bash
python -m unittest -v
```
Observed: `Ran 11 tests ... OK (skipped=1)` - library tests are skipped locally (not installed) and run in CI.

## Try it
```bash
python try_it.py
```
Observed:
```
two-exp on 0-5 h: RMSE 0.170 C, T_inf=-71014 C, B=71029 C, tau_wall=326494 h
random holdout RMSE: one-exp (3 p) 0.257, two-exp (5 p) 0.189, poly-6 (7 p) 0.178 -> picks poly-6 (7 p)
```

## Build it (hardening task)
Fix `select()` in `calibrate.py` so it scores the candidates on the time-ordered holdout (8-12 h), not on the calibration window.

Hints:
- `scores(models, y, mask)` already computes RMSE on any mask; `CAL` is the calibration window.
- The holdout must be the END of the log: a random holdout still picks poly-6 (tryIt 2).

Check your file: `BUILD_TARGET=mine python -m unittest test_build_task -v` (PowerShell: `$env:BUILD_TARGET = "mine"`, then `python -m unittest test_build_task -v`). Shipped file: `Ran 2 tests ... FAILED (failures=11)`; after the fix: `OK`. Without the variable the test checks `solution/calibrate.py` (observed: `Ran 2 tests ... OK`).
Reference solution output (`python solution/calibrate.py`), only the last line changes:
```
73 readings, 49 for calibration (0-8 h), 24 held out (8-12 h); sensor noise sd 0.15
  model           RMSE on calibration data   RMSE on holdout   prediction at 12 h (measured 13.33)
  one-exp (3 p)        0.175 C                  0.434 C         13.65 C
  two-exp (5 p)        0.152 C                  0.161 C         13.10 C
  poly-6 (7 p)         0.148 C                 12.517 C        -19.60 C
select() picks two-exp (5 p); its holdout RMSE is 0.161 C
```

## Stretch (after the build task)
Add param_report(): standard errors and correlations from the Jacobian (cov = s^2 (J^T J)^-1) and a verdict 'identifiable' only if every relative standard error is below 50%.

Hints:
- gauss_newton() already returns J at the solution.
- s^2 = residual sum of squares / (n - k).
- Name the worst-correlated pair - it tells you what extra measurement would help.

Check: `python -m unittest test_stretch -v` (observed: `Ran 3 tests ... OK`). The reference solution is `solution/param_report.py`; to test your own `param_report.py` in this folder, set `BUILD_TARGET=mine` (PowerShell: `$env:BUILD_TARGET = "mine"`).
Reference solution output (`python solution/param_report.py`):
```
one-exp, 0-8 h           identifiable=True  worst corr ('T_inf', 'tau', -0.853)  rel. s.e. {'T_inf': 0.01, 'A': 0.01, 'tau': 0.03}
two-exp, 0-8 h           identifiable=False worst corr ('tau_wall', 'T_inf', -0.994)  rel. s.e. {'T_inf': 0.14, 'A': 0.72, 'tau_air': 0.42, 'B': 0.42, 'tau_wall': 1.38}
two-exp, T_inf=12 fixed  identifiable=True  worst corr ('tau_wall', 'B', -0.99)  rel. s.e. {'A': 0.11, 'tau_air': 0.12, 'B': 0.15, 'tau_wall': 0.17}
```

## Library equivalent (pending-ci)
`calibrate_scipy.py` repeats the fits with `scipy.optimize.least_squares(method='lm')`; `test_calibrate.py` requires the same one-exp parameters (rtol 1e-4). Skipped locally, runs in CI.

## Files
- `calibrate.py` - main lab code (ships the unfixed `select()`)
- `calibrate_scipy.py` - SciPy least_squares equivalent (pending-ci)
- `solution/calibrate.py` - buildTask solution (the fix)
- `solution/param_report.py` - stretch solution
- `try_it.py` - tryIt script
- `test_calibrate.py` - unit tests + fault reproduction
- `test_build_task.py` - buildTask check (`BUILD_TARGET=mine` checks your file)
- `test_stretch.py` - stretch check

