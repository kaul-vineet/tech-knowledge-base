# 11 · A supply-chain model: (s, S) inventory with common random numbers

Bike shop reorders inner tubes with an (s, S) policy under random weekly demand and 1-4 day lead times; cost trade-offs and common random numbers for a fair comparison.

Read the concept note first: `../../../content/concepts/L200/11-supply-chain-inventory.md`. No new packages: the L100 pins (`labs/L100/01-setup-workbench/requirements.txt`) already include numpy, SciPy and SimPy.

## Run
```bash
python inventory.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L200\11-supply-chain-inventory` on Windows, `cd labs/L200/11-supply-chain-inventory` on macOS).

## Expected output (real run, Python 3.12.15, Linux; seeded, identical on every run)
```
(s, S) policies over 365 days, 30 replications: mean cost per day +/- 95% CI
  s=20 S=80:   8.71 +/- 0.30  orders/yr  40.6  lost tubes/yr  217.9
  s=30 S=80:   8.56 +/- 0.27  orders/yr  50.3  lost tubes/yr  111.3
  s=30 S=90:   8.30 +/- 0.22  orders/yr  42.7  lost tubes/yr   89.9
difference S=90 minus S=80, independent: +0.03 +/- 0.44 -> cannot tell
difference S=90 minus S=80, CRN        : -0.25 +/- 0.12 -> S=90 is cheaper
```

## Test
```bash
python -m unittest -v
```
Observed: `Ran 9 tests ... OK (skipped=1)` - library tests are skipped locally (not installed) and run in CI.

## Try it
```bash
python try_it.py
```
Observed:
```
same seeds, ONE shared stream: S=90 minus S=80 = -0.19 +/- 0.31
same seeds, one stream per purpose (lab): -0.25 +/- 0.12
lost sale costs 2.00: S=90 minus S=80 = -0.13 +/- 0.08 per day
```

## Build it (your task)
Add the fill rate (units served from stock / units demanded) to the results and compare it between S=80 and S=90 with CRN.

Hints:
- fill_rate = 1 - lost / total demand.
- Use the same streams(rep) for both policies.
- Report one CI of the per-replication difference.

Check: `python -m unittest test_build_task -v` (observed: `Ran 3 tests ... OK`). The reference solution is `solution/fill_rate.py`; to test your own version, change the import at the top of `test_build_task.py`.
Reference solution output (`python solution/fill_rate.py`):
```
s=20 S=80: fill rate 0.925 +/- 0.008
s=30 S=80: fill rate 0.962 +/- 0.006
s=30 S=90: fill rate 0.970 +/- 0.006
fill rate S=90 minus S=80 (CRN): +0.0073 +/- 0.0043
```

## Library equivalent (pending-ci)
`simpy_inventory.py` does the same with SimPy 4.1.2 `Container`. It is not installed in the offline sandbox, so it has **not been run yet**; the CI workflow installs the pinned version and runs it plus the un-skipped test.

## Files
- `inventory.py` - main lab code
- `simpy_inventory.py` - SimPy 4.1.2 Container equivalent (pending-ci)
- `solution/fill_rate.py` - buildTask solution
- `try_it.py` - tryIt script
- `test_*.py` - unit tests (`test_build_task.py` checks the buildTask)
