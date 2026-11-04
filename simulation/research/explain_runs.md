# Explain runs — simulation

Every output quoted in `content/explain/NN.md` comes from the runs below, executed on **2026-11-02** in this sandbox:
Python 3.12.15, numpy 2.5.3, Linux x86_64, 1 CPU (`os.cpu_count() = 1`), slow shared storage. SimPy, SciPy, Mesa,
SALib, FMPy, OpenModelica, pyarrow and a local LLM server are not installed; anything that needs them is marked
"Expected (not run here)" in the explanations.

Method: the topic's `labs/` folder was copied to a scratch directory outside the repository and every command was run
there from the lab's own folder, one at a time, so committed artefacts (`runs.jsonl`, `cosim_log_*.jsonl`,
`twin_log.jsonl`, `sweep.db`, `data/`) were not rewritten. Commands are exactly as shown (`$ ...`), with exit code and
wall time. `BUILD_TARGET=mine` runs check the *shipped* (faulty) file, so their exit 1 is the expected failure-lab
result. Scratch paths in tracebacks are shortened to `<scratch>`. `research/explain_checks.py` checks that every
number quoted in a "What you see" block (and in L500 "See it in numbers" code blocks) appears in this file.

## Differences from the lab READMEs / lesson JSON

- L300 #16 `perf.py` timing is machine-dependent: here numpy was 17.8x (shipped) and 11.6x (solution) faster than the
  loop; 2 spawn workers took 22.608 s / 39.430 s (slower than serial on 1 CPU). The lesson quotes "7-26x across runs".
- L400 #20 `storage_options.py`: CSV 0.098 s, SQLite per row 28.286 s, per 8 rows 7.528 s, one commit 0.068 s
  (lesson: 0.176 / 22.841 / 3.980 / 0.058 s). Same ordering and the same crash results (1 malformed of 2; 16 rows, 16 distinct).
- L400 #20 `scaling.py`: 10.6 tasks/s on 1 worker, 4.7 on 4 workers x chunk 8, f = 1.00 (lesson: 15.7 and 6.1). Same conclusion.
- L400 #22 `run_capstone.py` took 463.4 s here (lesson: "about 3 minutes"); all milestone numbers match the lesson.
- All other quoted values that the lesson text also states matched it (test timings like "Ran 3 tests in 89.819s" naturally vary).

## Not run here

SimPy/SciPy/Mesa equivalents (`simpy_queue.py`, `falling_scipy.py`, `schelling_mesa.py`, `fit_scipy.py`, `simpy_mmc.py`,
`ode_scipy.py`, `simpy_inventory.py`, `calibrate_scipy.py`, `sensitivity_salib.py`), `fmpy_cosim.py` with a real FMU,
agent assists against a real local model (only `--fake` was run), the Parquet round trip, and full `python -m unittest -v`
suites for L300/L400 labs (targeted build-task and fitness tests were run instead).

## 01 — Set up your simulation workbench

2026-11-02 | labs/L100/01-setup-workbench | $ python check_env.py | exit 0 | 21.9s

```text
Python 3.12.15 on Linux x86_64 | CPU cores: 1
  numpy  pin 2.5.3   installed 2.5.3
  simpy  pin 4.1.2   not installed -> runs in CI
  scipy  pin 1.18.1  not installed -> runs in CI
  mesa   pin 3.5.1   not installed -> runs in CI
seed 42 -> [0.773956, 0.438878, 0.858598]
seed 42 -> [0.773956, 0.438878, 0.858598] (identical = reproducible)
READY for local labs
```

2026-11-02 | labs/L100/01-setup-workbench | $ python try_it.py | exit 0 | 1.8s

```text
unseeded equal? False
random.Random(42): 0.639427 | numpy default_rng(42): 0.773956
```

2026-11-02 | labs/L100/01-setup-workbench | $ python -m unittest -v | exit 0 | 5.0s

```text
[stderr]
test_numpy_available (test_setup.TestSetup.test_numpy_available) ... ok
test_pins_are_exact (test_setup.TestSetup.test_pins_are_exact) ... ok
test_pins_parse_with_windows_line_endings (test_setup.TestSetup.test_pins_parse_with_windows_line_endings) ... ok
test_python_version (test_setup.TestSetup.test_python_version) ... ok
test_seeded_rng_is_reproducible (test_setup.TestSetup.test_seeded_rng_is_reproducible) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.374s

OK
```

## 02 — Monte Carlo: estimate a project's completion time

2026-11-02 | labs/L100/02-monte-carlo | $ python monte_carlo.py | exit 0 | 21.6s

```text
exact mean (from formula): 17.333 days
       N    mean   95% CI half-width   P(<= 20 days)
     100  17.196   +/- 0.436            0.890
    1000  17.376   +/- 0.150            0.849
   10000  17.346   +/- 0.047            0.855
  100000  17.334   +/- 0.015            0.857
P50 / P90 completion (days): [17.23 20.56]
```

2026-11-02 | labs/L100/02-monte-carlo | $ python try_it.py | exit 0 | 5.9s

```text
seed 42: N=100 mean 17.196 | N=100000 mean 17.334 +/- 0.015
seed 7: N=100 mean 17.401 | N=100000 mean 17.338 +/- 0.015
build max 20 d: mean 19.332 +/- 0.022, P(<= 20 days) 0.602
pi estimate (N=100000): 3.1501 +/- 0.0101
```

## 03 — Discrete-event simulation: a single-server queue

2026-11-02 | labs/L100/03-discrete-event-queue | $ python des_queue.py | exit 0 | 2.4s

```text
first events (clock jumps from event to event):
t=  0.180  arrive  customer 0  queue=0 busy=False
t=  1.623  depart  customer 0  queue=0
t=  2.531  arrive  customer 1  queue=0 busy=False
t=  2.899  arrive  customer 2  queue=0 busy=True
t=  3.215  depart  customer 1  queue=1
t=  3.645  arrive  customer 3  queue=0 busy=True
t=  4.269  depart  customer 2  queue=1
t=  4.368  depart  customer 3  queue=0
customers=200000  simulated time=250,436 min
simulated mean wait = 3.871 min | M/M/1 formula Wq = 4.000 min | diff -3.2%
```

2026-11-02 | labs/L100/03-discrete-event-queue | $ python try_it.py | exit 0 | 6.9s

```text
lam=0.8: simulated Wq=3.87 min, formula Wq=4.00 min
lam=0.88: simulated Wq=7.08 min, formula Wq=7.33 min
200 customers, seed 1: mean wait 4.19 min
200 customers, seed 2: mean wait 2.31 min
200 customers, seed 3: mean wait 7.71 min
```

## 04 — Time-stepped physics: a parcel dropped from a drone

2026-11-02 | labs/L100/04-time-stepped-physics | $ python falling.py | exit 0 | 2.3s

```text
No drag, height at t=3 s. Exact = 55.9000 m
    dt   explicit Euler err   semi-implicit err   RK4 err   (err = simulated - exact)
   0.1            +1.470000           -1.470000   -1.4e-14
  0.01            +0.147000           -0.147000   +7.8e-14
 0.001            +0.014700           -0.014700   +9.1e-13
With drag: terminal velocity = 18.40 m/s
Time to fall 100 m: no drag 4.52 s (exact 4.52 s), with drag 6.74 s, impact 18.37 m/s
```

2026-11-02 | labs/L100/04-time-stepped-physics | $ python try_it.py | exit 0 | 0.8s

```text
Euler dt=0.5: ground at 7.00 s, impact 18.40 m/s
RK4 dt=0.001: ground at 6.74 s, impact 18.37 m/s
4 kg parcel: terminal velocity 26.02 m/s (x1.41), ground at 5.65 s
sqrt(2) = 1.414
```

## 05 — Agent-based modelling: Schelling's neighbourhood model

2026-11-02 | labs/L100/05-agent-based-schelling | $ python schelling.py | exit 0 | 9.1s

```text
step  1: moved 160  % similar  62.2  % unhappy   8.1
step  2: moved  66  % similar  67.9  % unhappy   4.2
step  3: moved  34  % similar  69.3  % unhappy   4.0
step  5: moved  16  % similar  73.9  % unhappy   1.0
step 10: moved   4  % similar  75.1  % unhappy   0.4
step 15: moved   1  % similar  75.4  % unhappy   0.1
step 17: moved   1  % similar  75.4  % unhappy   0.0
start: % similar 50.2 -> end: 75.4 (each agent only wanted 30%)
top-left 10x10 corner at the end (. empty, x / o agent types):
x x x x x x x x x x
. x x x x x x x x x
x x x x x x . . x x
x x x x x x x o o x
o o . x x . x x o o
o . . x x x x x o o
o o x x x x x x x x
o o x x x x . x x x
o o x x x . o x x x
o . x x x x o o x x
```

2026-11-02 | labs/L100/05-agent-based-schelling | $ python try_it.py | exit 0 | 10.8s

```text
want 30%: end % similar 75.4, % unhappy 0.0, steps 17
want 50%: end % similar 87.6, % unhappy 0.0, steps 13
seeds 1-5 end % similar: [72.3, 76.3, 75.1, 74.7, 73.1]
```

## 06 — Is the model right? Verification vs validation

2026-11-02 | labs/L100/06-verification-validation | $ python vv.py | exit 0 | 10.7s

```text
1. reproducibility: seed 1 -> ef34cf71198d, seed 1 again -> ef34cf71198d, seed 2 -> ac9c300ece80
2. validation (lam=0.8): simulated 4.046 +/- 0.195 min vs formula 4.000 -> PASS
3. sensitivity to arrival rate (utilisation = lam/mu):
   lam=0.5  simulated  1.003 +/- 0.020   formula  1.000
   lam=0.6  simulated  1.506 +/- 0.037   formula  1.500
   lam=0.7  simulated  2.353 +/- 0.075   formula  2.333
   lam=0.8  simulated  4.046 +/- 0.195   formula  4.000
   lam=0.9  simulated  8.952 +/- 0.730   formula  9.000
```

2026-11-02 | labs/L100/06-verification-validation | $ python try_it.py | exit 0 | 18.7s

```text
buggy rule: min wait -5168.4 min, mean wait -2619.9 min  (negative waits are impossible)
warm-up   0: average of 50 short runs = 3.92 min (formula 4.00)
warm-up 500: average of 50 short runs = 4.02 min (formula 4.00)
```

2026-11-02 | labs/L100/06-verification-validation | $ python agent_assist.py --fake | exit 0 | 60.7s

```text
1. agent proposed: {"parameter": "lam", "values": [0.5, 0.7, 0.9, 1.2], "customers": 20000}
2. code validated: run lam=[0.5, 0.7, 0.9] with 20000 customers; rejected: 1.2: outside [0.05, 0.95] (unstable or trivial queue)
3. code ran 10 replications per value:
   lam | simulated mean wait (min) | 95% CI half-width | M/M/1 formula (min)
   0.50 | 1.014 | 0.033 | 1.000
   0.70 | 2.396 | 0.105 | 2.333
   0.90 | 9.141 | 1.275 | 9.000
4. agent explained: Mean wait grows faster than the arrival rate: at lam=0.50 the simulation gives 1.014 min (formula 1.000), at lam=0.90 it gives 9.141 min (formula 9.000). Extrapolating, at lam=0.95 the wait would be about 19.0 min.
5. code checked 8 quoted numbers: 6 match the table; UNVERIFIED (treat as the model's guess): 0.95, 19.0
```

2026-11-02 | labs/L100/06-verification-validation | $ python -m unittest -v test_vv | exit 0 | 23.9s

```text
[stderr]
test_t_975_9_matches_scipy (test_vv.TestTQuantile.test_t_975_9_matches_scipy) ... skipped 'scipy not installed (pending-ci)'
test_ci_contains_formula (test_vv.TestValidation.test_ci_contains_formula) ... ok
test_sensitivity_is_monotonic (test_vv.TestValidation.test_sensitivity_is_monotonic) ... ok
test_first_customer_never_waits (test_vv.TestVerification.test_first_customer_never_waits) ... ok
test_reproducible (test_vv.TestVerification.test_reproducible) ... ok
test_rule_hand_cases (test_vv.TestVerification.test_rule_hand_cases) ... ok
test_waits_never_negative (test_vv.TestVerification.test_waits_never_negative) ... ok

----------------------------------------------------------------------
Ran 7 tests in 6.919s

OK (skipped=1)
```

## 07 — Input modelling: fit service times and check the fit

2026-11-02 | labs/L200/07-input-modelling | $ python fit_inputs.py | exit 0 | 6.5s

```text
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

2026-11-02 | labs/L200/07-input-modelling | $ python try_it.py | exit 0 | 20.5s

```text
n=30: exponential D=0.326, normal D=0.175, lognormal D=0.098 | 1.36/sqrt(30)=0.248
load 0.50: exponential input   4.67 min vs data   3.65 min -> 1.28x
load 0.70: exponential input  10.84 min vs data   8.48 min -> 1.28x
load 0.85: exponential input  26.38 min vs data  21.18 min -> 1.25x
```

2026-11-02 | labs/L200/07-input-modelling | $ python agent_assist.py --fake | exit 0 | 22.5s

```text
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

## 08 — Resources and queues: c desks, one line, Erlang C

2026-11-02 | labs/L200/08-multi-server-queue | $ python mmc_queue.py | exit 0 | 3.8s

```text
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

2026-11-02 | labs/L200/08-multi-server-queue | $ python try_it.py | exit 0 | 6.5s

```text
3 separate lines: Wq=3.87 min | 1 shared line, 3 desks: Wq=1.11 min | formula 4.00 vs 1.08
lam=2.4: utilisation 80%, simulated Wq=1.11 min, Erlang C Wq=1.08 min
lam=2.64: utilisation 88%, simulated Wq=2.30 min, Erlang C Wq=2.17 min
```

## 09 — ODE solvers in practice: adaptive steps, tolerances, stiffness

2026-11-02 | labs/L200/09-adaptive-ode | $ python adaptive_ode.py | exit 0 | 6.3s

```text
1. coffee 90 C -> 30 min, room 20 C (exact 35.619111 C)
   rtol=1e-03:   5 steps, 0 rejected, error 1.3e-02 C
   rtol=1e-06:   9 steps, 0 rejected, error 8.2e-06 C
   rtol=1e-09:  26 steps, 0 rejected, error 7.9e-09 C
2. rabbits/foxes 0-15: 204 steps, invariant drift 2.6e-05
   smallest step 0.0316 at t=12.72: rabbits 12.24, foxes  1.12
   largest step 0.1852 at t= 7.40: rabbits  3.04, foxes  0.02
3. stiff RC filter (tau = 1 ms), 0-10 s, exact v(10)=-0.83961:
   explicit RK45 rtol=1e-03:  3027 steps (110 rejected), v(10)=-0.83987
   explicit RK45 rtol=1e-06:  3586 steps ( 10 rejected), v(10)=-0.83961
   implicit backward Euler dt=0.01: 1000 steps, v(10)=-0.83961
```

2026-11-02 | labs/L200/09-adaptive-ode | $ python try_it.py | exit 0 | 13.6s

```text
rabbits/foxes rtol=1e-03:   55 steps, invariant drift 1.4e-01
rabbits/foxes rtol=1e-06:  204 steps, invariant drift 2.6e-05
rabbits/foxes rtol=1e-09:  639 steps, invariant drift 3.1e-08
RC tau=1e-03 s: explicit RK45   3027 steps, v(10)=-0.83987
RC tau=1e-04 s: explicit RK45  30226 steps, v(10)=-0.83929
```

## 10 — Warm-up, replications and confidence

2026-11-02 | labs/L200/10-warmup-replications | $ python warmup.py | exit 0 | 5.7s

```text
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

2026-11-02 | labs/L200/10-warmup-replications | $ python try_it.py | exit 0 | 9.9s

```text
backlog 30, no deletion: 5.59 +/- 0.61 min (true 4.0)
backlog  0, no deletion: 3.57 +/- 0.43 min (true 4.0)
proposed warm-up for three new seed sets: [215, 195, 961]
80 replications, delete first 169: 4.01 +/- 0.16 min
80 replications, delete first 961: 3.98 +/- 0.17 min
```

## 11 — A supply-chain model: (s, S) inventory with common random numbers

2026-11-02 | labs/L200/11-supply-chain-inventory | $ python inventory.py | exit 0 | 4.1s

```text
(s, S) policies over 365 days, 30 replications: mean cost per day +/- 95% CI
  s=20 S=80:   8.71 +/- 0.30  orders/yr  40.6  lost tubes/yr  217.9
  s=30 S=80:   8.56 +/- 0.27  orders/yr  50.3  lost tubes/yr  111.3
  s=30 S=90:   8.30 +/- 0.22  orders/yr  42.7  lost tubes/yr   89.9
difference S=90 minus S=80, independent: +0.03 +/- 0.44 -> cannot tell
difference S=90 minus S=80, CRN        : -0.25 +/- 0.12 -> S=90 is cheaper
```

2026-11-02 | labs/L200/11-supply-chain-inventory | $ python try_it.py | exit 0 | 4.4s

```text
same seeds, ONE shared stream: S=90 minus S=80 = -0.19 +/- 0.31
same seeds, one stream per purpose (lab): -0.25 +/- 0.12
lost sale costs 2.00: S=90 minus S=80 = -0.13 +/- 0.08 per day
```

## 12 — Variance reduction: same precision, fewer runs

2026-11-02 | labs/L300/12-variance-reduction | $ python variance_reduction.py | exit 0 | 6.9s

```text
exact expected overtime: 0.9196 h per shift (Erlang formula)
20,000 model evaluations per method:
  method              estimate   std.err   variance ratio vs plain
  plain Monte Carlo   0.9025    0.00990    1.00x
  antithetic          0.9208    0.00819    1.46x  rho=-0.32
  control variate     0.9203    0.00426    5.40x  beta=0.609
  antithetic (loop)   0.8999    0.00986    1.01x  rho=-0.00
CRN recap, overtime saved by a 7.5 h shift: independent 0.2120 +/- 0.0259, common 0.2237 +/- 0.0033 h
```

2026-11-02 | labs/L300/12-variance-reduction | $ BUILD_TARGET=mine python -m unittest test_build_task -v | exit 1 | 8.4s

```text
[stderr]
test_pairs_anti_correlate (test_build_task.TestOneStreamPerPair.test_pairs_anti_correlate) ... FAIL
test_still_unbiased (test_build_task.TestOneStreamPerPair.test_still_unbiased) ... ok
test_variance_ratio_like_the_vectorised_version (test_build_task.TestOneStreamPerPair.test_variance_ratio_like_the_vectorised_version) ... FAIL

======================================================================
FAIL: test_pairs_anti_correlate (test_build_task.TestOneStreamPerPair.test_pairs_anti_correlate)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L300/12-variance-reduction/test_build_task.py", line 29, in test_pairs_anti_correlate
    self.assertLess(self.r["rho"], -0.25)
AssertionError: -0.0012398657583570188 not less than -0.25

======================================================================
FAIL: test_variance_ratio_like_the_vectorised_version (test_build_task.TestOneStreamPerPair.test_variance_ratio_like_the_vectorised_version)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L300/12-variance-reduction/test_build_task.py", line 32, in test_variance_ratio_like_the_vectorised_version
    self.assertGreater(reference.plain(N)["var_per_eval"] / self.r["var_per_eval"], 1.3)
AssertionError: 1.0085792208411501 not greater than 1.3

----------------------------------------------------------------------
Ran 3 tests in 5.318s

FAILED (failures=2)
```

2026-11-02 | labs/L300/12-variance-reduction | $ python solution/variance_reduction.py | exit 0 | 4.8s

```text
exact expected overtime: 0.9196 h per shift (Erlang formula)
20,000 model evaluations per method:
  method              estimate   std.err   variance ratio vs plain
  plain Monte Carlo   0.9025    0.00990    1.00x
  antithetic          0.9208    0.00819    1.46x  rho=-0.32
  control variate     0.9203    0.00426    5.40x  beta=0.609
  antithetic (loop)   0.9091    0.00809    1.50x  rho=-0.33
CRN recap, overtime saved by a 7.5 h shift: independent 0.2120 +/- 0.0259, common 0.2237 +/- 0.0033 h
```

2026-11-02 | labs/L300/12-variance-reduction | $ python try_it.py | exit 0 | 2.6s

```text
symmetric model: rho=+1.00, variance ratio antithetic vs plain = 0.49x
control variate beta=0.609: variance ratio 5.40x
control variate beta=1.0: variance ratio 1.92x
control variate beta=1.5: variance ratio 0.52x
```

2026-11-02 | labs/L300/12-variance-reduction | $ python -m unittest test_build_task -v | exit 0 | 8.5s

```text
[stderr]
test_pairs_anti_correlate (test_build_task.TestOneStreamPerPair.test_pairs_anti_correlate) ... ok
test_still_unbiased (test_build_task.TestOneStreamPerPair.test_still_unbiased) ... ok
test_variance_ratio_like_the_vectorised_version (test_build_task.TestOneStreamPerPair.test_variance_ratio_like_the_vectorised_version) ... ok

----------------------------------------------------------------------
Ran 3 tests in 3.041s

OK
```

## 13 — Calibration: fit to data, validate on data you did not fit

2026-11-02 | labs/L300/13-calibration | $ python calibrate.py | exit 0 | 18.0s

```text
73 readings, 49 for calibration (0-8 h), 24 held out (8-12 h); sensor noise sd 0.15
  model           RMSE on calibration data   RMSE on holdout   prediction at 12 h (measured 13.33)
  one-exp (3 p)        0.175 C                  0.434 C         13.65 C
  two-exp (5 p)        0.152 C                  0.161 C         13.10 C
  poly-6 (7 p)         0.148 C                 12.517 C        -19.60 C
select() picks poly-6 (7 p); its holdout RMSE is 12.517 C
```

2026-11-02 | labs/L300/13-calibration | $ BUILD_TARGET=mine python -m unittest test_build_task -v | exit 1 | 5.8s

```text
[stderr]
test_never_picks_the_polynomial_for_other_noise_seeds (test_build_task.TestHoldoutSelection.test_never_picks_the_polynomial_for_other_noise_seeds) ... 
  test_never_picks_the_polynomial_for_other_noise_seeds (test_build_task.TestHoldoutSelection.test_never_picks_the_polynomial_for_other_noise_seeds) (seed=20) ... FAIL
  test_never_picks_the_polynomial_for_other_noise_seeds (test_build_task.TestHoldoutSelection.test_never_picks_the_polynomial_for_other_noise_seeds) (seed=21) ... FAIL
  test_never_picks_the_polynomial_for_other_noise_seeds (test_build_task.TestHoldoutSelection.test_never_picks_the_polynomial_for_other_noise_seeds) (seed=22) ... FAIL
  test_never_picks_the_polynomial_for_other_noise_seeds (test_build_task.TestHoldoutSelection.test_never_picks_the_polynomial_for_other_noise_seeds) (seed=23) ... FAIL
  test_never_picks_the_polynomial_for_other_noise_seeds (test_build_task.TestHoldoutSelection.test_never_picks_the_polynomial_for_other_noise_seeds) (seed=24) ... FAIL
  test_never_picks_the_polynomial_for_other_noise_seeds (test_build_task.TestHoldoutSelection.test_never_picks_the_polynomial_for_other_noise_seeds) (seed=25) ... FAIL
  test_never_picks_the_polynomial_for_other_noise_seeds (test_build_task.TestHoldoutSelection.test_never_picks_the_polynomial_for_other_noise_seeds) (seed=26) ... FAIL
  test_never_picks_the_polynomial_for_other_noise_seeds (test_build_task.TestHoldoutSelection.test_never_picks_the_polynomial_for_other_noise_seeds) (seed=27) ... FAIL
  test_never_picks_the_polynomial_for_other_noise_seeds (test_build_task.TestHoldoutSelection.test_never_picks_the_polynomial_for_other_noise_seeds) (seed=28) ... FAIL
  test_never_picks_the_polynomial_for_other_noise_seeds (test_build_task.TestHoldoutSelection.test_never_picks_the_polynomial_for_other_noise_seeds) (seed=29) ... FAIL
test_picks_a_model_that_forecasts (test_build_task.TestHoldoutSelection.test_picks_a_model_that_forecasts) ... FAIL

======================================================================
FAIL: test_never_picks_the_polynomial_for_other_noise_seeds (test_build_task.TestHoldoutSelection.test_never_picks_the_polynomial_for_other_noise_seeds) (seed=20)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L300/13-calibration/test_build_task.py", line 37, in test_never_picks_the_polynomial_for_other_noise_seeds
    self.assertNotEqual(target.select(reference.observed(seed))[0], "poly-6 (7 p)")
AssertionError: 'poly-6 (7 p)' == 'poly-6 (7 p)'

======================================================================
FAIL: test_never_picks_the_polynomial_for_other_noise_seeds (test_build_task.TestHoldoutSelection.test_never_picks_the_polynomial_for_other_noise_seeds) (seed=21)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L300/13-calibration/test_build_task.py", line 37, in test_never_picks_the_polynomial_for_other_noise_seeds
    self.assertNotEqual(target.select(reference.observed(seed))[0], "poly-6 (7 p)")
AssertionError: 'poly-6 (7 p)' == 'poly-6 (7 p)'

======================================================================
FAIL: test_never_picks_the_polynomial_for_other_noise_seeds (test_build_task.TestHoldoutSelection.test_never_picks_the_polynomial_for_other_noise_seeds) (seed=22)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L300/13-calibration/test_build_task.py", line 37, in test_never_picks_the_polynomial_for_other_noise_seeds
    self.assertNotEqual(target.select(reference.observed(seed))[0], "poly-6 (7 p)")
AssertionError: 'poly-6 (7 p)' == 'poly-6 (7 p)'

======================================================================
FAIL: test_never_picks_the_polynomial_for_other_noise_seeds (test_build_task.TestHoldoutSelection.test_never_picks_the_polynomial_for_other_noise_seeds) (seed=23)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L300/13-calibration/test_build_task.py", line 37, in test_never_picks_the_polynomial_for_other_noise_seeds
    self.assertNotEqual(target.select(reference.observed(seed))[0], "poly-6 (7 p)")
AssertionError: 'poly-6 (7 p)' == 'poly-6 (7 p)'

======================================================================
FAIL: test_never_picks_the_polynomial_for_other_noise_seeds (test_build_task.TestHoldoutSelection.test_never_picks_the_polynomial_for_other_noise_seeds) (seed=24)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L300/13-calibration/test_build_task.py", line 37, in test_never_picks_the_polynomial_for_other_noise_seeds
    self.assertNotEqual(target.select(reference.observed(seed))[0], "poly-6 (7 p)")
AssertionError: 'poly-6 (7 p)' == 'poly-6 (7 p)'

======================================================================
FAIL: test_never_picks_the_polynomial_for_other_noise_seeds (test_build_task.TestHoldoutSelection.test_never_picks_the_polynomial_for_other_noise_seeds) (seed=25)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L300/13-calibration/test_build_task.py", line 37, in test_never_picks_the_polynomial_for_other_noise_seeds
    self.assertNotEqual(target.select(reference.observed(seed))[0], "poly-6 (7 p)")
AssertionError: 'poly-6 (7 p)' == 'poly-6 (7 p)'

======================================================================
FAIL: test_never_picks_the_polynomial_for_other_noise_seeds (test_build_task.TestHoldoutSelection.test_never_picks_the_polynomial_for_other_noise_seeds) (seed=26)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L300/13-calibration/test_build_task.py", line 37, in test_never_picks_the_polynomial_for_other_noise_seeds
    self.assertNotEqual(target.select(reference.observed(seed))[0], "poly-6 (7 p)")
AssertionError: 'poly-6 (7 p)' == 'poly-6 (7 p)'

======================================================================
FAIL: test_never_picks_the_polynomial_for_other_noise_seeds (test_build_task.TestHoldoutSelection.test_never_picks_the_polynomial_for_other_noise_seeds) (seed=27)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L300/13-calibration/test_build_task.py", line 37, in test_never_picks_the_polynomial_for_other_noise_seeds
    self.assertNotEqual(target.select(reference.observed(seed))[0], "poly-6 (7 p)")
AssertionError: 'poly-6 (7 p)' == 'poly-6 (7 p)'

======================================================================
FAIL: test_never_picks_the_polynomial_for_other_noise_seeds (test_build_task.TestHoldoutSelection.test_never_picks_the_polynomial_for_other_noise_seeds) (seed=28)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L300/13-calibration/test_build_task.py", line 37, in test_never_picks_the_polynomial_for_other_noise_seeds
    self.assertNotEqual(target.select(reference.observed(seed))[0], "poly-6 (7 p)")
AssertionError: 'poly-6 (7 p)' == 'poly-6 (7 p)'

======================================================================
FAIL: test_never_picks_the_polynomial_for_other_noise_seeds (test_build_task.TestHoldoutSelection.test_never_picks_the_polynomial_for_other_noise_seeds) (seed=29)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L300/13-calibration/test_build_task.py", line 37, in test_never_picks_the_polynomial_for_other_noise_seeds
    self.assertNotEqual(target.select(reference.observed(seed))[0], "poly-6 (7 p)")
AssertionError: 'poly-6 (7 p)' == 'poly-6 (7 p)'

======================================================================
FAIL: test_picks_a_model_that_forecasts (test_build_task.TestHoldoutSelection.test_picks_a_model_that_forecasts)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L300/13-calibration/test_build_task.py", line 31, in test_picks_a_model_that_forecasts
    self.assertEqual(best, "two-exp (5 p)")
AssertionError: 'poly-6 (7 p)' != 'two-exp (5 p)'
- poly-6 (7 p)
+ two-exp (5 p)


----------------------------------------------------------------------
Ran 2 tests in 1.867s

FAILED (failures=11)
```

2026-11-02 | labs/L300/13-calibration | $ python solution/calibrate.py | exit 0 | 2.8s

```text
73 readings, 49 for calibration (0-8 h), 24 held out (8-12 h); sensor noise sd 0.15
  model           RMSE on calibration data   RMSE on holdout   prediction at 12 h (measured 13.33)
  one-exp (3 p)        0.175 C                  0.434 C         13.65 C
  two-exp (5 p)        0.152 C                  0.161 C         13.10 C
  poly-6 (7 p)         0.148 C                 12.517 C        -19.60 C
select() picks two-exp (5 p); its holdout RMSE is 0.161 C
```

2026-11-02 | labs/L300/13-calibration | $ python try_it.py | exit 0 | 20.7s

```text
two-exp on 0-5 h: RMSE 0.170 C, T_inf=-71014 C, B=71029 C, tau_wall=326494 h
random holdout RMSE: one-exp (3 p) 0.257, two-exp (5 p) 0.189, poly-6 (7 p) 0.178 -> picks poly-6 (7 p)
```

2026-11-02 | labs/L300/13-calibration | $ python -m unittest test_build_task -v | exit 0 | 27.7s

```text
[stderr]
test_never_picks_the_polynomial_for_other_noise_seeds (test_build_task.TestHoldoutSelection.test_never_picks_the_polynomial_for_other_noise_seeds) ... ok
test_picks_a_model_that_forecasts (test_build_task.TestHoldoutSelection.test_picks_a_model_that_forecasts) ... ok

----------------------------------------------------------------------
Ran 2 tests in 2.254s

OK
```

## 14 — Global sensitivity: OAT vs Morris vs Sobol'

2026-11-02 | labs/L300/14-global-sensitivity | $ python sensitivity.py | exit 0 | 2.2s

```text
input         OAT swing   Morris mu*  sigma    Sobol S1    ST     (kWh/day; indices = share of variance)
outdoor_C        192.0      240.0   112.3     0.804    0.971
occupants         40.0       40.0     0.0     0.031    0.035
window_open        0.0      100.8   107.4     0.005    0.155
lights_h          12.0       12.0     0.0     0.004    0.003
runs: OAT 8, Morris 100, Sobol 49152
rank by OAT swing: outdoor_C > occupants > lights_h > window_open
rank by Sobol ST:  outdoor_C > window_open > occupants > lights_h
sum S1 = 0.844  (1 - sum S1 = variance from interactions)
screen() keeps ['outdoor_C', 'occupants']: the reduced model keeps 84.1% of the variance
```

2026-11-02 | labs/L300/14-global-sensitivity | $ BUILD_TARGET=mine python -m unittest test_build_task -v | exit 1 | 3.3s

```text
[stderr]
test_keeps_the_window (test_build_task.TestScreening.test_keeps_the_window) ... FAIL
test_reduced_model_keeps_over_95_percent_of_the_variance (test_build_task.TestScreening.test_reduced_model_keeps_over_95_percent_of_the_variance) ... FAIL

======================================================================
FAIL: test_keeps_the_window (test_build_task.TestScreening.test_keeps_the_window)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L300/14-global-sensitivity/test_build_task.py", line 27, in test_keeps_the_window
    self.assertEqual(self.keep, ["outdoor_C", "window_open"])
AssertionError: Lists differ: ['outdoor_C', 'occupants'] != ['outdoor_C', 'window_open']

First differing element 1:
'occupants'
'window_open'

- ['outdoor_C', 'occupants']
+ ['outdoor_C', 'window_open']

======================================================================
FAIL: test_reduced_model_keeps_over_95_percent_of_the_variance (test_build_task.TestScreening.test_reduced_model_keeps_over_95_percent_of_the_variance)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L300/14-global-sensitivity/test_build_task.py", line 30, in test_reduced_model_keeps_over_95_percent_of_the_variance
    self.assertGreater(reference.variance_kept(self.keep), 0.95)  # judged by the lab's own check, not the target's
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0.8407603140746266 not greater than 0.95

----------------------------------------------------------------------
Ran 2 tests in 0.310s

FAILED (failures=2)
```

2026-11-02 | labs/L300/14-global-sensitivity | $ python solution/sensitivity.py | exit 0 | 2.0s

```text
input         OAT swing   Morris mu*  sigma    Sobol S1    ST     (kWh/day; indices = share of variance)
outdoor_C        192.0      240.0   112.3     0.804    0.971
occupants         40.0       40.0     0.0     0.031    0.035
window_open        0.0      100.8   107.4     0.005    0.155
lights_h          12.0       12.0     0.0     0.004    0.003
runs: OAT 8, Morris 100, Sobol 49152
rank by OAT swing: outdoor_C > occupants > lights_h > window_open
rank by Sobol ST:  outdoor_C > window_open > occupants > lights_h
sum S1 = 0.844  (1 - sum S1 = variance from interactions)
screen() keeps ['outdoor_C', 'window_open']: the reduced model keeps 96.1% of the variance
```

2026-11-02 | labs/L300/14-global-sensitivity | $ python try_it.py | exit 0 | 2.1s

```text
OAT swings at outdoor=26 C: outdoor_C 192.0, occupants 40.0, window_open 96.0, lights_h 12.0
additive model: outdoor_C S1 0.952 ST 0.951, occupants S1 0.039 ST 0.041, window_open S1 0.000 ST 0.000, lights_h S1 0.005 ST 0.004; sum S1 = 0.995
```

2026-11-02 | labs/L300/14-global-sensitivity | $ python agent_assist.py --fake | exit 0 | 7.6s

```text
1. code computed the table (input | oat_swing | mu* | sigma | S1 | ST):
   outdoor_C | 192.0 | 240.0 | 112.3 | 0.804 | 0.971
   occupants | 40.0 | 40.0 | 0.0 | 0.031 | 0.035
   window_open | 0.0 | 100.8 | 107.4 | 0.005 | 0.155
   lights_h | 12.0 | 12.0 | 0.0 | 0.004 | 0.003
2. agent ranked: outdoor_C > occupants > lights_h > window_open (window_open shows zero swing in the one-at-a-time test, so it can be ignored)
3. code ranks by ST: outdoor_C > window_open > occupants > lights_h
4. code verdict: OVERRULED at #2: agent occupants, code window_open; #3: agent lights_h, code occupants; #4: agent window_open, code lights_h
5. agent explained: outdoor_C dominates with a total-order index of 0.971. window_open explains about 30% of the variance, so it should stay in the model.
6. code checked 2 quoted numbers: 1 match; UNVERIFIED (treat as the model's guess): 30
```

2026-11-02 | labs/L300/14-global-sensitivity | $ python -m unittest test_build_task -v | exit 0 | 36.9s

```text
[stderr]
test_keeps_the_window (test_build_task.TestScreening.test_keeps_the_window) ... ok
test_reduced_model_keeps_over_95_percent_of_the_variance (test_build_task.TestScreening.test_reduced_model_keeps_over_95_percent_of_the_variance) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.297s

OK
```

## 15 — Co-simulation with FMI: master algorithm and communication step

2026-11-02 | labs/L300/15-cosimulation-fmi | $ python cosim.py | exit 0 | 1.5s

```text
{"h_s": 900, "last_hour_swing_C": 6.78, "last_hour_mean_error_C": 2.72, "heater_flips": 9}
  cosim_log_900s.jsonl: 24 lines; last 4:
    {"t_min": 300.0, "h_s": 900, "T_room": 22.755, "heater": 0.049}
    {"t_min": 315.0, "h_s": 900, "T_room": 19.086, "heater": 0.0}
    {"t_min": 330.0, "h_s": 900, "T_room": 15.97, "heater": 0.996}
    {"t_min": 345.0, "h_s": 900, "T_room": 18.834, "heater": 1.0}
```

2026-11-02 | labs/L300/15-cosimulation-fmi | $ python cosim.py 60 | exit 0 | 0.9s

```text
{"h_s": 60, "last_hour_swing_C": 0.0, "last_hour_mean_error_C": 0.0, "heater_flips": 1}
  cosim_log_60s.jsonl: 360 lines; last 4:
    {"t_min": 356.0, "h_s": 60, "T_room": 21.0, "heater": 0.667}
    {"t_min": 357.0, "h_s": 60, "T_room": 21.0, "heater": 0.667}
    {"t_min": 358.0, "h_s": 60, "T_room": 21.0, "heater": 0.667}
    {"t_min": 359.0, "h_s": 60, "T_room": 21.0, "heater": 0.667}
```

2026-11-02 | labs/L300/15-cosimulation-fmi | $ BUILD_TARGET=mine python -m unittest test_build_task -v | exit 1 | 2.5s

```text
[stderr]
test_default_run_settles (test_build_task.TestDefaultStep.test_default_run_settles) ... FAIL
test_default_step_is_below_the_stability_bound (test_build_task.TestDefaultStep.test_default_step_is_below_the_stability_bound) ... FAIL

======================================================================
FAIL: test_default_run_settles (test_build_task.TestDefaultStep.test_default_run_settles)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L300/15-cosimulation-fmi/test_build_task.py", line 28, in test_default_run_settles
    self.assertLess(m["last_hour_swing_C"], 0.2)
AssertionError: 6.78 not less than 0.2

======================================================================
FAIL: test_default_step_is_below_the_stability_bound (test_build_task.TestDefaultStep.test_default_step_is_below_the_stability_bound)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L300/15-cosimulation-fmi/test_build_task.py", line 24, in test_default_step_is_below_the_stability_bound
    self.assertLess(target.COMM_STEP_S, 3600 * math.log(12 / 11))  # tau ln(K/(K-1)) = 313 s
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 900 not less than 313.2409571626669

----------------------------------------------------------------------
Ran 2 tests in 0.007s

FAILED (failures=2)
```

2026-11-02 | labs/L300/15-cosimulation-fmi | $ python try_it.py | exit 0 | 1.3s

```text
h=180 s: last-hour swing 0.00 C, heater flips 1
h=240 s: last-hour swing 0.01 C, heater flips 1
h=300 s: last-hour swing 1.57 C, heater flips 1
h=360 s: last-hour swing 2.42 C, heater flips 10
Gauss-Seidel h=450 s: {'h_s': 450, 'last_hour_swing_C': 0.0, 'last_hour_mean_error_C': 0.0, 'heater_flips': 0}
Gauss-Seidel h=900 s: {'h_s': 900, 'last_hour_swing_C': 2.81, 'last_hour_mean_error_C': 0.92, 'heater_flips': 14}
```

2026-11-02 | labs/L300/15-cosimulation-fmi | $ python -m unittest test_build_task -v | exit 0 | 9.3s

```text
[stderr]
test_default_run_settles (test_build_task.TestDefaultStep.test_default_run_settles) ... ok
test_default_step_is_below_the_stability_bound (test_build_task.TestDefaultStep.test_default_step_is_below_the_stability_bound) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.061s

OK
```

## 16 — Performance and scale: vectorise, parallelise, keep streams independent

2026-11-02 | labs/L300/16-performance-scale | $ python perf.py | exit 0 | 28.7s

```text
40 replications x 20,000 tickets, M/M/1 at 80% load (true mean wait 4.0 min, from empty)
largest difference loop vs numpy: 9.1e-14; numpy vs 2 workers: 7.7e-01
TIMING (machine-dependent):
  python loop           2.746 s   speed-up x   1.0
  numpy vectorised      0.154 s   speed-up x  17.8
  2 spawn workers      22.608 s   speed-up x   0.1
mean wait 4.240 +/- 0.000 min
distinct replication results 1 of 40 (one line each in runs.jsonl)
```

2026-11-02 | labs/L300/16-performance-scale | $ BUILD_TARGET=mine python -m unittest test_build_task -v | exit 1 | 70.5s

```text
[stderr]
test_confidence_interval_has_real_width (test_build_task.TestStreamPerReplication.test_confidence_interval_has_real_width) ... FAIL
test_every_replication_is_distinct (test_build_task.TestStreamPerReplication.test_every_replication_is_distinct) ... FAIL
test_same_results_on_one_or_two_workers (test_build_task.TestStreamPerReplication.test_same_results_on_one_or_two_workers) ... ok

======================================================================
FAIL: test_confidence_interval_has_real_width (test_build_task.TestStreamPerReplication.test_confidence_interval_has_real_width)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L300/16-performance-scale/test_build_task.py", line 33, in test_confidence_interval_has_real_width
    self.assertGreater(reference.ci(self.two)[1], 0.01)
AssertionError: 7.785227104583448e-16 not greater than 0.01

======================================================================
FAIL: test_every_replication_is_distinct (test_build_task.TestStreamPerReplication.test_every_replication_is_distinct)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L300/16-performance-scale/test_build_task.py", line 30, in test_every_replication_is_distinct
    self.assertEqual(len(set(self.two.tolist())), 6)
AssertionError: 1 != 6

----------------------------------------------------------------------
Ran 3 tests in 52.527s

FAILED (failures=2)
```

2026-11-02 | labs/L300/16-performance-scale | $ python solution/perf.py | exit 0 | 87.3s

```text
40 replications x 20,000 tickets, M/M/1 at 80% load (true mean wait 4.0 min, from empty)
largest difference loop vs numpy: 9.1e-14; numpy vs 2 workers: 0.0e+00
TIMING (machine-dependent):
  python loop           3.398 s   speed-up x   1.0
  numpy vectorised      0.292 s   speed-up x  11.6
  2 spawn workers      39.430 s   speed-up x   0.1
mean wait 4.042 +/- 0.118 min
distinct replication results 40 of 40 (one line each in runs.jsonl)
```

2026-11-02 | labs/L300/16-performance-scale | $ python try_it.py | exit 0 | 79.7s

```text
1 vs 2 vs 3 workers bit-identical: True | mean wait 4.099 min
root+id seeding: 7 of 8 replications of run B repeat run A
SeedSequence(17).spawn(8): 0 of 8 repeat run A
```

2026-11-02 | labs/L300/16-performance-scale | $ head -n 2 runs.jsonl | exit 0 | 0.2s

```text
{"rep": 0, "spawn_key": [], "mean_wait": 4.240082576236665, "pid": 6614}
{"rep": 1, "spawn_key": [], "mean_wait": 4.240082576236665, "pid": 6614}
```

2026-11-02 | labs/L300/16-performance-scale | $ python -m unittest test_build_task -v | exit 0 | 67.9s

```text
[stderr]
test_confidence_interval_has_real_width (test_build_task.TestStreamPerReplication.test_confidence_interval_has_real_width) ... ok
test_every_replication_is_distinct (test_build_task.TestStreamPerReplication.test_every_replication_is_distinct) ... ok
test_same_results_on_one_or_two_workers (test_build_task.TestStreamPerReplication.test_same_results_on_one_or_two_workers) ... ok

----------------------------------------------------------------------
Ran 3 tests in 35.340s

OK
```

## 17 — Digital twins with live data: state estimation, drift detection and recalibration

2026-11-02 | labs/L400/17-digital-twin | $ python twin.py | exit 0 | 16.6s

```text
OPTIONS (1-h forecast RMSE vs true zone temperature, C): before drift | last day
  A open-loop model       0.167 |  6.316
  B Kalman filter only    1.480 |  0.194
  C KF + CUSUM + refit    1.789 |  0.151
feed: 850 scored forecasts; skipped {'late_or_duplicate': 2, 'null_reading': 1}
events: 12 (twin_log.jsonl); first 3:
   {"t_min": 1250, "event": "drift_alarm", "s_hi": 405.13, "s_lo": 0.0}
   {"t_min": 1490, "event": "recalibrated", "a": 0.2, "b": 1.0}
   {"t_min": 1495, "event": "drift_alarm", "s_hi": 10.49, "s_lo": 0.0}
alarms before the drift (t < 2500 min): 5; first alarm after it: 2610 min
final model: a=0.0339 b=0.285 (plant after drift: a=0.035 b=0.30)
```

2026-11-02 | labs/L400/17-digital-twin | $ head -c 600 twin_log.jsonl | exit 0 | 0.0s

```text
{"t_min": 1250, "event": "drift_alarm", "s_hi": 405.13, "s_lo": 0.0}
{"t_min": 1490, "event": "recalibrated", "a": 0.2, "b": 1.0}
{"t_min": 1495, "event": "drift_alarm", "s_hi": 10.49, "s_lo": 0.0}
{"t_min": 1745, "event": "recalibrated", "a": 0.2, "b": 1.0}
{"t_min": 1750, "event": "drift_alarm", "s_hi": 10.55, "s_lo": 0.0}
{"t_min": 1990, "event": "recalibrated", "a": 0.0246, "b": 0.375}
{"t_min": 2045, "event": "drift_alarm", "s_hi": 9.34, "s_lo": 0.0}
{"t_min": 2285, "event": "recalibrated", "a": 0.109, "b": 1.0}
{"t_min": 2305, "event": "drift_alarm", "s_hi": 9.23, "s_lo": 0.0}
{"t_min":
```

2026-11-02 | labs/L400/17-digital-twin | $ BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v | exit 1 | 2.9s

```text
[stderr]
test_glitch_is_rejected_not_assimilated (test_build_task.TestInnovationGate.test_glitch_is_rejected_not_assimilated) ... FAIL
test_no_false_alarm_before_the_drift (test_build_task.TestInnovationGate.test_no_false_alarm_before_the_drift) ... FAIL
test_detection_delay_within_one_hour (test_fitness.TestTwinFitness.test_detection_delay_within_one_hour) ... FAIL
test_forecast_beats_threshold_and_filter_only (test_fitness.TestTwinFitness.test_forecast_beats_threshold_and_filter_only) ... FAIL
test_no_false_alarms (test_fitness.TestTwinFitness.test_no_false_alarms) ... FAIL
test_recalibrated_physics_matches_the_plant (test_fitness.TestTwinFitness.test_recalibrated_physics_matches_the_plant) ... ok

======================================================================
FAIL: test_glitch_is_rejected_not_assimilated (test_build_task.TestInnovationGate.test_glitch_is_rejected_not_assimilated)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L400/17-digital-twin/test_build_task.py", line 26, in test_glitch_is_rejected_not_assimilated
    self.assertEqual((first["t_min"], first["event"]), (1250, "rejected"))
AssertionError: Tuples differ: (1250, 'drift_alarm') != (1250, 'rejected')

First differing element 1:
'drift_alarm'
'rejected'

- (1250, 'drift_alarm')
+ (1250, 'rejected')

======================================================================
FAIL: test_no_false_alarm_before_the_drift (test_build_task.TestInnovationGate.test_no_false_alarm_before_the_drift)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L400/17-digital-twin/test_build_task.py", line 29, in test_no_false_alarm_before_the_drift
    self.assertEqual([e for e in self.twin.events if e["event"] == "drift_alarm" and e["t_min"] < 2500], [])
AssertionError: Lists differ: [{'t_min': 1250, 'event': 'drift_alarm', '[357 chars]0.0}] != []

First list contains 5 additional elements.
First extra element 0:
{'t_min': 1250, 'event': 'drift_alarm', 's_hi': np.float64(405.13), 's_lo': 0.0}

+ []
- [{'event': 'drift_alarm',
-   's_hi': np.float64(405.13),
-   's_lo': 0.0,
-   't_min': 1250},
-  {'event': 'drift_alarm',
-   's_hi': np.float64(10.49),
-   's_lo': 0.0,
-   't_min': 1495},
-  {'event': 'drift_alarm',
-   's_hi': np.float64(10.55),
-   's_lo': 0.0,
-   't_min': 1750},
-  {'event': 'drift_alarm', 's_hi': np.float64(9.34), 's_lo': 0.0, 't_min': 2045},
-  {'event': 'drift_alarm', 's_hi': np.float64(9.23), 's_lo': 0.0, 't_min': 2305}]

======================================================================
FAIL: test_detection_delay_within_one_hour (test_fitness.TestTwinFitness.test_detection_delay_within_one_hour)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L400/17-digital-twin/test_fitness.py", line 34, in test_detection_delay_within_one_hour
    self.assertLessEqual(min(t for t in self.alarms() if t >= DRIFT_T) - DRIFT_T, 60)
AssertionError: 110 not less than or equal to 60

======================================================================
FAIL: test_forecast_beats_threshold_and_filter_only (test_fitness.TestTwinFitness.test_forecast_beats_threshold_and_filter_only)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L400/17-digital-twin/test_fitness.py", line 41, in test_forecast_beats_threshold_and_filter_only
    self.assertLessEqual(mine, 0.15)
AssertionError: 0.15052142354379322 not less than or equal to 0.15

======================================================================
FAIL: test_no_false_alarms (test_fitness.TestTwinFitness.test_no_false_alarms)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L400/17-digital-twin/test_fitness.py", line 31, in test_no_false_alarms
    self.assertEqual([t for t in self.alarms() if t < DRIFT_T], [])
AssertionError: Lists differ: [1250, 1495, 1750, 2045, 2305] != []

First list contains 5 additional elements.
First extra element 0:
1250

- [1250, 1495, 1750, 2045, 2305]
+ []

----------------------------------------------------------------------
Ran 6 tests in 1.976s

FAILED (failures=5)
```

2026-11-02 | labs/L400/17-digital-twin | $ python solution/twin.py | exit 0 | 5.7s

```text
OPTIONS (1-h forecast RMSE vs true zone temperature, C): before drift | last day
  A open-loop model       0.167 |  6.316
  B Kalman filter only    0.189 |  0.194
  C KF + CUSUM + refit    0.189 |  0.127
feed: 850 scored forecasts; skipped {'late_or_duplicate': 2, 'null_reading': 1}
events: 3 (twin_log.jsonl); first 3:
   {"t_min": 1250, "event": "rejected", "zone_C": 85.0, "z": 404.5}
   {"t_min": 2525, "event": "drift_alarm", "s_hi": 0.0, "s_lo": 10.51}
   {"t_min": 2765, "event": "recalibrated", "a": 0.0331, "b": 0.267}
alarms before the drift (t < 2500 min): 0; first alarm after it: 2525 min
final model: a=0.0331 b=0.267 (plant after drift: a=0.035 b=0.30)
```

2026-11-02 | labs/L400/17-digital-twin | $ python -m unittest test_fitness -v | exit 0 | 3.5s

```text
[stderr]
test_detection_delay_within_one_hour (test_fitness.TestTwinFitness.test_detection_delay_within_one_hour) ... ok
test_forecast_beats_threshold_and_filter_only (test_fitness.TestTwinFitness.test_forecast_beats_threshold_and_filter_only) ... ok
test_no_false_alarms (test_fitness.TestTwinFitness.test_no_false_alarms) ... ok
test_recalibrated_physics_matches_the_plant (test_fitness.TestTwinFitness.test_recalibrated_physics_matches_the_plant) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.897s

OK
```

2026-11-02 | labs/L400/17-digital-twin | $ python try_it.py | exit 0 | 64.0s

```text
h=8.0: false alarms 0, detection delay 25 min, rejected 1, last-day RMSE 0.127 C
h=4.0: false alarms 2, detection delay 760 min, rejected 490, last-day RMSE 2.407 C
gate=5.0: false alarms 0, detection delay 25 min, rejected 1, last-day RMSE 0.127 C
gate=2.5: false alarms 0, detection delay None min, rejected 366, last-day RMSE 6.051 C
```

## 18 — Simulation-based optimisation: search, ranking & selection and fair budgets

2026-11-02 | labs/L400/18-sim-optimisation | $ python optimise.py | exit 0 | 50.8s

```text
81 (s, Q) designs; true best (25, 70) at 8.479/day (truth.json: 100 reps per design)
budget 324 runs per optimiser (0 reserved for selection), 5 macro-replications
method             mean gap worst gap  reported - true  runs
grid_search           0.049     0.117           -0.472   324   picks [(30, 80), (20, 80), (25, 90), (25, 80), (25, 80)]
surrogate_search      0.277     1.085           -0.412   324   picks [(25, 70), (30, 70), (30, 90), (10, 80), (25, 80)]
evolution             0.052     0.145           -0.299   324   picks [(25, 80), (35, 60), (30, 70), (20, 80), (30, 70)]
```

2026-11-02 | labs/L400/18-sim-optimisation | $ python solution/optimise.py | exit 0 | 40.1s

```text
81 (s, Q) designs; true best (25, 70) at 8.479/day (truth.json: 100 reps per design)
budget 324 runs per optimiser (60 reserved for selection), 5 macro-replications
method             mean gap worst gap  reported - true  runs
grid_search           0.042     0.088           -0.161   324   picks [(30, 60), (25, 80), (25, 60), (20, 80), (30, 70)]
surrogate_search      0.090     0.186           -0.188   324   picks [(25, 80), (35, 70), (25, 80), (20, 80), (35, 70)]
evolution             0.088     0.241           -0.295   324   picks [(25, 60), (30, 50), (25, 60), (30, 70), (25, 70)]
```

2026-11-02 | labs/L400/18-sim-optimisation | $ python try_it.py | exit 0 | 52.8s

```text
grid + OCBA, CRN on : mean gap 0.042, worst 0.088, runs 324
grid + OCBA, CRN off: mean gap 0.200, worst 0.372, runs 324
evolution, fair budget 324: mean gap 0.088, worst 0.241, runs 324
evolution, budget 648     : mean gap 0.008, worst 0.021, runs 648
```

2026-11-02 | labs/L400/18-sim-optimisation | $ BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v | exit 1 | 40.1s

```text
[stderr]
test_report_comes_from_fresh_runs_not_from_the_search (test_build_task.TestSelection.test_report_comes_from_fresh_runs_not_from_the_search) ... FAIL
test_reserve_is_spent_inside_the_same_budget (test_build_task.TestSelection.test_reserve_is_spent_inside_the_same_budget) ... FAIL
test_budget_fairness_across_methods (test_fitness.TestOptimisationFitness.test_budget_fairness_across_methods) ... ok
test_chosen_design_within_the_indifference_zone (test_fitness.TestOptimisationFitness.test_chosen_design_within_the_indifference_zone) ... FAIL
test_reported_cost_is_unbiased (test_fitness.TestOptimisationFitness.test_reported_cost_is_unbiased) ... FAIL

======================================================================
FAIL: test_report_comes_from_fresh_runs_not_from_the_search (test_build_task.TestSelection.test_report_comes_from_fresh_runs_not_from_the_search)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L400/18-sim-optimisation/test_build_task.py", line 29, in test_report_comes_from_fresh_runs_not_from_the_search
    self.assertGreater(reported, 7.0)
AssertionError: 0.0 not greater than 7.0

======================================================================
FAIL: test_reserve_is_spent_inside_the_same_budget (test_build_task.TestSelection.test_reserve_is_spent_inside_the_same_budget)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L400/18-sim-optimisation/test_build_task.py", line 21, in test_reserve_is_spent_inside_the_same_budget
    self.assertGreater(target.RESERVE, 0)
AssertionError: 0 not greater than 0

======================================================================
FAIL: test_chosen_design_within_the_indifference_zone (test_fitness.TestOptimisationFitness.test_chosen_design_within_the_indifference_zone)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L400/18-sim-optimisation/test_fitness.py", line 36, in test_chosen_design_within_the_indifference_zone
    self.assertLessEqual(max(gaps), DELTA)
AssertionError: 0.1169999999999991 not less than or equal to 0.1

======================================================================
FAIL: test_reported_cost_is_unbiased (test_fitness.TestOptimisationFitness.test_reported_cost_is_unbiased)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L400/18-sim-optimisation/test_fitness.py", line 39, in test_reported_cost_is_unbiased
    self.assertLessEqual(abs(np.mean([r["reported"] - r["true"] for r in self.grid])), 0.15)
AssertionError: np.float64(0.39410787037037015) not less than or equal to 0.15

----------------------------------------------------------------------
Ran 5 tests in 15.004s

FAILED (failures=4)
```

2026-11-02 | labs/L400/18-sim-optimisation | $ python -m unittest test_fitness -v | exit 0 | 37.7s

```text
[stderr]
test_budget_fairness_across_methods (test_fitness.TestOptimisationFitness.test_budget_fairness_across_methods) ... ok
test_chosen_design_within_the_indifference_zone (test_fitness.TestOptimisationFitness.test_chosen_design_within_the_indifference_zone) ... ok
test_reported_cost_is_unbiased (test_fitness.TestOptimisationFitness.test_reported_cost_is_unbiased) ... ok

----------------------------------------------------------------------
Ran 3 tests in 15.016s

OK
```

## 19 — Surrogate models and emulation: fast what-ifs that know where they stop

2026-11-02 | labs/L400/19-surrogates | $ python surrogate.py | exit 0 | 34.2s

```text
expensive model: M/M/3 DES, 20,000 patients/run; 30 LHS training runs, 20 holdout runs
surrogate        holdout RMSE max error   (min of wait)
polynomial              0.037     0.079
gp-lite                 0.042     0.103
random features         0.049     0.133
(noise floor)           0.033   = holdout runs vs Erlang C
gp-lite 95% intervals cover 85% of holdout runs; params {'length_scales': [0.4, 0.4], 'noise': 0.01}
WHAT-IF (Erlang C = exact answer for this M/M/3; * = answered by the simulation, not the surrogate):
  lam=2.00 mu=1.00 (rho 0.67): exact  0.444 | polynomial  0.466   gp-lite  0.447   random features  0.447  | gp sd 0.031
  lam=2.42 mu=1.00 (rho 0.81): exact  1.135 | polynomial  1.047   gp-lite  0.876   random features  0.833  | gp sd 0.052
  lam=2.70 mu=0.95 (rho 0.95): exact  6.015 | polynomial  1.930   gp-lite  0.877   random features  0.552  | gp sd 0.178
```

2026-11-02 | labs/L400/19-surrogates | $ python solution/surrogate.py | exit 0 | 36.5s

```text
expensive model: M/M/3 DES, 20,000 patients/run; 30 LHS training runs, 20 holdout runs
surrogate        holdout RMSE max error   (min of wait)
polynomial              0.037     0.079
gp-lite                 0.042     0.103
random features         0.049     0.133
(noise floor)           0.033   = holdout runs vs Erlang C
gp-lite 95% intervals cover 85% of holdout runs; params {'length_scales': [0.4, 0.4], 'noise': 0.01}
WHAT-IF (Erlang C = exact answer for this M/M/3; * = answered by the simulation, not the surrogate):
  lam=2.00 mu=1.00 (rho 0.67): exact  0.444 | polynomial  0.466   gp-lite  0.447   random features  0.447  | gp sd 0.031
  lam=2.42 mu=1.00 (rho 0.81): exact  1.135 | polynomial  1.109*  gp-lite  1.109*  random features  1.109* | gp sd 0.052
  lam=2.70 mu=0.95 (rho 0.95): exact  6.015 | polynomial  6.240*  gp-lite  6.240*  random features  6.240* | gp sd 0.178
```

2026-11-02 | labs/L400/19-surrogates | $ python try_it.py | exit 0 | 36.0s

```text
n=30: polynomial 0.037  gp-lite 0.042  random features 0.049
n=10: polynomial 0.043  gp-lite 0.066  random features 0.181
polynomial: raw 1.930, log-fit 2.583, exact 6.015
gp-lite: raw 0.877, log-fit 0.929, exact 6.015
```

2026-11-02 | labs/L400/19-surrogates | $ BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v | exit 1 | 70.1s

```text
[stderr]
test_far_outside_the_answer_is_within_20_percent_of_exact (test_build_task.TestEnvelopeGuard.test_far_outside_the_answer_is_within_20_percent_of_exact) ... FAIL
test_inside_the_envelope_the_surrogate_answers (test_build_task.TestEnvelopeGuard.test_inside_the_envelope_the_surrogate_answers) ... ok
test_just_outside_the_box_is_not_answered_by_the_surrogate (test_build_task.TestEnvelopeGuard.test_just_outside_the_box_is_not_answered_by_the_surrogate) ... FAIL
test_holdout_accuracy_and_calibrated_uncertainty (test_fitness.TestSurrogateFitness.test_holdout_accuracy_and_calibrated_uncertainty) ... ok
test_in_envelope_what_ifs_are_close_to_exact (test_fitness.TestSurrogateFitness.test_in_envelope_what_ifs_are_close_to_exact) ... ok
test_no_out_of_envelope_answer_comes_from_the_surrogate (test_fitness.TestSurrogateFitness.test_no_out_of_envelope_answer_comes_from_the_surrogate) ... FAIL

======================================================================
FAIL: test_far_outside_the_answer_is_within_20_percent_of_exact (test_build_task.TestEnvelopeGuard.test_far_outside_the_answer_is_within_20_percent_of_exact)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L400/19-surrogates/test_build_task.py", line 35, in test_far_outside_the_answer_is_within_20_percent_of_exact
    self.assertLess(abs(r["Wq"] - 6.015) / 6.015, 0.20)
AssertionError: 0.6791561633137768 not less than 0.2

======================================================================
FAIL: test_just_outside_the_box_is_not_answered_by_the_surrogate (test_build_task.TestEnvelopeGuard.test_just_outside_the_box_is_not_answered_by_the_surrogate)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L400/19-surrogates/test_build_task.py", line 31, in test_just_outside_the_box_is_not_answered_by_the_surrogate
    self.assertNotEqual(target.what_if(model, 2.42, 1.0)["source"], "surrogate")
AssertionError: 'surrogate' == 'surrogate'

======================================================================
FAIL: test_no_out_of_envelope_answer_comes_from_the_surrogate (test_fitness.TestSurrogateFitness.test_no_out_of_envelope_answer_comes_from_the_surrogate)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L400/19-surrogates/test_fitness.py", line 42, in test_no_out_of_envelope_answer_comes_from_the_surrogate
    self.assertNotEqual(target.what_if(self.gp, lam, mu)["source"], "surrogate")
AssertionError: 'surrogate' == 'surrogate'

----------------------------------------------------------------------
Ran 6 tests in 48.086s

FAILED (failures=3)
```

2026-11-02 | labs/L400/19-surrogates | $ python -m unittest test_fitness -v | exit 0 | 52.4s

```text
[stderr]
test_holdout_accuracy_and_calibrated_uncertainty (test_fitness.TestSurrogateFitness.test_holdout_accuracy_and_calibrated_uncertainty) ... ok
test_in_envelope_what_ifs_are_close_to_exact (test_fitness.TestSurrogateFitness.test_in_envelope_what_ifs_are_close_to_exact) ... ok
test_no_out_of_envelope_answer_comes_from_the_surrogate (test_fitness.TestSurrogateFitness.test_no_out_of_envelope_answer_comes_from_the_surrogate) ... ok

----------------------------------------------------------------------
Ran 3 tests in 18.012s

OK
```

## 20 — Large-scale and parallel simulation: reproducible streams, checkpoints and result storage

2026-11-02 | labs/L400/20-parallel-scale | $ python sweep.py | exit 0 | 28.5s

```text
clean run: 120 tasks on 2 spawn workers in 11.6 s (machine-dependent); checksum 5a2bd148609737c0
interrupted run: crashed after 48 committed results; resuming...
resumed run: +72 rows; checksum 8a6983e0e764e5cb -> DIFFERENT to the clean run
lam desks  mean Wq (min)  reps
1.6     3         0.181    10
1.6     4         0.036    10
1.6     5         0.007    10
2.0     3         0.453    10
2.0     4         0.083    10
2.0     5         0.019    10
2.4     3         1.042    10
2.4     4         0.182    10
2.4     5         0.042    10
2.8     3         3.909    10
2.8     4         0.353    10
2.8     5         0.080    10
```

2026-11-02 | labs/L400/20-parallel-scale | $ python solution/sweep.py | exit 0 | 37.6s

```text
clean run: 120 tasks on 2 spawn workers in 14.7 s (machine-dependent); checksum 38975a17ffb143cd
interrupted run: crashed after 48 committed results; resuming...
resumed run: +72 rows; checksum 38975a17ffb143cd -> IDENTICAL to the clean run
lam desks  mean Wq (min)  reps
1.6     3         0.189    10
1.6     4         0.038    10
1.6     5         0.008    10
2.0     3         0.415    10
2.0     4         0.090    10
2.0     5         0.021    10
2.4     3         1.125    10
2.4     4         0.195    10
2.4     5         0.043    10
2.8     3         3.847    10
2.8     4         0.353    10
2.8     5         0.084    10
```

2026-11-02 | labs/L400/20-parallel-scale | $ python storage_options.py | exit 0 | 37.0s

```text
write 5,000 rows (machine-dependent):
  CSV append + flush per row    0.098 s
  SQLite, commit every row     28.286 s
  SQLite, commit every 8 rows   7.528 s
  SQLite, one commit            0.068 s
crash mid-write, CSV: 1 malformed of 2 lines - the torn row swallowed the resumed row
crash mid-batch, SQLite: 16 rows, 16 distinct after resume (the torn batch rolled back)
```

2026-11-02 | labs/L400/20-parallel-scale | $ python scaling.py | exit 0 | 157.9s

```text
os.cpu_count() = 1
workers 1 chunksize 1:   10.6 tasks/s  (speed-up x1.00)
workers 1 chunksize 8:    6.7 tasks/s  (speed-up x0.64)
workers 2 chunksize 1:    5.4 tasks/s  (speed-up x0.51)
workers 2 chunksize 8:    2.7 tasks/s  (speed-up x0.25)
workers 4 chunksize 1:    3.9 tasks/s  (speed-up x0.37)
workers 4 chunksize 8:    4.7 tasks/s  (speed-up x0.44)
Amdahl serial fraction estimate (chunksize 8): f = 1.00
```

2026-11-02 | labs/L400/20-parallel-scale | $ python try_it.py | exit 0 | 292.7s

```text
fixed, crash after 9, resume on 1 worker: identical = True
fixed, crash after 33, resume on 1 worker: identical = True
shipped: task (7, 2) seed column = 20/[14]
fixed: task (7, 2) seed column = 20/[7, 2]
```

2026-11-02 | labs/L400/20-parallel-scale | $ BUILD_TARGET=mine python -m unittest test_build_task -v | exit 1 | 104.0s

```text
[stderr]
test_resume_on_one_worker_matches_clean_run (test_build_task.TestResumeIsReproducible.test_resume_on_one_worker_matches_clean_run) ... FAIL
test_resume_on_two_workers_matches_clean_run (test_build_task.TestResumeIsReproducible.test_resume_on_two_workers_matches_clean_run) ... FAIL

======================================================================
FAIL: test_resume_on_one_worker_matches_clean_run (test_build_task.TestResumeIsReproducible.test_resume_on_one_worker_matches_clean_run)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L400/20-parallel-scale/test_build_task.py", line 40, in test_resume_on_one_worker_matches_clean_run
    self.assertEqual(self.resumed("r1.db", 1, 10), target.checksum(self.dir / "clean.db"))
AssertionError: '659ab86dccd2e221' != 'ead92195f692dcbe'
- 659ab86dccd2e221
+ ead92195f692dcbe


======================================================================
FAIL: test_resume_on_two_workers_matches_clean_run (test_build_task.TestResumeIsReproducible.test_resume_on_two_workers_matches_clean_run)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L400/20-parallel-scale/test_build_task.py", line 44, in test_resume_on_two_workers_matches_clean_run
    self.assertEqual(self.resumed("r2.db", 2, 20), target.checksum(self.dir / "clean.db"))
AssertionError: '0c16465275f7758f' != 'ead92195f692dcbe'
- 0c16465275f7758f
+ ead92195f692dcbe


----------------------------------------------------------------------
Ran 2 tests in 99.827s

FAILED (failures=2)
```

2026-11-02 | labs/L400/20-parallel-scale | $ python -m unittest test_fitness -v | exit 0 | 196.1s

```text
[stderr]
test_any_crash_point_any_worker_count_same_results (test_fitness.TestSweepFitness.test_any_crash_point_any_worker_count_same_results) ... ok

----------------------------------------------------------------------
Ran 1 test in 190.527s

OK
```

## 21 — Model governance and V&V: model cards checked against evidence

2026-11-02 | labs/L400/21-governance-vv | $ python governance.py | exit 0 | 49.1s

```text
verification: 7 tests, 0 failures
validation vs Erlang C (10 reps x 20,000 patients):  rho  sim_Wq  exact  rel_err  rel_CI  ok
  0.50   0.157  0.158    0.4%   2.4%  True
  0.60   0.279  0.296    5.5%   3.5%  True
  0.70   0.528  0.547    3.5%   4.7%  True
  0.80   1.060  1.079    1.7%   9.9%  True
  0.85   1.573  1.623    3.1%   6.7%  True
  0.90   2.873  2.724    5.5%  11.9%  False
  0.95   6.127  6.047    1.3%  21.0%  False
validity envelope: utilisation <= 0.85; max error inside 5.5%; busiest hour in arrivals.csv needs 0.8
sensitivity (elasticity of Wq): {'lam': 6.01, 'mu': -7.02} -> most influential: mu
model_card.json: PUBLISHABLE; findings []
   [x] verification suite passes
   [x] validated envelope covers the busiest hour in the data
   [x] sensitivity results recorded
   [x] model and data versions pinned by hash
   [x] card claims match the evidence
draft_overclaiming.json: PUBLISHABLE; findings []
   [x] verification suite passes
   [x] validated envelope covers the busiest hour in the data
   [x] sensitivity results recorded
   [x] model and data versions pinned by hash
   [x] card claims match the evidence
```

2026-11-02 | labs/L400/21-governance-vv | $ python solution/governance.py | exit 0 | 38.2s

```text
verification: 7 tests, 0 failures
validation vs Erlang C (10 reps x 20,000 patients):  rho  sim_Wq  exact  rel_err  rel_CI  ok
  0.50   0.157  0.158    0.4%   2.4%  True
  0.60   0.279  0.296    5.5%   3.5%  True
  0.70   0.528  0.547    3.5%   4.7%  True
  0.80   1.060  1.079    1.7%   9.9%  True
  0.85   1.573  1.623    3.1%   6.7%  True
  0.90   2.873  2.724    5.5%  11.9%  False
  0.95   6.127  6.047    1.3%  21.0%  False
validity envelope: utilisation <= 0.85; max error inside 5.5%; busiest hour in arrivals.csv needs 0.8
sensitivity (elasticity of Wq): {'lam': 6.01, 'mu': -7.02} -> most influential: mu
model_card.json: PUBLISHABLE; findings []
   [x] verification suite passes
   [x] validated envelope covers the busiest hour in the data
   [x] sensitivity results recorded
   [x] model and data versions pinned by hash
   [x] card claims match the evidence
draft_overclaiming.json: BLOCKED; findings ['envelope claims utilisation <= 0.95, evidence supports 0.85', 'claims max error 2.0%, evidence shows 5.5%', "claims most influential input 'lam', evidence says 'mu'", 'code_sha256 is stale: re-run the evidence and bump model_version']
   [x] verification suite passes
   [x] validated envelope covers the busiest hour in the data
   [x] sensitivity results recorded
   [x] model and data versions pinned by hash
   [ ] card claims match the evidence
```

2026-11-02 | labs/L400/21-governance-vv | $ python agent_assist.py --fake | exit 0 | 4.3s

```text
1. agent drafted:
   Validity and evidence (draft):
   - Valid for utilisation up to 0.95 with 3 desks.
   - Mean wait within 2.0% of Erlang C across the range.
   - Results are most sensitive to the service rate (elasticity -7.02).
   - 7 of 7 tests pass.
2. code checked each claim against evidence.json:
   OVERCLAIM envelope     'utilisation up to 0.95'
   OVERCLAIM accuracy     'within 2.0% of Erlang C'
   OK        key input    'most sensitive to the service rate'
   OK        verification '7 of 7 tests pass'
3. numbers not found in the evidence (UNVERIFIED): 3, 2.0
4. code verdict: draft REJECTED - fix the claims, then re-run
```

2026-11-02 | labs/L400/21-governance-vv | $ python try_it.py | exit 0 | 57.0s

```text
accuracy requirement 10%: validated envelope utilisation <= 0.85
accuracy requirement 5%: validated envelope utilisation <= 0.5
committed data: no findings
one new row   : ['data_sha256 is stale: re-run the evidence and bump model_version']
```

2026-11-02 | labs/L400/21-governance-vv | $ BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v | exit 1 | 51.3s

```text
[stderr]
test_every_overclaim_in_the_draft_is_found (test_build_task.TestClaimChecks.test_every_overclaim_in_the_draft_is_found) ... 
  test_every_overclaim_in_the_draft_is_found (test_build_task.TestClaimChecks.test_every_overclaim_in_the_draft_is_found) (claim='envelope') ... FAIL
  test_every_overclaim_in_the_draft_is_found (test_build_task.TestClaimChecks.test_every_overclaim_in_the_draft_is_found) (claim='error') ... FAIL
  test_every_overclaim_in_the_draft_is_found (test_build_task.TestClaimChecks.test_every_overclaim_in_the_draft_is_found) (claim='influential') ... FAIL
  test_every_overclaim_in_the_draft_is_found (test_build_task.TestClaimChecks.test_every_overclaim_in_the_draft_is_found) (claim='code_sha256') ... FAIL
test_honest_card_has_no_findings (test_build_task.TestClaimChecks.test_honest_card_has_no_findings) ... ok
test_committed_card_matches_fresh_evidence (test_fitness.TestGovernanceFitness.test_committed_card_matches_fresh_evidence) ... ok
test_envelope_covers_the_busiest_hour (test_fitness.TestGovernanceFitness.test_envelope_covers_the_busiest_hour) ... ok
test_every_checklist_item_ticked (test_fitness.TestGovernanceFitness.test_every_checklist_item_ticked) ... ok
test_verification_green (test_fitness.TestGovernanceFitness.test_verification_green) ... ok

======================================================================
FAIL: test_every_overclaim_in_the_draft_is_found (test_build_task.TestClaimChecks.test_every_overclaim_in_the_draft_is_found) (claim='envelope')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L400/21-governance-vv/test_build_task.py", line 36, in test_every_overclaim_in_the_draft_is_found
    self.assertIn(word, findings)
AssertionError: 'envelope' not found in ''

======================================================================
FAIL: test_every_overclaim_in_the_draft_is_found (test_build_task.TestClaimChecks.test_every_overclaim_in_the_draft_is_found) (claim='error')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L400/21-governance-vv/test_build_task.py", line 36, in test_every_overclaim_in_the_draft_is_found
    self.assertIn(word, findings)
AssertionError: 'error' not found in ''

======================================================================
FAIL: test_every_overclaim_in_the_draft_is_found (test_build_task.TestClaimChecks.test_every_overclaim_in_the_draft_is_found) (claim='influential')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L400/21-governance-vv/test_build_task.py", line 36, in test_every_overclaim_in_the_draft_is_found
    self.assertIn(word, findings)
AssertionError: 'influential' not found in ''

======================================================================
FAIL: test_every_overclaim_in_the_draft_is_found (test_build_task.TestClaimChecks.test_every_overclaim_in_the_draft_is_found) (claim='code_sha256')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<scratch>/labs/L400/21-governance-vv/test_build_task.py", line 36, in test_every_overclaim_in_the_draft_is_found
    self.assertIn(word, findings)
AssertionError: 'code_sha256' not found in ''

----------------------------------------------------------------------
Ran 6 tests in 24.681s

FAILED (failures=4)
```

2026-11-02 | labs/L400/21-governance-vv | $ python -m unittest test_fitness -v | exit 0 | 56.1s

```text
[stderr]
test_committed_card_matches_fresh_evidence (test_fitness.TestGovernanceFitness.test_committed_card_matches_fresh_evidence) ... ok
test_envelope_covers_the_busiest_hour (test_fitness.TestGovernanceFitness.test_envelope_covers_the_busiest_hour) ... ok
test_every_checklist_item_ticked (test_fitness.TestGovernanceFitness.test_every_checklist_item_ticked) ... ok
test_verification_green (test_fitness.TestGovernanceFitness.test_verification_green) ... ok

----------------------------------------------------------------------
Ran 4 tests in 31.106s

OK
```

## 22 — Capstone: a digital twin of a service centre

2026-11-02 | labs/L400/22-capstone | $ python run_capstone.py | exit 0 | 463.4s

```text
{"milestone": "M1 input modelling", "pass": true, "service": "lognormal", "ks": {"lognormal": 0.0059, "normal": 0.1403, "exponential": 0.1762}, "max_rate_error": 0.07}
{"milestone": "M2 DES core verified", "pass": true, "sl_sim": 0.8376, "sl_erlang_c": 0.8365, "reproducible": true}
{"milestone": "M3 calibration + holdout validation", "pass": true, "patience_min": 4.5, "patience_plausible": [3.0, 5.5], "sl_mae_pp": 1.09, "abandon_mae_pp": 0.73}
{"milestone": "M4 sensitivity + staffing under SLA", "pass": true, "plan": [10, 19, 22, 25, 22, 19, 22, 24, 19, 15, 13, 11], "agent_hours": 221, "erlang_c_hours": 219, "flat_hours": 300, "erlang_c_day_abandon_max": 0.039, "elasticity_peak_sl": {"rate": -0.64, "mean_service": -0.68, "patience": -0.01}, "day_sl_min_low": 0.872, "day_abandon_max": 0.036}
{"milestone": "M5 parallel replications + live twin", "pass": true, "resume_identical": true, "alarm_delay_min": 75, "m_at_alarm": 1.201, "replan_from": "15:00", "extra_agent_hours": 14, "static_sl_after": 0.719, "twin_sl_after": 0.896}
{"milestone": "M6 governance pack + agent explanation", "pass": true, "card_findings": [], "review_flags": ["hour 15:00 plans for 6.16 calls/min > validated 5.6"], "agent_unverified": ["9"], "agent_publish": false, "decision": "235 agent-hours: plan [10, 19, 22, 25, 22, 19, 22, 28, 22, 18, 15, 13]"}
{"scorecard": "PASS", "passed": 6, "total": 6}
```

2026-11-02 | labs/L400/22-capstone | $ python try_it.py | exit 0 | 55.4s

```text
point estimates : 208 agent-hours, worst-hour mean abandonment 0.064
95% bounds      : 221 agent-hours, worst-hour mean abandonment 0.036
Erlang C only   : 219 agent-hours, worst-hour mean abandonment 0.036
```

2026-11-02 | labs/L400/22-capstone | $ python -m unittest test_fitness -v | exit 0 | 133.8s

```text
[stderr]
test_governance_card_is_current (test_fitness.TestCapstoneFitness.test_governance_card_is_current) ... ok
test_sla_holds_for_the_recommended_plan (test_fitness.TestCapstoneFitness.test_sla_holds_for_the_recommended_plan) ... ok
test_twin_alarm_timing (test_fitness.TestCapstoneFitness.test_twin_alarm_timing) ... ok

----------------------------------------------------------------------
Ran 3 tests in 89.819s

OK
```

## 23 — Foundations I: probability and stochastic processes for simulation

2026-11-02 | labs/L500/23-probability | $ python t1_wlln.py | exit 0 | 6.7s

```text
n      Chebyshev bound  observed P(|mean - 1| >= 0.2)
25     1.0000           0.3220
100    0.2500           0.0427
400    0.0625           0.0003
1600   0.0156           0.0000
bound holds for every n; it is loose (Chebyshev uses only the variance)
```

2026-11-02 | labs/L500/23-probability | $ python t2_clt.py | exit 0 | 6.9s

```text
n     P(Z_n <= 1.96)  KS distance to N(0,1)  skewness 2/sqrt(n)
1     0.9482          0.1587                 2.000
4     0.9524          0.0651                 1.000
16    0.9631          0.0324                 0.500
64    0.9696          0.0231                 0.250
256   0.9728          0.0121                 0.125
exact P(Z <= 1.96) = 0.9750; KS noise floor for 20,000 draws ~ 0.0096
```

2026-11-02 | labs/L500/23-probability | $ python t3_poisson.py | exit 0 | 8.0s

```text
events 9943 in 5000 time units (expected 10000)
mean gap 0.5025 (theory 1/lam = 0.5000); var 0.2550 (theory 1/lam^2 = 0.2500)
P(T > 0.25) observed 0.6063 theory exp(-lam t) = 0.6065
P(T > 0.5) observed 0.3692 theory exp(-lam t) = 0.3679
P(T > 1.0) observed 0.1375 theory exp(-lam t) = 0.1353
memoryless: P(T > 1.5 | T > 0.5) = 0.1411 vs P(T > 1.0) = 0.1375
N(1) per unit interval: mean 1.9886 var 2.0237 (Poisson: both = lam = 2.0)
P(N(1) = 0) observed 0.1388 theory 0.1353
```

2026-11-02 | labs/L500/23-probability | $ python t4_birth_death.py | exit 0 | 21.0s

```text
(a) pi from pi P = pi : [0.2439 0.4634 0.2927]
    every row of P^50 : [0.2439 0.4634 0.2927] max row spread < 1e-12
    simulated 200,000 : [0.2457 0.4633 0.2909]
(b) n:                  0       1       2       3       4      L
    (1-rho) rho^n    0.2000 0.1600 0.1280 0.1024 0.0819  4.000
    generator solve  0.2000 0.1600 0.1280 0.1024 0.0819  4.000
    CTMC simulation  0.2003 0.1612 0.1285 0.1025 0.0823  3.919
    Little's law: W = L / lam = 5.000 = 1/(mu - lam) = 5.000
```

## 24 — Foundations II: numerical methods - truncation error, order, stability, stiffness and floating point

2026-11-02 | labs/L500/24-numerics | $ python t1_euler_order.py | exit 0 | 18.1s

```text
h         local err   ratio  global err   ratio  observed order
0.20000   2.930e-02    -    4.397e-01    -    -
0.10000   7.415e-03   3.95  2.420e-01   1.82  0.862
0.05000   1.864e-03   3.98  1.275e-01   1.90  0.925
0.02500   4.674e-04   3.99  6.550e-02   1.95  0.961
0.01250   1.170e-04   3.99  3.321e-02   1.97  0.980
0.00625   2.928e-05   4.00  1.672e-02   1.99  0.990
local error falls ~4x per halving (O(h^2)); global ~2x (O(h)): N = 2/h steps each add O(h^2)
```

2026-11-02 | labs/L500/24-numerics | $ python t2_rk4_order.py | exit 0 | 0.7s

```text
(0) order conditions satisfied: 8/8 (sum b = 1, b.c = 1/2, b.c^2 = 1/3, b.Ac = 1/6, b.c^3 = 1/4, b.(c*Ac) = 1/8, b.Ac^2 = 1/12, b.AAc = 1/24)
(a) z = -0.130: RK4 step = R(z) to 0e+00; e^z - R(z) = -3.028e-07; z^5/120 = -3.094e-07
(a) z = -0.065: RK4 step = R(z) to 0e+00; e^z - R(z) = -9.565e-09; z^5/120 = -9.669e-09
(b) h         global err   ratio   observed order
    0.20000   1.089e-04        -   -
    0.10000   6.990e-06    15.59   3.962
    0.05000   4.421e-07    15.81   3.983
    0.02500   2.779e-08    15.91   3.992
    0.01250   1.742e-09    15.96   3.996
global error ~16x smaller per halving: O(h^4) (N = 2/h steps x O(h^5) local error)
```

2026-11-02 | labs/L500/24-numerics | $ python t3_stability.py | exit 0 | 20.4s

```text
(a) explicit Euler, lam = -50 (limit h = 2/50 = 0.04), |y| after 200 steps from y0 = 1:
    h = 0.039  |1 + h lam| = 0.950  |y_200| = 3.505e-05
    h = 0.040  |1 + h lam| = 1.000  |y_200| = 1.000e+00
    h = 0.041  |1 + h lam| = 1.050  |y_200| = 1.729e+04
(b) RK4 real-axis stability limit: z = -2.7853 (explicit Euler: -2)
(c) stiff y' = -1000(y - cos t) - sin t on [0, 2]; the solution cos t is smooth but lam = -1000:
    explicit Euler h = 0.0021  steps   952  error 2.673e+33
    explicit Euler h = 0.0019  steps  1053  error 6.368e-04
    implicit Euler h = 0.1    steps    20  error 1.923e-05
    implicit Euler h = 0.01   steps   200  error 2.061e-06
```

2026-11-02 | labs/L500/24-numerics | $ python t4_floating_point.py | exit 0 | 15.0s

```text
machine epsilon 2.220446049250313e-16 = 2^-52; unit roundoff u = 1.1102230246251565e-16
20,000 random decimals: max relative representation error 1.104e-16 <= u: True
0.1 + 0.2 == 0.3: False; ten x (acc += 0.1) = 0.9999999999999999; math.fsum = 1.0
cancellation: (1 - cos x)/x^2 at x = 1e-8 -> 0.0; stable 2 sin^2(x/2)/x^2 -> 0.5
forward difference of e^x at x = 1 (exact e):
    h = 1e-01  error 1.41e-01
    h = 1e-03  error 1.36e-03
    h = 1e-05  error 1.36e-05
    h = 1e-07  error 1.40e-07
    h = 1e-09  error 2.15e-07
    h = 1e-11  error 3.26e-05
    h = 1e-13  error 4.56e-04
    smallest error at h = 1e-07 (sqrt(eps) = 1.5e-08)
explicit Euler on y' = -y to t = 1, float32 vs float64 (truncation O(h) vs accumulated round-off):
    steps        10  float32 error 1.92e-02  float64 error 1.92e-02
    steps     1,000  float32 error 1.84e-04  float64 error 1.84e-04
    steps    10,000  float32 error 1.89e-05  float64 error 1.84e-05
    steps   100,000  float32 error 4.26e-07  float64 error 1.84e-06
    steps 1,000,000  float32 error 2.57e-05  float64 error 1.84e-07
float32 stops following O(h) beyond ~10^4 steps (u32 = 6e-8 per step accumulates; signs vary, so 10^5 is a lucky
partial cancellation); float64 keeps O(h) here because its round-off floor is ~10^9 times lower
```

## 25 — Foundations III: random number generation and Monte Carlo theory

2026-11-02 | labs/L500/25-rng-monte-carlo | $ python t1_lcg_period.py | exit 0 | 7.9s

```text
m = 64: 4096 (a, c) pairs, full period for 512; Hull-Dobell predicts all 4096/4096
m = 60: 3600 (a, c) pairs, full period for 16; Hull-Dobell predicts all 3600/3600
m = 81: 6561 (a, c) pairs, full period for 1458; Hull-Dobell predicts all 6561/6561
RANDU: a^2 mod 2^31 = 393225, (6a - 9) mod 2^31 = 393225
RANDU triples violating x2 = 6 x1 - 9 x0 (mod 2^31): 0 of 99998; distinct planes used: 15
lowest bit of an m = 2^32 LCG (a = 1664525, c = 1013904223): 10101010101010101 -> period 2
```

2026-11-02 | labs/L500/25-rng-monte-carlo | $ python t2_gof_tests.py | exit 0 | 24.0s

```text
mean X^2 over 400 PCG64 runs (k = 100): 99.06 (theory k - 1 = 99)
generator  1-D X^2 (99 df)  p      KS sqrt(n)D  p      3-D X^2 (7999 df)  p
PCG64      87.8             0.782  1.064       0.208  7868.5             0.849
Philox     116.5            0.111  0.997       0.273  7906.3             0.767
MT19937    83.8             0.863  0.597       0.869  8122.8             0.164
RANDU      76.1             0.958  0.636       0.814  151465.4           0
LCG low-bit serial pairs 00/01/10/11: [0, 10000, 0, 0]  X^2 = 30000 (3 df), p = 0
a pass is not proof of quality: tests can only reject; batteries (TestU01 BigCrush) run hundreds of them
```

2026-11-02 | labs/L500/25-rng-monte-carlo | $ python t3_mc_variance_is.py | exit 0 | 23.8s

```text
(a) e - 1 = 1.71828; sigma^2 = 0.24204
    N      sd of 2,000 estimates   sigma/sqrt(N)   mean of estimates
    100    0.05046                 0.04920         1.71770
    400    0.02413                 0.02460         1.71978
    1600   0.01245                 0.01230         1.71859
    6400   0.00625                 0.00615         1.71844
    log-log slope of sd vs N: -0.500 (theory -0.5)
(b) exact P(Z > 4) = 3.1671e-05
    naive,  N = 100,000: estimate 3.0000e-05; theory relative SE 0.562
    IS N(4,1), N = 10,000: estimate 3.1924e-05; sample relative SE 0.0212; theory 0.0212
    variance per sample: naive 3.167e-05 vs IS 4.525e-09 -> 6,999x fewer samples
```

2026-11-02 | labs/L500/25-rng-monte-carlo | $ python t4_antithetic.py | exit 0 | 8.6s

```text
f(u) = e^u: rho = (e - (e-1)^2) / sigma^2 = -0.9677; predicted gain 1/(1 + rho) = 30.9x
  same 1,000 evaluations: var plain 2.384e-04, antithetic 7.922e-06, observed gain 30.1x
f(u) = (u - 0.5)^2 (symmetric): observed gain 0.53x (theory 1/(1 + 1) = 0.50x)
```

2026-11-02 | labs/L500/25-rng-monte-carlo | $ python streams_demo.py | exit 0 | 4.5s

```text
PCG64: 1,001st output after drawing 1,000 == after advance(1000): True
Philox: word 1,000 via counter advance(250) equals the stream's word 1,000: True
SeedSequence.spawn -> independent streams, first draws: [0.9991, 0.7135, 0.721]
periods: PCG64 2^128; Philox4x64 2^256 - 1 (NumPy docs)
```

## 26 — Ethics and professional responsibility: models that make decisions about people

2026-11-02 | labs/L500/26-ethics | $ python aggregate_vs_individual.py | exit 0 | 9.9s

```text
teacher-exam correlation 0.80: distribution error 0.0000; same grade as exam 40.0%; within one grade 86.4%
teacher-exam correlation 0.90: distribution error 0.0000; same grade as exam 51.5%; within one grade 95.3%
exam vs an equally good re-sit: same grade 39.7%; within one 86.5%
small centres: a centre's top-two-grade share (true p = 0.26) estimated from 3 past years of n students each:
  n =   5: SD 0.113 (theory sqrt(p(1-p)/3n) = 0.113), relative error 43%
  n =   8: SD 0.090 (theory sqrt(p(1-p)/3n) = 0.090), relative error 34%
  n =  15: SD 0.065 (theory sqrt(p(1-p)/3n) = 0.065), relative error 25%
  n =  50: SD 0.036 (theory sqrt(p(1-p)/3n) = 0.036), relative error 14%
  n = 200: SD 0.018 (theory sqrt(p(1-p)/3n) = 0.018), relative error 7%
```

## 27 — Reading seminar: Metropolis & Ulam (1949) 'The Monte Carlo Method' and Sargent on verification and validation

2026-11-02 | labs/L500/27-readings | $ python branching_process.py | exit 0 | 15.4s

```text
analytic extinction probability q = 0.6863 (smallest root of q = exp(1.2(q - 1)))
Monte Carlo, 20,000 chains: 0.6842 +/- 0.0064 (95% CI); contains q: True
capped chains contribute bias < q^500 = 1.8e-82
```
