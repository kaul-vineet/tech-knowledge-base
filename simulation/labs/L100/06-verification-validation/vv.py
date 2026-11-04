"""L100 "Is the model right?" -- verification and validation of a single-server queue model.

Model: customer waits via Lindley's rule  W[next] = max(0, W + service - gap_to_next_arrival).
1. Reproducibility: same seed -> identical output.
2. Validation vs an analytic result: replications + 95% CI must contain the M/M/1 formula.
3. Sensitivity: vary ONE parameter (arrival rate) and watch the output.
(Verification of the model rules lives in test_vv.py.)

python vv.py
"""
import hashlib
import random
import statistics

MU = 1.0  # service rate per minute
T_975 = {9: 2.262}  # Student t quantile for a 95% CI with 10 replications (9 degrees of freedom)


def next_wait(w, service, gap):
    return max(0.0, w + service - gap)  # model rule under test: a wait is never negative


def waits(n, lam, seed, mu=MU, rule=next_wait):
    rng = random.Random(seed)
    w, out = 0.0, []
    for _ in range(n):
        out.append(w)
        w = rule(w, rng.expovariate(mu), rng.expovariate(lam))
    return out


def mean_wait(n, lam, seed, warmup=5_000):
    return statistics.fmean(waits(n, lam, seed)[warmup:])  # drop the warm-up: the queue starts empty


def formula(lam, mu=MU):
    return lam / (mu * (mu - lam))


def replicate(lam, reps=10, n=50_000):
    means = [mean_wait(n, lam, seed) for seed in range(1, reps + 1)]  # independent replications = independent seeds
    m, s = statistics.fmean(means), statistics.stdev(means)
    half = T_975[reps - 1] * s / reps ** 0.5
    return m, half


def main():
    # hash values rounded to 9 decimals: a last-bit libm difference (macOS / Windows / Linux) must not change it
    digest = lambda seed: hashlib.sha256(repr([round(w, 9) for w in waits(1000, 0.8, seed)]).encode()).hexdigest()[:12]
    print(f"1. reproducibility: seed 1 -> {digest(1)}, seed 1 again -> {digest(1)}, seed 2 -> {digest(2)}")
    m, half = replicate(0.8)
    ok = abs(m - formula(0.8)) <= half
    print(f"2. validation (lam=0.8): simulated {m:.3f} +/- {half:.3f} min vs formula {formula(0.8):.3f} -> {'PASS' if ok else 'FAIL'}")
    print("3. sensitivity to arrival rate (utilisation = lam/mu):")
    for lam in (0.5, 0.6, 0.7, 0.8, 0.9):
        m, half = replicate(lam)
        print(f"   lam={lam:.1f}  simulated {m:6.3f} +/- {half:.3f}   formula {formula(lam):6.3f}")


if __name__ == "__main__":
    main()
