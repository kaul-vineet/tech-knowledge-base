"""Theorem 25.2 (goodness-of-fit tests for generators).
Pearson X^2 = sum (O_j - E_j)^2 / E_j over k equiprobable cells has E[X^2] = k - 1 exactly under H0 and tends to
chi-square(k - 1); sqrt(n) D_n (Kolmogorov-Smirnov) tends to the Kolmogorov distribution.
Checks: E[X^2] by repetition; modern generators pass; RANDU fails a 3-D test; an LCG's low bit fails a serial test."""
import numpy as np

from stats_util import chi2_sf, chi_square, kolmogorov_sf, ks_uniform

K, N = 100, 100_000
xs = [np.histogram(np.random.default_rng(s).random(N), bins=K, range=(0, 1))[0] for s in range(400)]
mean_x2 = np.mean([chi_square(c, N / K) for c in xs])
print(f"mean X^2 over 400 PCG64 runs (k = {K}): {mean_x2:.2f} (theory k - 1 = {K - 1})")
assert abs(mean_x2 - (K - 1)) < 3 * np.sqrt(2 * (K - 1) / 400)


def randu(n, seed=1):
    out, x = np.empty(n), seed
    for i in range(n):
        x = 65539 * x % 2**31
        out[i] = x / 2**31
    return out


gens = {
    "PCG64": np.random.Generator(np.random.PCG64(2025)).random,
    "Philox": np.random.Generator(np.random.Philox(2025)).random,
    "MT19937": np.random.Generator(np.random.MT19937(2025)).random,
    "RANDU": randu,
}
print("generator  1-D X^2 (99 df)  p      KS sqrt(n)D  p      3-D X^2 (7999 df)  p")
pvals = {}
for name, draw in gens.items():
    u = draw(200_000 * 3)
    c1 = np.histogram(u, bins=K, range=(0, 1))[0]
    x1 = chi_square(c1, u.size / K)
    t = ks_uniform(u[:10_000].tolist()) * np.sqrt(10_000)
    cells = np.floor(u.reshape(-1, 3) * 20).astype(int) @ np.array([400, 20, 1])  # non-overlapping triples, 20^3 cells
    x3 = chi_square(np.bincount(cells, minlength=8000), 200_000 / 8000)
    pvals[name] = chi2_sf(x3, 7999)
    print(f"{name:<10} {x1:<16.1f} {chi2_sf(x1, 99):.3f}  {t:<11.3f} {kolmogorov_sf(t):.3f}  {x3:<18.1f} {pvals[name]:.3g}")
assert pvals["RANDU"] < 1e-10 and min(pvals[g] for g in ("PCG64", "Philox", "MT19937")) > 0.001
x, bits = 12345, []
for _ in range(20_000):
    x = (1664525 * x + 1013904223) % 2**32
    bits.append(x & 1)
pairs = np.bincount(2 * np.array(bits[:-1:2]) + np.array(bits[1::2]), minlength=4)
x2 = chi_square(pairs, sum(pairs) / 4)
print(f"LCG low-bit serial pairs 00/01/10/11: {pairs.tolist()}  X^2 = {x2:.0f} (3 df), p = {chi2_sf(x2, 3):.3g}")
print("a pass is not proof of quality: tests can only reject; batteries (TestU01 BigCrush) run hundreds of them")
