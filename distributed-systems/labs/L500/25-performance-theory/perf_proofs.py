"""Lesson 25 numerical checks (stdlib only, seeded: identical output on every run and OS).

python perf_proofs.py          all four checks (this output is quoted in content/L500.json)
python perf_proofs.py tail     one check: mm1 | little | tail | usl

T25.1 M/M/1: P(N = n) = (1 - rho) rho^n, L = rho / (1 - rho), W = 1 / (mu - lambda), against a simulation.
T25.2 Little's law L = lambda W: exact on a window that starts and ends empty, approximate on any long window.
T25.3 Tail amplification: P(any of n leaves slow) = 1 - (1 - p)^n, against a Monte Carlo fan-out.
T25.4 Amdahl S(p) = p / (1 + sigma (p - 1)) <= 1 / sigma; USL peak p* = sqrt((1 - sigma) / kappa), fitted to a
      simulated lock-contention + coherency system.
"""
import heapq
import math
import random
import sys


# ---------- single-server FIFO queue simulation (Lindley recursion) ----------
def simulate_queue(rng, n, arrival, service):
    """Return (arrival_times, departure_times) for a FIFO single server."""
    t, free_at, arr, dep = 0.0, 0.0, [], []
    for _ in range(n):
        t += arrival(rng)
        start = max(t, free_at)
        free_at = start + service(rng)
        arr.append(t)
        dep.append(free_at)
    return arr, dep


def time_average_n(arr, dep, t_end):
    """Integral of n(t) over [0, t_end] / t_end and fraction of time with n(t) = k, k = 0..4."""
    events = sorted([(a, 1) for a in arr if a < t_end] + [(d, -1) for d in dep if d < t_end])
    n, last, area, time_at = 0, 0.0, 0.0, [0.0] * 5
    for t, step in events:
        area += n * (t - last)
        if n < 5:
            time_at[n] += t - last
        n, last = n + step, t
    area += n * (t_end - last)
    if n < 5:
        time_at[n] += t_end - last
    return area / t_end, [x / t_end for x in time_at]


def check_mm1(n=400_000, seed=25):
    lines = [f"T25.1 M/M/1, mu = 1 per ms, {n:,} customers per load (seeded simulation vs closed form)"]
    for lam in (0.5, 0.8, 0.9):
        rng = random.Random(seed)
        arr, dep = simulate_queue(rng, n, lambda r: r.expovariate(lam), lambda r: r.expovariate(1.0))
        w = sum(d - a for a, d in zip(arr, dep)) / n
        t_end = arr[-1]
        l_avg, p = time_average_n(arr, dep, t_end)
        rho = lam
        lines.append(f"  rho={rho:.1f}: W sim {w:6.3f} theory {1 / (1 - rho):6.3f} | L sim {l_avg:6.3f} "
                     f"theory {rho / (1 - rho):6.3f} | P(N=0) sim {p[0]:.3f} theory {1 - rho:.3f} | "
                     f"P(N=2) sim {p[2]:.3f} theory {(1 - rho) * rho ** 2:.3f}")
    return lines


def check_little(n=200_000, seed=7):
    """G/G/1 with deterministic-plus-jitter arrivals and log-normal service: no Markov assumption anywhere."""
    rng = random.Random(seed)
    arr, dep = simulate_queue(rng, n, lambda r: 1.25 + r.uniform(-0.5, 0.5), lambda r: r.lognormvariate(-0.2, 0.6))
    # exact identity: pick a window [0, T] that ends when the system is empty
    t_cut = None
    for i in range(n // 2, n - 1):
        if dep[i] <= arr[i + 1]:          # customer i leaves before i+1 arrives: system empty in between
            t_cut, k = dep[i], i + 1
            break
    area, _ = time_average_n(arr[:k], dep[:k], t_cut)
    area *= t_cut
    sum_w = sum(d - a for a, d in zip(arr[:k], dep[:k]))
    lam, w = k / t_cut, sum_w / k
    lines = ["T25.2 Little's law on a G/G/1 queue (uniform-jitter arrivals, log-normal service), seeded",
             f"  window [0, {t_cut:,.3f}] starts and ends empty, {k:,} customers:",
             f"    area under n(t) = {area:,.6f}; sum of sojourn times = {sum_w:,.6f}; "
             f"relative difference {abs(area - sum_w) / sum_w:.1e}",
             f"    L = {area / t_cut:.6f}; lambda * W = {lam:.6f} * {w:.6f} = {lam * w:.6f}"]
    # any long window (not ending empty): edge effects only
    t_end = arr[n // 2] + 0.37
    l_avg, _ = time_average_n(arr, dep, t_end)
    inside = [(a, min(d, t_end)) for a, d in zip(arr, dep) if a < t_end]
    lam2 = len(inside) / t_end
    w2 = sum(d - a for a, d in inside) / len(inside)
    lines.append(f"  arbitrary window [0, {t_end:,.2f}]: L = {l_avg:.4f}, lambda * W (W truncated at the edge) = "
                 f"{lam2 * w2:.4f}")
    return lines


# ---------- tail amplification ----------
def check_tail(requests=100_000, seed=11):
    rng = random.Random(seed)
    # leaf latency: log-normal, median 10 ms; its p99 computed from the same distribution
    mu, sigma = math.log(10), 0.8
    leaf = sorted(rng.lognormvariate(mu, sigma) for _ in range(200_000))
    p99 = leaf[int(0.99 * len(leaf))]
    lines = ["T25.3 tail amplification: each leaf log-normal (median 10 ms), 'slow' = above the leaf p99 "
             f"({p99:.1f} ms); {requests:,} root requests per fan-out"]
    for n in (1, 10, 100):
        slow = 0
        for _ in range(requests):
            slow += any(rng.lognormvariate(mu, sigma) > p99 for _ in range(n))
        theory = 1 - 0.99 ** n
        lines.append(f"  fan-out {n:>3}: P(root waits for a slow leaf) sim {slow / requests:.4f}, "
                     f"1 - 0.99^n = {theory:.4f}")
    q = 0.99 ** (1 / 100)
    lines.append(f"  to keep the root's p99 at the leaf-p99 level with fan-out 100, each leaf must meet its "
                 f"{q:.6f} quantile (about p99.99)")
    return lines


# ---------- Amdahl and USL ----------
def amdahl(p, sigma):
    return p / (1 + sigma * (p - 1))


def usl(p, sigma, kappa):
    return p / (1 + sigma * (p - 1) + kappa * p * (p - 1))


def closed_system(p, seed, completions=20_000, think=1.0, hold=0.05, coherency=0.004):
    """p workers: think ~ Exp(mean 1.0), then take one shared FIFO lock for hold + coherency*(p-1).
    Returns throughput (completions per time unit)."""
    rng = random.Random(seed)
    h = hold + coherency * (p - 1)
    ready = [(rng.expovariate(1 / think), w) for w in range(p)]   # (time worker wants the lock, worker)
    heapq.heapify(ready)
    lock_free, done, t = 0.0, 0, 0.0
    while done < completions:
        t_want, w = heapq.heappop(ready)
        start = max(t_want, lock_free)
        lock_free = start + h
        done += 1
        t = lock_free
        heapq.heappush(ready, (lock_free + rng.expovariate(1 / think), w))
    return done / t


def fit_usl(ps, cap):
    """Least squares on p / C(p) - 1 = sigma (p - 1) + kappa p (p - 1) (linear in sigma, kappa), sigma >= 0."""
    xs = [(p - 1, p * (p - 1)) for p in ps]
    ys = [p / c - 1 for p, c in zip(ps, cap)]
    s11 = sum(a * a for a, _ in xs); s12 = sum(a * b for a, b in xs); s22 = sum(b * b for _, b in xs)
    t1 = sum(a * y for (a, _), y in zip(xs, ys)); t2 = sum(b * y for (_, b), y in zip(xs, ys))
    det = s11 * s22 - s12 * s12
    sigma, kappa = (t1 * s22 - t2 * s12) / det, (s11 * t2 - s12 * t1) / det
    if sigma < 0:                        # a serial fraction cannot be negative: refit kappa alone
        sigma, kappa = 0.0, t2 / s22
    return sigma, kappa


def check_usl():
    lines = ["T25.4 Amdahl and USL"]
    sigma = 0.05
    lines.append("  Amdahl sigma=0.05: " + ", ".join(f"S({p})={amdahl(p, sigma):.2f}" for p in (2, 8, 16, 64, 1024))
                 + f"; bound 1/sigma = {1 / sigma:.0f}")
    for s, k in ((0.02, 0.0005), (0.1, 0.001), (0.03, 0.0001)):
        grid_best = max(range(1, 2001), key=lambda p: usl(p, s, k))
        lines.append(f"  USL sigma={s}, kappa={k}: p* formula {math.sqrt((1 - s) / k):.2f}, integer argmax {grid_best}, "
                     f"C(p*)={usl(grid_best, s, k):.2f}")
    ps = list(range(1, 41))
    x = [closed_system(p, seed=100 + p) for p in ps]
    cap = [v / x[0] for v in x]
    fs, fk = fit_usl(ps, cap)
    p_meas = ps[max(range(len(ps)), key=lambda i: cap[i])]
    lines.append("  simulated closed system (p workers, think Exp(1), shared FIFO lock held 0.05 + 0.004(p-1)): "
                 + ", ".join(f"C({p})={cap[p - 1]:.2f}" for p in (1, 4, 8, 12, 16, 24, 32, 40)))
    lines.append(f"  USL fit (sigma >= 0): sigma={fs:.4f}, kappa={fk:.5f} -> predicted peak p*={math.sqrt((1 - fs) / fk):.1f}; "
                 f"measured peak at p={p_meas} (C={max(cap):.2f}); throughput falls after the peak: "
                 f"C(40)/C(peak)={cap[-1] / max(cap):.2f}")
    return lines


CHECKS = {"mm1": check_mm1, "little": check_little, "tail": check_tail, "usl": check_usl}


def main(argv):
    for name in argv[1:] or list(CHECKS):
        print("\n".join(CHECKS[name]()))


if __name__ == "__main__":
    main(sys.argv)
