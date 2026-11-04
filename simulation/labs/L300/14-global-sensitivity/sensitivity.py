"""L300 global sensitivity analysis: which inputs drive an office's daily cooling energy?

E = 150 + 4*dT + 1.0*(occupants - 40) + 24*window*dT + 3*(lights_h - 8)   [kWh/day], dT = outdoor - 22 C
Open windows only matter when it is warmer or colder outside than inside: an INTERACTION (window x dT).
Compares one-at-a-time (OAT), Morris screening and Sobol' indices (Saltelli/Jansen estimators).
python sensitivity.py
"""
import numpy as np

NAMES = ["outdoor_C", "occupants", "window_open", "lights_h"]
LOW = np.array([16.0, 20.0, 0.0, 6.0])
HIGH = np.array([28.0, 60.0, 1.0, 10.0])
NOMINAL = (LOW + HIGH) / 2  # 22 C, 40 people, windows half open, 8 h of lights
SEED = 14


def energy(x):
    """Model: x (n, 4) in physical units -> kWh/day."""
    dT = x[:, 0] - 22.0
    return 150 + 4 * dT + 1.0 * (x[:, 1] - 40) + 24 * x[:, 2] * dT + 3 * (x[:, 3] - 8)


def scale(u):
    return LOW + u * (HIGH - LOW)  # unit cube -> physical ranges (inputs independent, uniform)


def oat(f=energy):
    """One-at-a-time: swing each input over its full range, the others held at NOMINAL. Local view only."""
    swings = []
    for i in range(len(NAMES)):
        lo, hi = NOMINAL.copy(), NOMINAL.copy()
        lo[i], hi[i] = LOW[i], HIGH[i]
        swings.append(abs(f(hi[None])[0] - f(lo[None])[0]))
    return np.array(swings)


def morris(r=20, levels=4, f=energy, seed=SEED):
    """Morris screening: r random one-step-per-input trajectories on a grid; mu* = mean |EE|, sigma = sd(EE)."""
    rng, d = np.random.default_rng(seed), len(NAMES)
    delta = levels / (2 * (levels - 1))  # 2/3 for 4 levels (Morris 1991)
    ee = np.zeros((r, d))
    for k in range(r):
        x = rng.integers(0, levels // 2, d) / (levels - 1)  # start where x + delta stays inside [0, 1]
        y = f(scale(x)[None])[0]
        for i in rng.permutation(d):  # move one input at a time, in random order
            x[i] += delta
            y_new = f(scale(x)[None])[0]
            ee[k, i], y = (y_new - y) / delta, y_new  # elementary effect per full input range
    return np.abs(ee).mean(axis=0), ee.std(axis=0, ddof=1)


def sobol(n=8192, f=energy, seed=SEED):
    """Sobol' indices from N(d+2) runs: matrices A, B and AB_i (column i of A replaced by column i of B)."""
    rng, d = np.random.default_rng(seed), len(NAMES)
    a, b = rng.random((n, d)), rng.random((n, d))
    fa, fb = f(scale(a)), f(scale(b))
    mean, var = np.mean(np.concatenate([fa, fb])), np.var(np.concatenate([fa, fb]))
    fa, fb = fa - mean, fb - mean  # centring: same indices in expectation, much less estimator noise
    s1, st = np.zeros(d), np.zeros(d)
    for i in range(d):
        ab = a.copy()
        ab[:, i] = b[:, i]
        fab = f(scale(ab)) - mean
        s1[i] = np.mean(fb * (fab - fa)) / var  # first order, Saltelli et al. 2010
        st[i] = 0.5 * np.mean((fa - fab) ** 2) / var  # total order (includes interactions), Jansen 1999
    return s1, st


def table(n=8192):
    swing, (mu_star, sigma), (s1, st) = oat(), morris(), sobol(n)
    return [{"input": NAMES[i], "oat_swing": round(float(swing[i]), 1), "morris_mu_star": round(float(mu_star[i]), 1),
             "morris_sigma": round(float(sigma[i]), 1), "S1": round(float(s1[i]), 3), "ST": round(float(st[i]), 3)}
            for i in range(len(NAMES))]


def ranking(rows, key):
    return [r["input"] for r in sorted(rows, key=lambda r: -r[key])]


def screen(rows, k=2):
    """Screening: keep the k most important inputs; the rest get frozen at nominal. Importance = OAT swing."""
    return ranking(rows, "oat_swing")[:k]


def variance_kept(keep, n=50_000, f=energy, seed=SEED):
    """Screening test: fix every input NOT in keep at its nominal value; share of output variance still explained."""
    x = scale(np.random.default_rng(seed).random((n, len(NAMES))))
    reduced = x.copy()
    for i, name in enumerate(NAMES):
        if name not in keep:
            reduced[:, i] = NOMINAL[i]
    return float(np.var(f(reduced)) / np.var(f(x)))


def main():
    rows = table()
    print("input         OAT swing   Morris mu*  sigma    Sobol S1    ST     (kWh/day; indices = share of variance)")
    for r in rows:
        print(f"{r['input']:12s}  {r['oat_swing']:8.1f}   {r['morris_mu_star']:8.1f}  {r['morris_sigma']:6.1f}"
              f"   {r['S1']:7.3f}  {r['ST']:7.3f}")
    print(f"runs: OAT {2 * len(NAMES)}, Morris {20 * (len(NAMES) + 1)}, Sobol {8192 * (len(NAMES) + 2)}")
    print("rank by OAT swing:", " > ".join(ranking(rows, "oat_swing")))
    print("rank by Sobol ST: ", " > ".join(ranking(rows, "ST")))
    print(f"sum S1 = {sum(r['S1'] for r in rows):.3f}  (1 - sum S1 = variance from interactions)")
    keep = screen(rows)
    print(f"screen() keeps {keep}: the reduced model keeps {variance_kept(keep):.1%} of the variance")


if __name__ == "__main__":
    main()
