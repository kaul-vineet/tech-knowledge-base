# 12 · Variance reduction: same precision, fewer runs

Expected overtime of a 12-task warehouse picking shift (exact answer known): antithetic variates, a control variate and common random numbers, each with its variance ratio measured.

Read the concept note first: `../../../content/concepts/L300/12-variance-reduction.md`. Main lab: Python 3.12 + numpy only. The library equivalents need the L300 pins: `python -m pip install -r ../requirements.txt` (same command on macOS and Windows; adds SALib 1.6.0 and FMPy 0.3.32 to the L100 pins).

## Run
```bash
python variance_reduction.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L300\12-variance-reduction` on Windows, `cd labs/L300/12-variance-reduction` on macOS).

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux)
Seeded, identical on every run.
```
exact expected overtime: 0.9196 h per shift (Erlang formula)
20,000 model evaluations per method:
  method              estimate   std.err   variance ratio vs plain
  plain Monte Carlo   0.9025    0.00990    1.00x
  antithetic          0.9208    0.00819    1.46x  rho=-0.32
  control variate     0.9203    0.00426    5.40x  beta=0.609
  antithetic (loop)   0.8999    0.00986    1.01x  rho=-0.00
CRN recap, overtime saved by a 7.5 h shift: independent 0.2120 +/- 0.0259, common 0.2237 +/- 0.0033 h
```

## Failure lab: break it, see it, fix it
- **Fault (seeded, shipped in `variance_reduction.py`):** `antithetic_loop()` - the loop version you write when a simulator is called once per run - creates a fresh stream for every evaluation, so the 'mirror' 1-u belongs to a different u: rho = -0.00, variance ratio 1.01x (no gain, and nothing crashes). The vectorised `antithetic()` above it still shows rho = -0.32, 1.46x.
- **Fix (your build task):** draw u once per pair from one stream and evaluate u and 1-u: rho = -0.33, ratio 1.50x (`solution/variance_reduction.py`).
- **Proof:** `test_build_task.py` - 2 of 3 tests FAIL with `BUILD_TARGET=mine` on the shipped file, 3 of 3 PASS on the solution. `TestFailureLab` in `test_variance_reduction.py` keeps the fault reproducible (rho ~ 0, ratio < 1.15). `research/failure_proofs_L300.py`: shipped file FAIL, solution PASS.

## Test
```bash
python -m unittest -v
```
Observed: `Ran 14 tests ... OK (skipped=1)` - library tests are skipped locally (not installed) and run in CI.

## Try it
```bash
python try_it.py
```
Observed:
```
symmetric model: rho=+1.00, variance ratio antithetic vs plain = 0.49x
control variate beta=0.609: variance ratio 5.40x
control variate beta=1.0: variance ratio 1.92x
control variate beta=1.5: variance ratio 0.52x
```

## Build it (hardening task)
Fix `antithetic_loop()` in `variance_reduction.py`: one stream per PAIR, and evaluate f(u) and f(1-u) from the same u.

Hints:
- Compare its rho with the vectorised `antithetic()`: they should agree.
- `np.random.default_rng([i, seed])` gives pair i its own reproducible stream.
- Keep analysing pair averages: the two halves of a pair are not independent.

Check your file: `BUILD_TARGET=mine python -m unittest test_build_task -v` (PowerShell: `$env:BUILD_TARGET = "mine"`, then `python -m unittest test_build_task -v`). Shipped file: `Ran 3 tests ... FAILED (failures=2)`; after the fix: `OK`. Without the variable the test checks `solution/variance_reduction.py` (observed: `Ran 3 tests ... OK`).
Reference solution output (`python solution/variance_reduction.py`), only the loop row changes:
```
exact expected overtime: 0.9196 h per shift (Erlang formula)
20,000 model evaluations per method:
  method              estimate   std.err   variance ratio vs plain
  plain Monte Carlo   0.9025    0.00990    1.00x
  antithetic          0.9208    0.00819    1.46x  rho=-0.32
  control variate     0.9203    0.00426    5.40x  beta=0.609
  antithetic (loop)   0.9091    0.00809    1.50x  rho=-0.33
CRN recap, overtime saved by a 7.5 h shift: independent 0.2120 +/- 0.0259, common 0.2237 +/- 0.0033 h
```

## Stretch (after the build task)
Add pick_estimator(): a 2,000-run pilot measures the pair correlation and the control-variate gain, refuses antithetic sampling when rho >= 0, picks the best method and logs the decision as one JSON line.

Hints:
- Owen 8.2: Var(anti) = sigma^2 (1 + rho) / n - rho >= 0 means no gain or a loss.
- Compare per-evaluation variances so the methods are judged at equal cost.
- Return the evidence (rho, ratios) with the decision.

Check: `python -m unittest test_stretch -v` (observed: `Ran 4 tests ... OK`). The reference solution is `solution/pick_estimator.py`; to test your own `pick_estimator.py` in this folder, set `BUILD_TARGET=mine` (PowerShell: `$env:BUILD_TARGET = "mine"`).
Reference solution output (`python solution/pick_estimator.py`):
```
{"event": "estimator_choice", "pilot": 2000, "rho": -0.332, "ratios": {"plain": 1.0, "antithetic": 1.62, "control variate": 5.47}, "method": "control variate"}
{"event": "estimator_choice", "pilot": 2000, "rho": 1.0, "ratios": {"plain": 1.0}, "method": "plain"}
{"event": "estimator_choice", "pilot": 2000, "rho": -0.935, "ratios": {"plain": 1.0, "antithetic": 15.17}, "method": "antithetic"}
```

## Library equivalent (pending-ci)
`test_variance_reduction.py` checks `exact_overtime()` against SciPy (`stats.gamma` + `integrate.quad`); skipped locally, runs in CI.

## Files
- `variance_reduction.py` - main lab code (ships the unfixed `antithetic_loop()`)
- `solution/variance_reduction.py` - buildTask solution (the fix)
- `solution/pick_estimator.py` - stretch solution
- `try_it.py` - tryIt script
- `test_variance_reduction.py` - unit tests + fault reproduction
- `test_build_task.py` - buildTask check (`BUILD_TARGET=mine` checks your file)
- `test_stretch.py` - stretch check

