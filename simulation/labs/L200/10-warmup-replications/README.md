# 10 · Warm-up, replications and confidence

Help desk opening with a 30-ticket backlog: Welch's method proposes a warm-up, deletion removes the bias, replications give a CI that shrinks like 1/sqrt(n).

Read the concept note first: `../../../content/concepts/L200/10-warmup-replications.md`. No new packages: the L100 pins (`labs/L100/01-setup-workbench/requirements.txt`) already include numpy, SciPy and SimPy.

## Run
```bash
python warmup.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L200\10-warmup-replications` on Windows, `cd labs/L200/10-warmup-replications` on macOS).

## Expected output (real run, Python 3.12.15, Linux; seeded, identical on every run)
```
1. Welch: 20 replications x 5,000 customers, window 50. Moving average at customer:
   0: 29.19  50: 16.24  100: 8.69  150: 5.34  200: 3.39  500: 3.95  2000: 3.62  4000: 3.15
   code proposes warm-up = 169 customers (enters 5% band around level 4.32)
2. 40 runs x 1,000 customers, delete first   0: 5.59 +/- 0.61 min (true 4.0)
2. 40 runs x 1,000 customers, delete first 169: 3.71 +/- 0.53 min (true 4.0)
3. replications of 5,000 customers, warm-up deleted: 95% CI
   n=10: 3.89 +/- 0.50 min  (half-width x sqrt(n) = 1.58)
   n=20: 4.00 +/- 0.31 min  (half-width x sqrt(n) = 1.40)
   n=40: 4.18 +/- 0.25 min  (half-width x sqrt(n) = 1.59)
   n=80: 4.01 +/- 0.16 min  (half-width x sqrt(n) = 1.43)
```

## Test
```bash
python -m unittest -v
```
Observed: `Ran 10 tests ... OK (skipped=1)` - library tests are skipped locally (not installed) and run in CI.

## Try it
```bash
python try_it.py
```
Observed:
```
backlog 30, no deletion: 5.59 +/- 0.61 min (true 4.0)
backlog  0, no deletion: 3.57 +/- 0.43 min (true 4.0)
proposed warm-up for three new seed sets: [215, 195, 961]
80 replications, delete first 169: 4.01 +/- 0.16 min
80 replications, delete first 961: 3.98 +/- 0.17 min
```

## Build it (your task)
Add reps_for_precision(rel=0.05): start with 10 replications and add one at a time until the CI half-width is within rel of the mean (relative-error rule).

Hints:
- Stop when half / |mean| <= rel / (1 + rel) (Currie & Cheng 5.2).
- Reuse waits(..)[warmup:].mean() and ci().
- Cap the loop with max_reps.

Check: `python -m unittest test_build_task -v` (observed: `Ran 3 tests ... OK`). The reference solution is `solution/sequential_reps.py`; to test your own version, change the import at the top of `test_build_task.py`.
Reference solution output (`python solution/sequential_reps.py`):
```
stopped after 64 replications: 4.04 +/- 0.19 min (4.7% of the mean)
```

## Library check (pending-ci)
`test_warmup.py` compares `t975()` with `scipy.stats.t.ppf(0.975, df)`; skipped locally, runs in CI.

## Learning tools (optional)
Write 40 per-replication mean waits for two scenarios as CSV for Orange's Box Plot or JupyterLab (see `../../../documentation/LEARNING-TOOLS.md`):
```bash
python export_csv.py
```
Observed:
```
wrote 80 rows to replications.csv
  delete 0: mean of 40 replication means 5.59 min (true 4.0)
delete 169: mean of 40 replication means 3.71 min (true 4.0)
```
Test: `python -m unittest test_export_csv -v` (observed: `Ran 1 test ... OK`).

## Files
- `warmup.py` - main lab code
- `export_csv.py` - writes `replications.csv` for the learning tools (+ `test_export_csv.py`)
- `solution/sequential_reps.py` - buildTask solution
- `try_it.py` - tryIt script
- `test_*.py` - unit tests (`test_build_task.py` checks the buildTask)
