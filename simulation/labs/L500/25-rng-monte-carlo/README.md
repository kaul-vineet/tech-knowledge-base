# 25 · Foundations III: random number generation and Monte Carlo theory

Each script checks one theorem of lesson 25. `stats_util.py` holds dependency-free chi-square and Kolmogorov tail functions (anchored to tabulated 5% points); `streams_demo.py` shows PCG64 `advance()` and Philox counters.

Read the concept note first: `../../../content/concepts/L500/25-rng-monte-carlo.md`; the statements, proofs and problem set are in `../../../content/L500.json` (lesson 25). Needs only Python 3.12 + numpy (same commands on macOS and Windows; use `cd labs\L500\25-rng-monte-carlo` on Windows).

## Run
```bash
python t1_lcg_period.py
python t2_gof_tests.py
python t3_mc_variance_is.py
python t4_antithetic.py
python streams_demo.py
python -m unittest -v      # runs every script, checks exit code and (on Linux) the exact recorded output
```

## Expected output (real runs, Python 3.12.15 + numpy 2.5.3, Linux)

### `t1_lcg_period.py` - Theorem 25.1 - Full period of an LCG (Hull-Dobell) and the RANDU planes
```
m = 64: 4096 (a, c) pairs, full period for 512; Hull-Dobell predicts all 4096/4096
m = 60: 3600 (a, c) pairs, full period for 16; Hull-Dobell predicts all 3600/3600
m = 81: 6561 (a, c) pairs, full period for 1458; Hull-Dobell predicts all 6561/6561
RANDU: a^2 mod 2^31 = 393225, (6a - 9) mod 2^31 = 393225
RANDU triples violating x2 = 6 x1 - 9 x0 (mod 2^31): 0 of 99998; distinct planes used: 15
lowest bit of an m = 2^32 LCG (a = 1664525, c = 1013904223): 10101010101010101 -> period 2
```

### `t2_gof_tests.py` - Theorem 25.2 - Goodness-of-fit tests for generators
```
mean X^2 over 400 PCG64 runs (k = 100): 99.06 (theory k - 1 = 99)
generator  1-D X^2 (99 df)  p      KS sqrt(n)D  p      3-D X^2 (7999 df)  p
PCG64      87.8             0.782  1.064       0.208  7868.5             0.849
Philox     116.5            0.111  0.997       0.273  7906.3             0.767
MT19937    83.8             0.863  0.597       0.869  8122.8             0.164
RANDU      76.1             0.958  0.636       0.814  151465.4           0
LCG low-bit serial pairs 00/01/10/11: [0, 10000, 0, 0]  X^2 = 30000 (3 df), p = 0
a pass is not proof of quality: tests can only reject; batteries (TestU01 BigCrush) run hundreds of them
```

### `t3_mc_variance_is.py` - Theorem 25.3 - The Monte Carlo estimator, its 1/sqrt(N) error, and importance sampling
```
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

### `t4_antithetic.py` - Theorem 25.4 - Antithetic variates: the covariance argument
```
f(u) = e^u: rho = (e - (e-1)^2) / sigma^2 = -0.9677; predicted gain 1/(1 + rho) = 30.9x
  same 1,000 evaluations: var plain 2.384e-04, antithetic 7.922e-06, observed gain 30.1x
f(u) = (u - 0.5)^2 (symmetric): observed gain 0.53x (theory 1/(1 + 1) = 0.50x)
```

### `streams_demo.py`
```
PCG64: 1,001st output after drawing 1,000 == after advance(1000): True
Philox: word 1,000 via counter advance(250) equals the stream's word 1,000: True
SeedSequence.spawn -> independent streams, first draws: [0.9991, 0.7135, 0.721]
periods: PCG64 2^128; Philox4x64 2^256 - 1 (NumPy docs)
```

## Notes
- Every generator is seeded; outputs are identical run to run. On macOS/Windows the asserts must pass; last digits of a few floating-point values may differ with a different libm (pending CI).
- Run time: a few seconds per script (the M/M/1 simulation in lesson 23 and the RANDU loops in lesson 25 are pure-Python loops).
