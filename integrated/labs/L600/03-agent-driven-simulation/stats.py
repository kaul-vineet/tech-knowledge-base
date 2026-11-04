"""Exact Student-t quantiles (no SciPy) and the confidence intervals the pipeline decides with.

warmup.t975 (L200 #10) is a Cornish-Fisher approximation, documented as good for df >= 9 only; with 3 replications
(df 2) it gives 3.85 instead of 4.30 - too narrow a CI exactly where the agent is tempted to over-claim.
"""
import math


def _betacf(a, b, x, eps=1e-15, itmax=300):
    """Continued fraction for the regularised incomplete beta (modified Lentz)."""
    tiny, qab, qap, qam = 1e-300, a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        for aa in (m * (b - m) * x / ((qam + m2) * (a + m2)), -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))):
            d = 1.0 + aa * d
            d = 1.0 / (d if abs(d) > tiny else tiny)
            c = 1.0 + aa / c
            c = c if abs(c) > tiny else tiny
            h *= d * c
        if abs(d * c - 1.0) < eps:
            break
    return h


def betainc(a, b, x):
    if x <= 0.0 or x >= 1.0:
        return 0.0 if x <= 0.0 else 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x)
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * _betacf(b, a, 1.0 - x) / b


def t_cdf(t, df):
    tail = 0.5 * betainc(df / 2.0, 0.5, df / (df + t * t))
    return 1.0 - tail if t >= 0 else tail


def t_quantile(p, df):
    lo, hi = 0.0, 1e4
    for _ in range(200):  # bisection: robust, 1e-12 is plenty
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if t_cdf(mid, df) < p else (lo, mid)
    return (lo + hi) / 2


def mean_sd(xs):
    n = len(xs)
    m = math.fsum(xs) / n
    return m, math.sqrt(math.fsum((x - m) ** 2 for x in xs) / (n - 1)) if n > 1 else float("inf")


def mean_ci(xs, conf=0.95):
    m, s = mean_sd(xs)
    return m, t_quantile(0.5 + conf / 2, len(xs) - 1) * s / math.sqrt(len(xs))


def welch_ci(a, b, conf=0.95):
    """CI for mean(b) - mean(a), independent streams, unequal variances (Welch-Satterthwaite df)."""
    (ma, sa), (mb, sb) = mean_sd(a), mean_sd(b)
    va, vb = sa * sa / len(a), sb * sb / len(b)
    df = (va + vb) ** 2 / (va * va / (len(a) - 1) + vb * vb / (len(b) - 1))
    hw = t_quantile(0.5 + conf / 2, df) * math.sqrt(va + vb)
    return mb - ma, hw, df
