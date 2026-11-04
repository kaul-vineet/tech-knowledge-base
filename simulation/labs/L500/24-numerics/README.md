# 24 · Foundations II: numerical methods

Each script checks one theorem of lesson 24 (Euler order, RK4 order conditions, stability/stiffness, floating point).

Read the concept note first: `../../../content/concepts/L500/24-numerical-methods.md`; the statements, proofs and problem set are in `../../../content/L500.json` (lesson 24). Needs only Python 3.12 + numpy (same commands on macOS and Windows; use `cd labs\L500\24-numerics` on Windows).

## Run
```bash
python t1_euler_order.py
python t2_rk4_order.py
python t3_stability.py
python t4_floating_point.py
python -m unittest -v      # runs every script, checks exit code and (on Linux) the exact recorded output
```

## Expected output (real runs, Python 3.12.15 + numpy 2.5.3, Linux)

### `t1_euler_order.py` - Theorem 24.1 - Explicit Euler: local error O(h^2), global error O(h)
```
h         local err   ratio  global err   ratio  observed order
0.20000   2.930e-02    -    4.397e-01    -    -
0.10000   7.415e-03   3.95  2.420e-01   1.82  0.862
0.05000   1.864e-03   3.98  1.275e-01   1.90  0.925
0.02500   4.674e-04   3.99  6.550e-02   1.95  0.961
0.01250   1.170e-04   3.99  3.321e-02   1.97  0.980
0.00625   2.928e-05   4.00  1.672e-02   1.99  0.990
local error falls ~4x per halving (O(h^2)); global ~2x (O(h)): N = 2/h steps each add O(h^2)
```

### `t2_rk4_order.py` - Theorem 24.2 - Classical RK4 is fourth order
```
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

### `t3_stability.py` - Theorem 24.3 - Absolute stability of explicit Euler; stiffness
```
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

### `t4_floating_point.py` - Theorem 24.4 - IEEE 754 rounding model and its consequences
```
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

## Notes
- Every generator is seeded; outputs are identical run to run. On macOS/Windows the asserts must pass; last digits of a few floating-point values may differ with a different libm (pending CI).
- Run time: a few seconds per script (the M/M/1 simulation in lesson 23 and the RANDU loops in lesson 25 are pure-Python loops).
