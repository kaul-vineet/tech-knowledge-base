"""Small, dependency-free statistics helpers (no SciPy): chi-square tail and Kolmogorov tail probabilities."""
import math


def gammaincc(a, x):
    """Regularised upper incomplete gamma Q(a, x): series for x < a + 1, Lentz continued fraction otherwise."""
    if x <= 0:
        return 1.0
    lg = math.lgamma(a)
    if x < a + 1:
        term = total = 1.0 / a
        ap = a
        for _ in range(10_000):
            ap += 1
            term *= x / ap
            total += term
            if abs(term) < abs(total) * 1e-16:
                break
        return 1.0 - total * math.exp(-x + a * math.log(x) - lg)
    tiny = 1e-300
    b = x + 1 - a
    c, d = 1 / tiny, 1 / b
    h = d
    for i in range(1, 10_000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = tiny if abs(d) < tiny else d
        c = b + an / c
        c = tiny if abs(c) < tiny else c
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-16:
            break
    return math.exp(-x + a * math.log(x) - lg) * h


def chi2_sf(x, df):
    return gammaincc(df / 2, x / 2)


def kolmogorov_sf(t):
    """P(sqrt(n) D_n > t) for large n: 2 sum (-1)^(k-1) exp(-2 k^2 t^2)."""
    if t < 0.2:
        return 1.0
    return max(0.0, min(1.0, 2 * sum((-1) ** (k - 1) * math.exp(-2 * k * k * t * t) for k in range(1, 101))))


def chi_square(counts, expected):
    return sum((o - expected) ** 2 / expected for o in counts)


def ks_uniform(sample):
    """Kolmogorov-Smirnov statistic of a sample against U(0, 1)."""
    xs = sorted(sample)
    n = len(xs)
    return max(max((i + 1) / n - x, x - i / n) for i, x in enumerate(xs))


# anchors: the 95th percentile of chi-square(100) is 124.342; of chi-square(1) is 3.841; Kolmogorov 5% point 1.358
assert abs(chi2_sf(124.342, 100) - 0.05) < 1e-4 and abs(chi2_sf(3.841, 1) - 0.05) < 1e-4
assert abs(kolmogorov_sf(1.3581) - 0.05) < 1e-4
