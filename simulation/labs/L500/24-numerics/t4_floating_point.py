"""Theorem 24.4 (floating-point model, IEEE 754 binary64).
fl(x) = x (1 + d) with |d| <= u = 2^-53 (round to nearest); machine epsilon eps = 2^-52 is the gap after 1.0.
Consequences checked here: representation error, cancellation, and the truncation/round-off trade-off
(forward difference error ~ h/2 |f''| + 2u|f|/h, minimised near h ~ sqrt(eps))."""
import math
import random
from fractions import Fraction

import numpy as np

eps = 1.0
while 1.0 + eps / 2 > 1.0:
    eps /= 2
print(f"machine epsilon {eps!r} = 2^{math.log2(eps):.0f}; unit roundoff u = {eps / 2!r}")
rnd = random.Random(2404)
worst = 0.0
for _ in range(20_000):
    s = f"{rnd.randint(1, 10**9)}e{rnd.randint(-30, 30)}"
    worst = max(worst, abs(Fraction(float(s)) - Fraction(s)) / Fraction(s))
print(f"20,000 random decimals: max relative representation error {float(worst):.3e} <= u: {worst <= Fraction(1, 2**53)}")
acc = 0.0
for _ in range(10):
    acc += 0.1  # naive running sum: one rounding per addition
print(f"0.1 + 0.2 == 0.3: {0.1 + 0.2 == 0.3}; ten x (acc += 0.1) = {acc!r}; math.fsum = {math.fsum([0.1] * 10)!r}")
x = 1e-8
print(f"cancellation: (1 - cos x)/x^2 at x = 1e-8 -> {(1 - math.cos(x)) / x**2}; stable 2 sin^2(x/2)/x^2 -> {2 * math.sin(x / 2) ** 2 / x**2}")
print("forward difference of e^x at x = 1 (exact e):")
best = (1.0, None)
for k in range(1, 15, 2):
    h = 10.0**-k
    err = abs((math.exp(1 + h) - math.exp(1)) / h - math.e)
    best = min(best, (err, k))
    print(f"    h = 1e-{k:02d}  error {err:.2e}")
print(f"    smallest error at h = 1e-{best[1]:02d} (sqrt(eps) = {math.sqrt(eps):.1e})")
assert best[1] in (7, 9) and eps == 2.0**-52 and worst <= Fraction(1, 2**53)
print("explicit Euler on y' = -y to t = 1, float32 vs float64 (truncation O(h) vs accumulated round-off):")
for n in (10, 1000, 10_000, 100_000, 1_000_000):
    errs = []
    for dt in (np.float32, np.float64):
        h, y = dt(1.0 / n), dt(1.0)
        for _ in range(n):
            y = y - h * y
        errs.append(abs(float(y) - math.exp(-1)))
    print(f"    steps {n:>9,}  float32 error {errs[0]:.2e}  float64 error {errs[1]:.2e}")
print("float32 stops following O(h) beyond ~10^4 steps (u32 = 6e-8 per step accumulates; signs vary, so 10^5 is a lucky")
print("partial cancellation); float64 keeps O(h) here because its round-off floor is ~10^9 times lower")
assert errs[0] > 10 * errs[1]  # at 10^6 steps float32 is round-off dominated
