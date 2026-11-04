# 07 · Input modelling: fit service times and check the fit

Fit exponential, normal and lognormal to 200 service times, rank them by KS distance and Q-Q points, and see what a wrong choice does to a queue.

Read the concept note first: `../../../content/concepts/L200/07-input-modelling.md`. No new packages: the L100 pins (`labs/L100/01-setup-workbench/requirements.txt`) already include numpy, SciPy and SimPy.

## Run
```bash
python fit_inputs.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L200\07-input-modelling` on Windows, `cd labs/L200/07-input-modelling` on macOS).

## Expected output (real run, Python 3.12.15, Linux; seeded, identical on every run)
```
data: n=200 mean=4.75 sd=3.46 cv=0.73 max=24.30 min
candidate    parameters                   KS D   (5% critical ~0.096 if params were known)
exponential  rate=0.211                   0.217
normal       mu=4.749 sigma=3.463         0.132
lognormal    mu=1.344 sigma=0.655         0.031
smallest D: lognormal | Q-Q (p: fitted vs data): 0.10: 1.66 vs 1.75  0.50: 3.84 vs 3.93  0.90: 8.88 vs 8.49  0.99: 17.59 vs 18.17
queue at 85% load (lam=0.179/min): mean wait / p95 wait / P(service > 10 min)
  exponential       26.38 min /  85.51 min / 0.122
  normal            24.11 min /  76.41 min / 0.065
  lognormal         20.48 min /  67.56 min / 0.072
  data (resampled)  21.18 min /  71.91 min / 0.055
```

## Test
```bash
python -m unittest -v
```
Observed: `Ran 16 tests ... OK (skipped=1)` - library tests are skipped locally (not installed) and run in CI.

## Try it
```bash
python try_it.py
```
Observed:
```
n=30: exponential D=0.326, normal D=0.175, lognormal D=0.098 | 1.36/sqrt(30)=0.248
load 0.50: exponential input   4.67 min vs data   3.65 min -> 1.28x
load 0.70: exponential input  10.84 min vs data   8.48 min -> 1.28x
load 0.85: exponential input  26.38 min vs data  21.18 min -> 1.25x
```

## Build it (your task)
Add a shifted-exponential candidate (minimum set-up time + exponential tail): fit, cdf, ppf, sample, and include it in FITTERS.

Hints:
- MLE: loc = min(data), rate = 1 / (mean - loc).
- cdf must be 0 below loc: use np.where.
- ppf(p) = loc - log(1 - p) / rate.

Check: `python -m unittest test_build_task -v` (observed: `Ran 4 tests ... OK`). The reference solution is `solution/shifted_exponential.py`; to test your own version, change the import at the top of `test_build_task.py`.
Reference solution output (`python solution/shifted_exponential.py`):
```
exponential          KS D=0.217
normal               KS D=0.132
lognormal            KS D=0.031
shifted exponential  KS D=0.176
```

## Library equivalent (pending-ci)
`fit_scipy.py` does the same with SciPy 1.18.1 `scipy.stats` fits + `kstest`. It is not installed in the offline sandbox, so it has **not been run yet**; the CI workflow installs the pinned version and runs it plus the un-skipped test.

## Agent assist (optional)
```bash
python agent_assist.py --fake   # deterministic fake model server
python agent_assist.py          # local Ollama at LOCAL_MODEL_URL
```
Observed with the fake server:
```
1. code summarised the data: {"n": 200, "mean": 4.75, "sd": 3.46, "cv": 0.73, "skewness": 2.31, "min": 0.39, "max": 24.3}
2. agent proposed: {"distribution": "exponential", "reason": "cv is close to 1, so service times look memoryless"}
3. code fitted every candidate (KS D, smallest first):
   lognormal | 0.031
   normal | 0.132
   exponential | 0.217
4. code decided: lognormal - the agent's pick (exponential) is overruled (rank 3 of 3); data cv is 0.73
5. agent explained: The lognormal fits best with D = 0.031, far below the exponential at D = 0.217. Because D is below 0.05 the lognormal is accepted at the 99% level.
6. code checked 4 quoted numbers: 2 match; UNVERIFIED (treat as the model's guess): 0.05, 99
```
The agent only proposes and explains. Code fits every candidate, decides by the smallest KS D, and flags any quoted number that is not in the table. Tests: `python -m unittest test_agent_assist -v` (observed: `Ran 4 tests ... OK`).

## Files
- `fit_inputs.py` - main lab code
- `service_times.csv` - 200 synthetic service times (minutes)
- `make_data.py` - how the CSV was generated (seed 2026, lognormal)
- `fit_scipy.py` - SciPy 1.18.1 equivalent (pending-ci)
- `solution/shifted_exponential.py` - buildTask solution
- `agent_assist.py` - agent proposes a distribution; code decides and checks
- `try_it.py` - tryIt script
- `test_*.py` - unit tests (`test_build_task.py` checks the buildTask)
