# 02 · Monte Carlo: estimate a project's completion time

Sample three uncertain task durations up to 100,000 times; report mean, 95% CI and P(done in 20 days).

Read the concept note first: `../../../content/concepts/02-monte-carlo-estimation.md`.

## Run
```bash
python monte_carlo.py
```

## Expected output (real run, Python 3.12.15, Linux, numpy 2.5.3; seeded, identical on every run)
```
exact mean (from formula): 17.333 days
       N    mean   95% CI half-width   P(<= 20 days)
     100  17.196   +/- 0.436            0.890
    1000  17.376   +/- 0.150            0.849
   10000  17.346   +/- 0.047            0.855
  100000  17.334   +/- 0.015            0.857
P50 / P90 completion (days): [17.23 20.56]
```

## Test
```bash
python -m unittest -v
```
Observed: `Ran 5 tests ... OK`.

## Try it
```bash
python try_it.py
```
Observed:
```
seed 42: N=100 mean 17.196 | N=100000 mean 17.334 +/- 0.015
seed 7: N=100 mean 17.401 | N=100000 mean 17.338 +/- 0.015
build max 20 d: mean 19.332 +/- 0.022, P(<= 20 days) 0.602
pi estimate (N=100000): 3.1501 +/- 0.0101
```

## Learning tools (optional)
Write the lab's 100,000 seeded totals as CSV for KNIME or marimo (see `../../../documentation/LEARNING-TOOLS.md`):
```bash
python export_csv.py
```
Observed:
```
wrote 100000 rows to mc_totals.csv
P50 / P90 completion (days): [17.23 20.56]
```
Test: `python -m unittest test_export_csv -v` (observed: `Ran 2 tests ... OK`).

## Files
- `monte_carlo.py` - main lab code
- `export_csv.py` - writes `mc_totals.csv` for the learning tools (+ `test_export_csv.py`)
- `test_monte_carlo.py` - seeding, bounds, CI checks
- `try_it.py` - tryIt script (+ pi bonus)
