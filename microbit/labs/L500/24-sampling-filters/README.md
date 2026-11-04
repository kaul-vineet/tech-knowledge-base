# Lab L500 #24 — Foundations II: sampling and signal processing (theorem checks)

Numerical checks for the theorems in `content/L500.json` (lesson 24) and the concept note
`content/concepts/L500/24-sampling-filters.md`. Each `check_*` function returns `(ok, line)`; the lines are quoted verbatim
as `checkOutput` in the JSON, and `research/l500_checks.py` fails if they drift.

**What is checked:** Sinc reconstruction and aliasing (100 Hz flicker at 30 Hz through the stub light sensor), moving-average response and sqrt(N) noise reduction (stub accelerometer), exponential-filter step response, time constant and noise ratio (stub light sensor). Traces are SYNTHETIC and seeded.

**Validation status: validated-stub.** CPython 3.12.15 + numpy 2.5.3 on Linux, with `labs/sim_stub`. Nothing was
measured on a micro:bit; Mac/Windows runs are pending CI.

| File | Purpose |
|---|---|
| `foundations2.py` | The checks; `python foundations2.py` prints one line per theorem and exits 1 on any failure |
| `test_theory.py` | One unittest per check (run by `labs/run_tests.py`) |

## Run
```bash
cd labs/L500/24-sampling-filters
python3 -m pip install numpy==2.5.3    # once; Windows: py -m pip install numpy==2.5.3
python3 foundations2.py                   # Windows (PowerShell): py foundations2.py
python3 -m unittest -v
```

## Expected output (observed, Python 3.12.15, numpy 2.5.3, Linux sandbox)
```
OK   T1 sampling: W=4 Hz, fs=10 Hz, sinc reconstruction max error 0.0002 mid-record; 100 Hz sampled at 30 Hz equals 10 Hz to 8.2e-13; stub light FFT peak at 10.0 Hz (predicted |f - round(f/fs)fs| = 10 Hz)
OK   T2 moving average: N=16 closed-form |H| matches direct sum to 5.8e-16; stub accel z noise std ratio 3.98 (sqrt(N) = 4.00); N=3 at 30 Hz nulls 10 Hz: aliased flicker std 70.7 -> 0.00
OK   T3 EMA: alpha=0.2, Ts=0.1 s -> step error vs 1-(1-a)^(n+1) 2.2e-16, tau 0.448 s (Ts/alpha = 0.500 s), -3 dB at 0.3566 Hz; stub light noise variance ratio 0.1120 (alpha/(2-alpha) = 0.1111, same as N=9 MA)
```
```
test_check_ema (test_theory.TheoremChecks.test_check_ema) ... ok
test_check_moving_average (test_theory.TheoremChecks.test_check_moving_average) ... ok
test_check_sampling_theorem (test_theory.TheoremChecks.test_check_sampling_theorem) ... ok

----------------------------------------------------------------------
Ran 3 tests

OK
```
