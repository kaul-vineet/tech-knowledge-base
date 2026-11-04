"""Lesson 24 - statistics for evaluating agents (Python standard library only).

Pass rates are binomial proportions; Wilson intervals; sample size to detect a regression;
paired comparisons with McNemar's exact test; multiple-comparison control.

    python eval_stats.py              demo on lesson 12's golden-set numbers
    python eval_stats.py check T1     numerical check of theorem T1 (T1..T4)
"""
import math
import random
import sys
from statistics import NormalDist

Z = NormalDist()


def z_of(conf):
    """Two-sided critical value, e.g. 0.95 -> 1.959964."""
    return Z.inv_cdf(1 - (1 - conf) / 2)


def binom_pmf(k, n, p):
    return math.comb(n, k) * p**k * (1 - p) ** (n - k)


def binom_cdf(k, n, p):
    return sum(binom_pmf(i, n, p) for i in range(0, k + 1))


def wald(x, n, conf=0.95):
    p, z = x / n, z_of(conf)
    h = z * math.sqrt(p * (1 - p) / n)
    return p - h, p + h


def wilson(x, n, conf=0.95):
    """Invert the score test |p_hat - p| <= z sqrt(p(1-p)/n) (Wilson 1927)."""
    p, z = x / n, z_of(conf)
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z / (1 + z * z / n) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, centre - half), min(1.0, centre + half)


def score_roots_by_bisection(x, n, conf=0.95):
    """Same interval found numerically: the p where (p_hat - p)^2 = z^2 p(1-p)/n."""
    p_hat, z = x / n, z_of(conf)
    f = lambda p: (p_hat - p) ** 2 - z * z * p * (1 - p) / n

    def bisect(lo, hi):
        for _ in range(200):
            mid = (lo + hi) / 2
            if (f(lo) > 0) == (f(mid) > 0):
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    lower = 0.0 if f(0.0) <= 0 else bisect(0.0, p_hat)
    upper = 1.0 if f(1.0) <= 0 else bisect(p_hat, 1.0)
    return lower, upper


def coverage(method, n, p, conf=0.95):
    """Exact coverage probability: sum of P(X=x) over the x whose interval contains the true p."""
    return sum(binom_pmf(x, n, p) for x in range(n + 1) if method(x, n, conf)[0] <= p <= method(x, n, conf)[1])


def sample_size(p0, p1, alpha=0.05, power=0.8):
    """One-sided test of H0: p = p0 against a drop to p1 < p0 (normal approximation)."""
    za, zb = Z.inv_cdf(1 - alpha), Z.inv_cdf(power)
    n = ((za * math.sqrt(p0 * (1 - p0)) + zb * math.sqrt(p1 * (1 - p1))) / (p0 - p1)) ** 2
    return math.ceil(n)


def exact_power(n, p0, p1, alpha=0.05):
    """Reject 'no regression' when X <= c, c the largest count with P(X <= c | p0) <= alpha."""
    c = -1
    while binom_cdf(c + 1, n, p0) <= alpha:
        c += 1
    size = binom_cdf(c, n, p0) if c >= 0 else 0.0
    power = binom_cdf(c, n, p1) if c >= 0 else 0.0
    return c, size, power


def mcnemar_exact(b, c):
    """Two-sided exact p-value; b = old passes/new fails, c = old fails/new passes (discordant pairs)."""
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(0, min(b, c) + 1)) / 2**n
    return min(1.0, 2 * tail)


def mcnemar_chi2(b, c, correction=True):
    stat = (abs(b - c) - (1 if correction else 0)) ** 2 / (b + c)
    return stat, math.erfc(math.sqrt(stat / 2))  # chi-square(1) upper tail


def two_proportion_p(x1, x2, n):
    """Unpaired two-sided z-test p-value: what you get if you ignore the pairing."""
    p = (x1 + x2) / (2 * n)
    se = math.sqrt(p * (1 - p) * 2 / n)
    zstat = (x1 / n - x2 / n) / se
    return 2 * (1 - Z.cdf(abs(zstat)))


def fwer_independent(alpha, m):
    return 1 - (1 - alpha) ** m


def exact_lower_test_size(n, p0, alpha):
    """Attained size of the exact one-sided binomial test (always <= alpha)."""
    return exact_power(n, p0, p0, alpha)[1]


# ---------------------------------------------------------------- theorem checks
def check_T1():
    lines = []
    for x, n in ((20, 20), (18, 20), (180, 200)):
        w, b, wd = wilson(x, n), score_roots_by_bisection(x, n), wald(x, n)
        lines.append(f"{x}/{n}: Wilson [{w[0]:.4f}, {w[1]:.4f}]  bisection [{b[0]:.4f}, {b[1]:.4f}]  "
                     f"Wald [{wd[0]:.4f}, {wd[1]:.4f}]  agree to 1e-9: {max(abs(w[0]-b[0]), abs(w[1]-b[1])) < 1e-9}")
    rnd = random.Random(0)
    xs = [sum(rnd.random() < 0.9 for _ in range(50)) for _ in range(4000)]
    mean = sum(x / 50 for x in xs) / len(xs)
    var = sum((x / 50 - mean) ** 2 for x in xs) / (len(xs) - 1)
    lines.append(f"4000 simulated suites, n=50, p=0.9: mean p_hat {mean:.4f}; var {var:.5f} vs p(1-p)/n = {0.9 * 0.1 / 50:.5f}")
    for n, p in ((20, 0.95), (20, 0.90), (50, 0.95), (200, 0.95)):
        lines.append(f"exact coverage of nominal 95 %: n={n:>3} p={p:.2f}  Wald {coverage(wald, n, p):.4f}  Wilson {coverage(wilson, n, p):.4f}")
    return lines


def check_T2():
    lines = []
    for p0, p1 in ((0.90, 0.85), (0.95, 0.90), (0.90, 0.80)):
        n = sample_size(p0, p1)
        c, size, power = exact_power(n, p0, p1)
        lines.append(f"detect {p0:.2f} -> {p1:.2f} (alpha 0.05 one-sided, power 0.80): n = {n}; exact test rejects if passes <= {c}: "
                     f"size {size:.4f}, power {power:.4f}")
    c, size, power = exact_power(20, 0.95, 0.90)
    lines.append(f"lesson 12 golden set n=20, 0.95 -> 0.90: reject if passes <= {c}; size {size:.4f}; power {power:.4f}")
    lines.append(f"n needed scales with 1/delta^2: n(0.90->0.85) / n(0.90->0.80) = {sample_size(0.90, 0.85) / sample_size(0.90, 0.80):.2f}")
    return lines


def check_T3():
    lines = []
    n_disc = 20
    size = sum(math.comb(n_disc, b) / 2**n_disc for b in range(n_disc + 1) if mcnemar_exact(b, n_disc - b) <= 0.05)
    lines.append(f"exact McNemar, 20 discordant pairs: P(reject | H0) = {size:.4f} <= 0.05")
    b, c, n = 15, 5, 200
    old_pass, new_pass = 170, 160  # 155 pass both; 15 old-only; 5 new-only; 25 fail both
    stat, p_chi = mcnemar_chi2(b, c)
    lines.append(f"paired suite n={n}: old {old_pass}, new {new_pass}, b={b}, c={c}: exact p {mcnemar_exact(b, c):.4f}; "
                 f"chi2 (cc) {stat:.3f}, p {p_chi:.4f}")
    lines.append(f"same counts, unpaired two-proportion z-test: p {two_proportion_p(old_pass, new_pass, n):.4f} (pairing ignored)")
    rnd = random.Random(1)
    rej = 0
    for _ in range(2000):
        bb = sum(rnd.random() < 0.5 for _ in range(n_disc))
        rej += mcnemar_exact(bb, n_disc - bb) <= 0.05
    lines.append(f"2000 simulated H0 suites (20 discordant): rejection rate {rej / 2000:.4f}")
    return lines


def check_T4():
    lines = []
    for m in (1, 5, 20):
        lines.append(f"m={m:>2} independent tests at 0.05: FWER = {fwer_independent(0.05, m):.4f}; "
                     f"Bonferroni 0.05/m: FWER = {fwer_independent(0.05 / m, m):.4f}")
    sizes = [exact_lower_test_size(n, 0.9, 0.05 / 20) for n in (30, 40, 50, 60, 80)] * 4
    fw = 1 - math.prod(1 - s for s in sizes)
    lines.append(f"20 category gates (exact one-sided tests, alpha 0.05/20, p0 0.9): attained FWER {fw:.4f} <= union bound {sum(sizes):.4f} <= 0.05")
    rnd = random.Random(2)
    any_fp = 0
    for _ in range(2000):
        any_fp += any(rnd.random() < 0.05 for _ in range(20))
    lines.append(f"2000 simulated releases with 20 null categories at 0.05 each: P(at least one false alarm) = {any_fp / 2000:.4f}")
    return lines


CHECKS = {"T1": check_T1, "T2": check_T2, "T3": check_T3, "T4": check_T4}


def demo():
    print("lesson 12 golden set (20 cases):")
    for x in (20, 18):
        lo, hi = wilson(x, 20)
        print(f"  {x}/20 = {x / 20:.0%}  Wilson 95 % [{lo:.3f}, {hi:.3f}]")
    print(f"  cases to detect a 5-point drop from 90 %: {sample_size(0.90, 0.85)}")
    print(f"  v1 vs v2 paired (2 regressions, 0 fixes): McNemar exact p = {mcnemar_exact(2, 0):.3f}")
    print(f"  checking 6 categories at 0.05 each: P(any false alarm) = {fwer_independent(0.05, 6):.3f}")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "check":
        print("\n".join(CHECKS[sys.argv[2]]()))
    else:
        demo()
