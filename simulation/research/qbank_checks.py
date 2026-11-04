"""Recomputes every calculation answer and executes every code-reading snippet in content/qbank/*.json (L100-L500).

python research/qbank_checks.py   (from the simulation/ folder; numpy + stdlib only; prints OK and exits 0)

- calculation: CALC_IDS maps each question id to a function below; the formatted result must be the option
  at the answer index and must not appear among the distractors.
- code-reading: the snippet is executed; its stdout must be the option at the answer index (and no other option).
- debugging snippets must compile.
- anchor checks: the helper functions reproduce numbers the labs print (Erlang C 0.647, 313 s bound, ...).
"""
import contextlib
import io
import json
import math
import sys
from pathlib import Path

import numpy as np

QBANK = Path(__file__).resolve().parent.parent / "content" / "qbank"


# ---------- helpers ----------
def t_quantile(p, df):
    """Student t quantile by bisection on the CDF (Simpson integration of the density); no SciPy needed."""
    c = math.exp(math.lgamma((df + 1) / 2) - math.lgamma(df / 2)) / math.sqrt(df * math.pi)
    pdf = lambda x: c * (1 + x * x / df) ** (-(df + 1) / 2)

    def cdf(x, n=4000):
        h = x / n
        s = pdf(0) + pdf(x) + sum((4 if k % 2 else 2) * pdf(k * h) for k in range(1, n))
        return 0.5 + s * h / 3

    lo, hi = 0.0, 50.0
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if cdf(mid) < p else (lo, mid)
    return (lo + hi) / 2


def mm1_wq(lam, mu):
    return lam / (mu * (mu - lam))


def erlang_c(lam, mu, c):
    """P(wait) for M/M/c."""
    a = lam / mu
    rho = a / c
    s = sum(a ** k / math.factorial(k) for k in range(c))
    top = a ** c / math.factorial(c) / (1 - rho)
    return top / (s + top)


def erlang_c_wq(lam, mu, c):
    return erlang_c(lam, mu, c) / (c * mu - lam)


def erlang_b(a, c):
    b = 1.0
    for k in range(1, c + 1):
        b = a * b / (k + a * b)
    return b


def service_level(lam, mu, c, t):
    """P(answered within t) for M/M/c: 1 - C * exp(-(c mu - lam) t)."""
    return 1 - erlang_c(lam, mu, c) * math.exp(-(c * mu - lam) * t)


def euler_fall_error(dt, t_end=3.0, g=9.8, h0=100.0):
    """Explicit Euler, no drag: simulated height minus exact height at t_end."""
    y, v = h0, 0.0
    for _ in range(round(t_end / dt)):
        y, v = y + v * dt, v - g * dt
    return y - (h0 - 0.5 * g * t_end ** 2)


def rk4_fall_error(dt, t_end=3.0, g=9.8, h0=100.0):
    y, v = h0, 0.0
    for _ in range(round(t_end / dt)):
        k1y, k1v = v, -g
        k2y, k3y, k4y = v + 0.5 * dt * k1v, v + 0.5 * dt * k1v, v + dt * k1v
        y, v = y + dt / 6 * (k1y + 2 * k2y + 2 * k3y + k4y), v - g * dt
    return y - (h0 - 0.5 * g * t_end ** 2)


def terminal_velocity(mass, g=9.8, cd=1.05, rho=1.225, area=0.09):
    return math.sqrt(2 * mass * g / (cd * rho * area))


def exact_overtime(k, mean, s):
    tail = lambda m: sum(math.exp(-s / mean) * (s / mean) ** j / math.factorial(j) for j in range(m))
    return k * mean * tail(k + 1) - s * tail(k)


def sobol_grid(f, d, lo=0.0, hi=1.0, m=41):
    """Exact-ish first- and total-order Sobol' indices of f on a tensor grid of midpoints (independent uniforms)."""
    x = lo + (np.arange(m) + 0.5) / m * (hi - lo)
    grids = np.meshgrid(*([x] * d), indexing="ij")
    y = f(*grids)
    v = y.var()
    s1, st = [], []
    for i in range(d):
        others = tuple(j for j in range(d) if j != i)
        s1.append(y.mean(axis=others).var() / v)  # Var(E[Y | X_i]) / V
        st.append(y.var(axis=i).mean() / v)  # E[Var(Y | X_~i)] / V
    return s1, st


def sobol_mc(f, d, lo, hi, n=200_000, seed=0):
    """Saltelli (S1) and Jansen (ST) estimators, as in lesson 14, to cross-check sobol_grid."""
    rng = np.random.default_rng(seed)
    a, b = lo + (hi - lo) * rng.random((n, d)), lo + (hi - lo) * rng.random((n, d))
    fa, fb = f(*a.T), f(*b.T)
    mean, var = np.concatenate([fa, fb]).mean(), np.concatenate([fa, fb]).var()
    fa, fb = fa - mean, fb - mean
    s1, st = [], []
    for i in range(d):
        ab = a.copy()
        ab[:, i] = b[:, i]
        fab = f(*ab.T) - mean
        s1.append(np.mean(fb * (fab - fa)) / var)
        st.append(0.5 * np.mean((fa - fab) ** 2) / var)
    return s1, st


def expected_min_normal(k, sd):
    """E[min of k iid N(0, sd^2)] by numerical integration of the order-statistic density."""
    x = np.linspace(-8, 8, 160_001)
    phi = np.exp(-x * x / 2) / math.sqrt(2 * math.pi)
    cdf = np.cumsum(phi) * (x[1] - x[0])
    dens = k * phi * (1 - cdf) ** (k - 1)
    return float(np.sum(x * dens) * (x[1] - x[0]) * sd)


def amdahl(f_serial, p):
    return 1 / (f_serial + (1 - f_serial) / p)


def extinction(m):
    """Smallest root of q = exp(m (q - 1)) (Poisson(m) branching process) by fixed-point iteration from 0."""
    q = 0.0
    for _ in range(5000):
        q = math.exp(m * (q - 1))
    return q


def min_servers(lam, mu, ok):
    c = math.floor(lam / mu) + 1
    while not ok(c):
        c += 1
    return c


# ---------- calculation answers (slug -> (function, format)) ----------
CALCS = {
    # L100
    "mc_tri_mean": (lambda: (3 + 5 + 10) / 3 + (4 + 6 + 11) / 3, "{:.3f} days"),
    "mc_n_for_hw": (lambda: round(1_000 * (0.150 / 0.050) ** 2), "{:,} samples"),
    "mm1_wq_09": (lambda: mm1_wq(0.9, 1.0), "{:.1f} min"),
    "mm1_lq_little": (lambda: 0.75 * mm1_wq(0.75, 1.0), "{:.2f} customers"),
    "mm1_growth": (lambda: 100 * (mm1_wq(0.95, 1.0) / mm1_wq(0.9, 1.0) - 1), "+{:.0f}%"),
    "euler_dt002": (lambda: euler_fall_error(0.02), "{:.3f} m"),
    "vt_8kg": (lambda: terminal_velocity(8.0), "{:.2f} m/s"),
    "vv_halfwidth": (lambda: t_quantile(0.975, 9) * 0.40 / math.sqrt(10), "{:.3f} min"),
    # L200
    "ec_pwait_4": (lambda: erlang_c(3.0, 1.0, 4), "{:.3f}"),
    "ec_min_desks": (lambda: min_servers(4.2, 1.0, lambda c: erlang_c(4.2, 1.0, c) < 0.20), "{} desks"),
    "pk_ratio_05": (lambda: (1 + 1.0 ** 2) / (1 + 0.5 ** 2), "{:.2f}x"),
    "lognorm_mean": (lambda: math.exp(1.0 + 0.5 ** 2 / 2), "{:.2f} min"),
    "coffee_50c": (lambda: math.log(70 / 30) / 0.05, "{:.2f} min"),
    "euler_stab_steps": (lambda: round(10 / (2 * 1e-3)), "{:,} steps"),
    "reps_for_020": (lambda: math.ceil(10 * (0.50 / 0.20) ** 2), "about {}"),
    "crn_width_ratio": (lambda: math.sqrt(2 * 0.8 ** 2 * (1 - 0.9)) / math.sqrt(2 * 0.8 ** 2), "{:.2f}"),
    # L300
    "anti_gain_06": (lambda: 1 / (1 - 0.6), "{:.2f}x"),
    "cv_gain_095": (lambda: 1 / (1 - 0.95 ** 2), "{:.2f}x"),
    "overtime_k10": (lambda: exact_overtime(10, 0.6, 6.5), "{:.4f} h"),
    "sobol_lin_s1": (lambda: sobol_grid(lambda x1, x2: x1 + 2 * x2, 2)[0][1], "{:.2f}"),
    "sobol_int_st2": (lambda: sobol_grid(lambda x1, x2: x1 + x1 * x2, 2, -1.0, 1.0)[1][1], "{:.2f}"),
    "sobol_runs": (lambda: 1024 * (6 + 2), "{:,} runs"),
    "cosim_bound_k6": (lambda: 1800 * math.log(6 / 5), "{:.0f} s"),
    "ols_s2": (lambda: 2.4 / (20 - 5), "{:.3f}"),
    # L400
    "kf_gain": (lambda: 0.09 / (0.09 + 0.01), "{:.2f}"),
    "gate_z": (lambda: (85.0 - 21.3) / math.sqrt(0.16), "{:.1f}"),
    "amdahl_8": (lambda: amdahl(0.10, 8), "{:.2f}x"),
    "gp_cost": (lambda: (3000 / 300) ** 3, "{:,.0f}x"),
    "rel_hw": (lambda: 100 * t_quantile(0.975, 9) * 0.35 / math.sqrt(10) / 2.10, "{:.1f}%"),
    "sl_staffing": (lambda: min_servers(2.0, 1 / 3, lambda c: service_level(2.0, 1 / 3, c, 1 / 3) >= 0.80), "{} agents"),
    "winners_curse": (lambda: expected_min_normal(81, 0.10), "{:+.2f} per day"),
    "elasticity": (lambda: ((0.749 - 0.800) / 0.800) / ((5.5 - 5.0) / 5.0), "{:+.2f}"),
    # L500
    "l5_cheb_n": (lambda: math.ceil(1.0 / (0.05 * 0.1**2)), "{:,} samples"),
    "l5_poisson_40s": (lambda: math.exp(-3.0 * 40 / 60), "{:.4f}"),
    "l5_rk4_pred": (lambda: 6.990e-06 / 2**4, "{:.2e}"),
    "l5_euler_stab_250": (lambda: 2 / 250, "{:.3f}"),
    "l5_halfwidth_n": (lambda: round(10_000 * (0.02 / 0.01) ** 2), "{:,} samples"),
    "l5_anti_075": (lambda: 1 / (1 - 0.75), "{:.2f}x"),
    "l5_ofqual_count": (lambda: round((1 - 0.964) * 718_276), "{:,} entries"),
    "l5_small_cohort_sd": (lambda: math.sqrt(0.26 * 0.74 / 24), "{:.3f}"),
    "l5_extinction_15": (lambda: extinction(1.5), "{:.4f}"),
}

# question id -> slug
CALC_IDS = {
    "sim-L100-007": "mc_tri_mean", "sim-L100-008": "mc_n_for_hw", "sim-L100-015": "mm1_wq_09", "sim-L100-016": "mm1_lq_little",
    "sim-L100-017": "mm1_growth", "sim-L100-022": "euler_dt002", "sim-L100-023": "vt_8kg", "sim-L100-039": "vv_halfwidth",
    "sim-L200-002": "pk_ratio_05", "sim-L200-003": "lognorm_mean", "sim-L200-011": "ec_pwait_4", "sim-L200-012": "ec_min_desks",
    "sim-L200-020": "coffee_50c", "sim-L200-021": "euler_stab_steps", "sim-L200-028": "reps_for_020", "sim-L200-036": "crn_width_ratio",
    "sim-L300-002": "anti_gain_06", "sim-L300-003": "cv_gain_095", "sim-L300-004": "overtime_k10", "sim-L300-011": "ols_s2",
    "sim-L300-019": "sobol_lin_s1", "sim-L300-020": "sobol_int_st2", "sim-L300-021": "sobol_runs", "sim-L300-028": "cosim_bound_k6",
    "sim-L400-002": "kf_gain", "sim-L400-003": "gate_z", "sim-L400-009": "winners_curse", "sim-L400-016": "gp_cost",
    "sim-L400-023": "amdahl_8", "sim-L400-030": "rel_hw", "sim-L400-036": "sl_staffing", "sim-L400-037": "elasticity",
    "sim-L500-002": "l5_cheb_n", "sim-L500-005": "l5_poisson_40s", "sim-L500-013": "l5_rk4_pred", "sim-L500-014": "l5_euler_stab_250",
    "sim-L500-026": "l5_halfwidth_n", "sim-L500-027": "l5_anti_075", "sim-L500-034": "l5_ofqual_count", "sim-L500-040": "l5_small_cohort_sd",
    "sim-L500-043": "l5_extinction_15",
}


def value(slug):
    fn, fmt = CALCS[slug]
    return fmt.format(fn())


def run_snippet(code):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(code, "<snippet>", "exec"), {"__name__": "__main__"})
    return buf.getvalue().strip()


def anchors():
    """Helpers must reproduce numbers the labs print; otherwise the answers above are not trustworthy."""
    checks = [
        (round(mm1_wq(0.8, 1.0), 3), 4.0),
        (round(erlang_c(2.4, 1.0, 3), 3), 0.647),
        (round(erlang_c_wq(2.4, 1.0, 3), 3), 1.079),
        (round(erlang_c(2.4, 1.0, 4), 3), 0.287),
        (round(erlang_b(2.4, 3), 3), 0.268),
        (round(euler_fall_error(0.1), 2), 1.47),
        (abs(rk4_fall_error(0.1)) < 1e-9, True),
        (round(terminal_velocity(2.0), 2), 18.40),
        (round(t_quantile(0.975, 9), 3), 2.262),
        (round(exact_overtime(12, 0.6, 7.0), 4), 0.9196),
        (round(3600 * math.log(12 / 11)), 313),
        (round(math.log(70 / 40) / 0.05, 6), 11.192316),
        (round(1.36 / math.sqrt(200), 3), 0.096),
        (round(math.exp(1.344 + 0.655 ** 2 / 2), 2), 4.75),
        (round((1 + 1) / (1 + 0.73 ** 2), 2), 1.30),
        (round(1 / (1 - 0.32), 2), 1.47),
    ]
    bad = [(got, want) for got, want in checks if got != want]
    assert not bad, f"anchor mismatches: {bad}"
    # the grid Sobol' values must agree with the lesson-14 Monte Carlo estimators
    for f, lo, hi in ((lambda x1, x2: x1 + 2 * x2, 0.0, 1.0), (lambda x1, x2: x1 + x1 * x2, -1.0, 1.0)):
        g1, gt = sobol_grid(f, 2, lo, hi)
        m1, mt = sobol_mc(f, 2, lo, hi)
        assert max(abs(a - b) for a, b in zip(g1 + gt, m1 + mt)) < 0.02, (g1, gt, m1, mt)
    assert round(sobol_grid(lambda x1, x2: x1 + x1 * x2, 2, -1.0, 1.0)[0][1], 2) == 0.0
    # winner's curse integral vs brute-force simulation
    sim = np.random.default_rng(1).normal(0, 0.10, (20_000, 81)).min(axis=1).mean()
    assert abs(sim - expected_min_normal(81, 0.10)) < 0.005
    # L500 anchors: lesson numbers printed by labs/L500 check scripts
    assert round(extinction(1.2), 4) == 0.6863 and round(extinction(2.0), 4) == 0.2032
    assert abs(6.990e-06 / 4.421e-07 - 16) < 0.5  # the RK4 check measured ratio 15.81


def main():
    anchors()
    errors, n_calc, n_code, n_debug, seen = [], 0, 0, 0, set()
    for lv in ("L100", "L200", "L300", "L400", "L500"):
        for q in json.loads((QBANK / f"{lv}.json").read_text(encoding="utf-8")):
            qid, opts, ans = q["id"], q["options"], q["answer"]
            if q["type"] == "calculation":
                n_calc += 1
                if qid not in CALC_IDS:
                    errors.append(f"{qid}: calculation without a recomputation in CALC_IDS")
                    continue
                seen.add(qid)
                v = value(CALC_IDS[qid])
                if opts[ans] != v:
                    errors.append(f"{qid}: answer option {opts[ans]!r} but code computes {v!r}")
                if sum(o == v for o in opts) != 1:
                    errors.append(f"{qid}: computed value {v!r} appears {sum(o == v for o in opts)} times")
            elif q["type"] == "code-reading":
                n_code += 1
                if not q.get("code"):
                    errors.append(f"{qid}: code-reading without code")
                    continue
                out = run_snippet(q["code"])
                if opts[ans] != out:
                    errors.append(f"{qid}: answer option {opts[ans]!r} but the snippet prints {out!r}")
                if sum(o == out for o in opts) != 1:
                    errors.append(f"{qid}: output {out!r} matches {sum(o == out for o in opts)} options")
            elif q.get("code"):
                n_debug += 1
                compile(q["code"], qid, "exec")
            if q.get("code") and len(q["code"].splitlines()) > 15:
                errors.append(f"{qid}: snippet longer than 15 lines")
    stale = set(CALC_IDS) - seen
    if stale:
        errors.append(f"CALC_IDS entries without a calculation question: {sorted(stale)}")
    for e in errors:
        print("ERROR", e)
    if errors:
        sys.exit(1)
    print(f"recomputed {n_calc} calculation answers, executed {n_code} code-reading snippets, compiled {n_debug} other snippets")
    print("OK")


if __name__ == "__main__":
    main()
