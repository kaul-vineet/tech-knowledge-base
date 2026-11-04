"""L500 #25 Foundations III: numerical checks of Hubble's law from homogeneous expansion, the low-z redshift-distance
relation, the critical density and the age of a flat universe, detailed balance for Metropolis(-Hastings), and the
closed-form (conjugate) posterior for H0 checked against a grid and against MCMC (the sampler of lesson 15).

python cosmo_bayes.py      # runs every check, prints the evidence, exits 1 if any check fails
Cosmology: Planck 2018 base-LCDM late-Universe values H0 = 67.4 km/s/Mpc, Omega_m = 0.315 (flat, radiation ignored).
G = 6.67408e-11 (CODATA 2014, as quoted in IAU 2015 B3). Hubble data are synthetic and seeded.
"""
import math
import sys

import numpy as np

C_KM = 299_792.458
AU = 149_597_870_700.0
MPC = AU * 648_000.0 / math.pi * 1e6        # m
G, GM_SUN = 6.67408e-11, 1.3271244e20
GYR = 365.25 * 86_400.0 * 1e9
H0, OM = 67.4, 0.315
OL = 1 - OM


def hubble_time_gyr(h0):
    return MPC / 1000 / h0 / GYR


def e_of_z(z):
    return np.sqrt(OM * (1 + z) ** 3 + OL)


def lum_distance(z, n=20_001):
    zz = np.linspace(0, z, n)
    return (1 + z) * C_KM / H0 * float(np.trapezoid(1 / e_of_z(zz), zz))


def age_closed_form(h0=H0, om=OM):
    ol = 1 - om
    return 2 / (3 * math.sqrt(ol)) * math.asinh(math.sqrt(ol / om)) * hubble_time_gyr(h0)


def check_hubble_law():
    lines = []
    rng = np.random.default_rng(25)
    x = rng.uniform(-100, 100, (500, 3))            # comoving positions, Mpc
    a, a_dot = 1.0, H0                              # r = a x, v = a_dot x, with a_dot / a = H0 today
    for k in (0, 137):                               # two different "home" galaxies
        rel_r, rel_v = a * (x - x[k]), a_dot * (x - x[k])
        mask = np.linalg.norm(rel_r, axis=1) > 0
        ratio = np.linalg.norm(rel_v[mask], axis=1) / np.linalg.norm(rel_r[mask], axis=1)
        aligned = np.min(np.sum(rel_v[mask] * rel_r[mask], axis=1) / np.linalg.norm(rel_v[mask], axis=1) / np.linalg.norm(rel_r[mask], axis=1))
        lines.append(f"observer at galaxy {k}: v/r ranges {ratio.min():.10f} .. {ratio.max():.10f} km/s/Mpc, min cos(angle v, r) = {aligned:.12f}")
    q0 = OM / 2 - OL
    zs = np.array([0.001, 0.002, 0.005, 0.01, 0.02])
    frac = np.array([lum_distance(z) / (C_KM * z / H0) - 1 for z in zs])
    slope = np.polyfit(zs[:3], frac[:3], 1)[0]
    lines.append(f"D_L / (cz/H0) - 1 at z = {[float(z) for z in zs]}: {[f'{f:.5f}' for f in frac]}")
    lines.append(f"small-z slope {slope:.4f} vs (1 - q0)/2 = {(1 - q0) / 2:.4f} with q0 = Om/2 - OL = {q0:.4f}")
    lines.append(f"Hubble time 1/H0: H0 = 67.4 -> {hubble_time_gyr(67.4):.2f} Gyr; Hubble (1929) K = 500 -> {hubble_time_gyr(500):.2f} Gyr")
    ok = abs(slope - (1 - q0) / 2) < 0.01 and f"{hubble_time_gyr(67.4):.2f}" == "14.51" and abs(frac[1] / zs[1] - (1 - q0) / 2) < 0.01
    return lines, ok


def check_friedmann_age():
    lines = []
    h_si = H0 * 1000 / MPC
    rho_c = 3 * h_si ** 2 / (8 * math.pi * G)
    per_mpc3 = rho_c * MPC ** 3 / (GM_SUN / G)
    lines.append(f"critical density 3H0^2/(8 pi G) = {rho_c:.4e} kg/m^3 = {per_mpc3:.4e} Msun/Mpc^3")
    a = np.linspace(1e-8, 1, 2_000_001)
    t_int = float(np.trapezoid(1 / (a * e_of_z(1 / a - 1)), a)) * hubble_time_gyr(H0)
    t_cf = age_closed_form()
    # independent route: integrate the Friedmann equation in u = a^(3/2), where du/dt = 1.5 H0 sqrt(Om + OL u^2) is smooth
    f = lambda u: 1.5 * math.sqrt(OM + OL * u * u)
    u, t, dt = 0.0, 0.0, 1e-4
    while True:
        k1 = f(u); k2 = f(u + 0.5 * dt * k1); k3 = f(u + 0.5 * dt * k2); k4 = f(u + dt * k3)
        step = dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        if u + step >= 1:
            t += dt * (1 - u) / step  # linear interpolation to a = 1 inside the last step
            break
        u, t = u + step, t + dt
    t_ode = t * hubble_time_gyr(H0)
    lines.append(f"age, flat LCDM (Om = {OM}): integral {t_int:.4f} Gyr, closed form {t_cf:.4f} Gyr, RK4 Friedmann ODE {t_ode:.4f} Gyr")
    lines.append(f"Einstein-de Sitter (Om = 1): 2/(3 H0) = {2 / 3 * hubble_time_gyr(H0):.2f} Gyr")
    ok = abs(t_int - t_cf) < 1e-3 and abs(t_ode - t_cf) < 1e-3 and abs(rho_c - 8.53e-27) < 0.01e-27
    return lines, ok


def metropolis_matrix(target, proposal, hastings=True):
    """Transition matrix K[i, j] = q(j|i) * acceptance; rejected moves stay on the diagonal."""
    n = len(target)
    k = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j and proposal[i, j] > 0:
                r = target[j] / target[i]
                if hastings:
                    r *= proposal[j, i] / proposal[i, j]
                k[i, j] = proposal[i, j] * min(1.0, r)
        k[i, i] = 1 - k[i].sum()
    return k


def check_detailed_balance():
    lines = []
    pi = np.array([1, 3, 2, 5, 4], float)
    pi /= pi.sum()
    n = len(pi)
    sym = np.zeros((n, n))
    for i in range(n):
        sym[i, (i + 1) % n] = sym[i, (i - 1) % n] = 0.5
    k = metropolis_matrix(pi, sym)
    flow = pi[:, None] * k
    lines.append(f"symmetric proposal: max |pi_i K_ij - pi_j K_ji| = {np.max(np.abs(flow - flow.T)):.1e}; max |pi K - pi| = {np.max(np.abs(pi @ k - pi)):.1e}")
    rng = np.random.default_rng(5)
    state, counts = 0, np.zeros(n)
    for _ in range(200_000):
        prop = (state + rng.choice((-1, 1))) % n
        if rng.uniform() < min(1.0, pi[prop] / pi[state]):
            state = prop
        counts[state] += 1
    lines.append(f"200000-step chain: max |frequency - pi| = {np.max(np.abs(counts / counts.sum() - pi)):.4f}")
    asym = np.zeros((n, n))
    for i in range(n):
        asym[i, (i + 1) % n], asym[i, (i - 1) % n] = 0.8, 0.2  # biased walk
    tv = lambda kk: 0.5 * np.sum(np.abs(np.linalg.matrix_power(kk, 4000)[0] - pi))
    no_h, with_h = tv(metropolis_matrix(pi, asym, hastings=False)), tv(metropolis_matrix(pi, asym, hastings=True))
    lines.append(f"biased proposal 0.8/0.2: total-variation distance to pi without Hastings factor {no_h:.3f}, with it {with_h:.1e}")
    ok = np.max(np.abs(flow - flow.T)) < 1e-15 and np.max(np.abs(counts / counts.sum() - pi)) < 0.01 and no_h > 0.05 and with_h < 1e-10
    return lines, ok


def synthetic_hubble(seed=1929, n=20, h0=70.0, sigma_v=300.0):
    rng = np.random.default_rng(seed)
    d = rng.uniform(5, 50, n)  # Mpc, assumed exact here
    return d, h0 * d + rng.normal(0, sigma_v, n), sigma_v


def posterior_closed_form(d, v, s, prior=None):
    """Gaussian likelihood, model v = H0 d: precision-weighted mean; prior = (mean, sd) or None for flat."""
    prec, num = np.sum(d ** 2) / s ** 2, np.sum(v * d) / s ** 2
    if prior is not None:
        prec, num = prec + 1 / prior[1] ** 2, num + prior[0] / prior[1] ** 2
    return num / prec, 1 / math.sqrt(prec)


def check_conjugate_posterior():
    lines = []
    d, v, s = synthetic_hubble()
    mean_cf, sd_cf = posterior_closed_form(d, v, s)
    grid = np.linspace(50, 90, 40_001)
    logl = -0.5 * np.sum((v[None, :] - grid[:, None] * d[None, :]) ** 2, axis=1) / s ** 2
    w = np.exp(logl - logl.max())
    w /= np.trapezoid(w, grid)
    mean_g = float(np.trapezoid(grid * w, grid))
    sd_g = math.sqrt(float(np.trapezoid((grid - mean_g) ** 2 * w, grid)))
    rng = np.random.default_rng(15)
    h, lp, chain, acc = 60.0, None, [], 0
    loglike = lambda hh: -0.5 * np.sum((v - hh * d) ** 2) / s ** 2  # flat prior: log posterior = log likelihood + const
    lp = loglike(h)
    for i in range(60_000):
        trial = h + rng.normal(0, 3.0)
        lt = loglike(trial)
        if math.log(rng.uniform()) < lt - lp:  # the Metropolis rule of lesson 15
            h, lp, acc = trial, lt, acc + 1
        if i >= 5_000:
            chain.append(h)
    chain = np.array(chain)
    lines.append(f"20 synthetic galaxies, sigma_v = 300 km/s, true H0 = 70: closed form {mean_cf:.3f} +/- {sd_cf:.3f}")
    lines.append(f"grid posterior {mean_g:.3f} +/- {sd_g:.3f}; Metropolis (55000 kept, acceptance {acc / 60_000:.2f}) {chain.mean():.3f} +/- {chain.std():.3f}")
    for prior in ((67.4, 0.5), (73.0, 1.0)):
        m, sd = posterior_closed_form(d, v, s, prior)
        lines.append(f"with Gaussian prior N({prior[0]}, {prior[1]}): posterior {m:.3f} +/- {sd:.3f}")
    ok = abs(mean_g - mean_cf) < 1e-3 and abs(sd_g - sd_cf) < 1e-3 and abs(chain.mean() - mean_cf) < 0.1 and abs(chain.std() - sd_cf) < 0.1
    return lines, ok


CHECKS = {"hubble_law": check_hubble_law, "friedmann_age": check_friedmann_age,
          "detailed_balance": check_detailed_balance, "conjugate_posterior": check_conjugate_posterior}


def main():
    all_ok = True
    for name, fn in CHECKS.items():
        lines, ok = fn()
        all_ok &= ok
        print(f"[{name}] {'PASS' if ok else 'FAIL'}")
        for line in lines:
            print("  " + line)
    print("ALL CHECKS PASS" if all_ok else "SOME CHECKS FAILED")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
