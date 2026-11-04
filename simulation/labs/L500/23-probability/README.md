# 23 · Foundations I: probability and stochastic processes

Each script checks one theorem of lesson 23 numerically and asserts its prediction (exit code 1 if the theorem's claim fails).

Read the concept note first: `../../../content/concepts/L500/23-probability-foundations.md`; the statements, proofs and problem set are in `../../../content/L500.json` (lesson 23). Needs only Python 3.12 + numpy (same commands on macOS and Windows; use `cd labs\L500\23-probability` on Windows).

## Run
```bash
python t1_wlln.py
python t2_clt.py
python t3_poisson.py
python t4_birth_death.py
python -m unittest -v      # runs every script, checks exit code and (on Linux) the exact recorded output
```

## Expected output (real runs, Python 3.12.15 + numpy 2.5.3, Linux)

### `t1_wlln.py` - Theorem 23.1 - Weak law of large numbers (Chebyshev proof)
```
n      Chebyshev bound  observed P(|mean - 1| >= 0.2)
25     1.0000           0.3220
100    0.2500           0.0427
400    0.0625           0.0003
1600   0.0156           0.0000
bound holds for every n; it is loose (Chebyshev uses only the variance)
```

### `t2_clt.py` - Theorem 23.2 - Central limit theorem (Lindeberg-Levy)
```
n     P(Z_n <= 1.96)  KS distance to N(0,1)  skewness 2/sqrt(n)
1     0.9482          0.1587                 2.000
4     0.9524          0.0651                 1.000
16    0.9631          0.0324                 0.500
64    0.9696          0.0231                 0.250
256   0.9728          0.0121                 0.125
exact P(Z <= 1.96) = 0.9750; KS noise floor for 20,000 draws ~ 0.0096
```

### `t3_poisson.py` - Theorem 23.3 - Poisson process has exponential inter-arrival times
```
events 9943 in 5000 time units (expected 10000)
mean gap 0.5025 (theory 1/lam = 0.5000); var 0.2550 (theory 1/lam^2 = 0.2500)
P(T > 0.25) observed 0.6063 theory exp(-lam t) = 0.6065
P(T > 0.5) observed 0.3692 theory exp(-lam t) = 0.3679
P(T > 1.0) observed 0.1375 theory exp(-lam t) = 0.1353
memoryless: P(T > 1.5 | T > 0.5) = 0.1411 vs P(T > 1.0) = 0.1375
N(1) per unit interval: mean 1.9886 var 2.0237 (Poisson: both = lam = 2.0)
P(N(1) = 0) observed 0.1388 theory 0.1353
```

### `t4_birth_death.py` - Theorem 23.4 - Stationary distributions; the M/M/1 queue from birth-death balance
```
(a) pi from pi P = pi : [0.2439 0.4634 0.2927]
    every row of P^50 : [0.2439 0.4634 0.2927] max row spread < 1e-12
    simulated 200,000 : [0.2457 0.4633 0.2909]
(b) n:                  0       1       2       3       4      L
    (1-rho) rho^n    0.2000 0.1600 0.1280 0.1024 0.0819  4.000
    generator solve  0.2000 0.1600 0.1280 0.1024 0.0819  4.000
    CTMC simulation  0.2003 0.1612 0.1285 0.1025 0.0823  3.919
    Little's law: W = L / lam = 5.000 = 1/(mu - lam) = 5.000
```

## Notes
- Every generator is seeded; outputs are identical run to run. On macOS/Windows the asserts must pass; last digits of a few floating-point values may differ with a different libm (pending CI).
- Run time: a few seconds per script (the M/M/1 simulation in lesson 23 and the RANDU loops in lesson 25 are pure-Python loops).
