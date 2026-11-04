# 08 · Resources and queues: c desks, one line, Erlang C

Clinic reception: 3 desks, one shared line, heapq event list; time-weighted Lq and utilisation checked against Erlang C; SimPy Resource in CI.

Read the concept note first: `../../../content/concepts/L200/08-multi-server-queue.md`. No new packages: the L100 pins (`labs/L100/01-setup-workbench/requirements.txt`) already include numpy, SciPy and SimPy.

## Run
```bash
python mmc_queue.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L200\08-multi-server-queue` on Windows, `cd labs/L200/08-multi-server-queue` on macOS).

## Expected output (real run, Python 3.12.15, Linux; seeded, identical on every run)
```
M/M/3: lam=2.4/min, mu=1.0/min per desk, utilisation 80%
metric    simulated   Erlang C
Wq            1.110      1.079
Lq            2.665      2.589
util          0.803      0.800
P_wait        0.652      0.647
desks needed so that P(wait) < 20%:
  c=3: P(wait)=0.647  Wq=1.079 min
  c=4: P(wait)=0.287  Wq=0.179 min
  c=5: P(wait)=0.114  Wq=0.044 min
  c=6: P(wait)=0.040  Wq=0.011 min
```

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
3 separate lines: Wq=3.87 min | 1 shared line, 3 desks: Wq=1.11 min | formula 4.00 vs 1.08
lam=2.4: utilisation 80%, simulated Wq=1.11 min, Erlang C Wq=1.08 min
lam=2.64: utilisation 88%, simulated Wq=2.30 min, Erlang C Wq=2.17 min
```

## Build it (your task)
Add a waiting-room limit max_queue: arrivals that find max_queue people in line leave and are counted as blocked. max_queue=0 must reproduce Erlang B.

Hints:
- Check the limit only when all desks are busy.
- Return blocked / n_customers in the result dict.
- Erlang B recursion: B = a*B / (k + a*B) for k = 1..c.

Check: `python -m unittest test_build_task -v` (observed: `Ran 3 tests ... OK`). The reference solution is `solution/mmc_capacity.py`; to test your own version, change the import at the top of `test_build_task.py`.
Reference solution output (`python solution/mmc_capacity.py`):
```
max_queue=None: blocked 0.000  Wq 1.110 min  util 0.803
max_queue=5: blocked 0.051  Wq 0.480 min  util 0.764
max_queue=0: blocked 0.269  Wq 0.000 min  util 0.585
Erlang B (max_queue=0): 0.268
```

## Library equivalent (pending-ci)
`simpy_mmc.py` does the same with SimPy 4.1.2 `Resource`. It is not installed in the offline sandbox, so it has **not been run yet**; the CI workflow installs the pinned version and runs it plus the un-skipped test.

## Files
- `mmc_queue.py` - main lab code
- `simpy_mmc.py` - SimPy 4.1.2 Resource equivalent (pending-ci)
- `solution/mmc_capacity.py` - buildTask solution
- `try_it.py` - tryIt script
- `test_*.py` - unit tests (`test_build_task.py` checks the buildTask)
