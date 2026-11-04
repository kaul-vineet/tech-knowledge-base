"""L500 #24 Foundations II: numerical checks of the Stefan-Boltzmann law (from Planck), L = 4 pi R^2 sigma T^4 and the
HR diagram, the mass-luminosity relation and stellar lifetimes, and the distance ladder (parallax -> Cepheids ->
Type Ia supernovae -> Hubble's law) on a seeded synthetic universe.

python stars.py            # runs every check, prints the evidence, exits 1 if any check fails
Constants: h, k, c exact (SI 2019); sigma CODATA (as in lesson 6); solar values IAU 2015 Resolution B3 (nominal);
G = 6.67408e-11 is the CODATA 2014 value quoted in the B3 text. Synthetic stars/galaxies are illustrative, not a catalogue.
"""
import math
import sys

import numpy as np

H, K, C = 6.62607015e-34, 1.380649e-23, 299_792_458.0
SIGMA_CODATA = 5.670374419e-8
L_SUN, R_SUN, T_SUN = 3.828e26, 6.957e8, 5772.0  # IAU 2015 B3 nominal
GM_SUN, G = 1.3271244e20, 6.67408e-11
AU = 149_597_870_700.0
PC = AU * 648_000.0 / math.pi
YEAR = 365.25 * 86_400.0
# Illustrative V-band Cepheid P-L relation M_V = A_PL (log P - 1) + B_PL (close to published Galactic calibrations)
A_PL, B_PL = -2.43, -4.05


def planck_lambda(lam, T):
    return 2 * H * C ** 2 / lam ** 5 / np.expm1(H * C / (lam * K * T))


def sigma_from_constants():
    return 2 * math.pi ** 5 * K ** 4 / (15 * C ** 2 * H ** 3)


def luminosity(R, T):
    return 4 * math.pi * R ** 2 * SIGMA_CODATA * T ** 4


def distance_modulus(d_pc):
    return 5 * np.log10(d_pc) - 5


def check_stefan_boltzmann():
    lines = []
    x = np.linspace(1e-6, 60, 600_001)
    integral = float(np.trapezoid(x ** 3 / np.expm1(x), x))
    series = sum(6 / n ** 4 for n in range(1, 200))
    lines.append(f"int_0^inf x^3/(e^x - 1) dx: quadrature {integral:.10f}, series 6*sum(1/n^4) {series:.10f}, pi^4/15 {math.pi ** 4 / 15:.10f}")
    sig = sigma_from_constants()
    lines.append(f"sigma = 2 pi^5 k^4 / (15 c^2 h^3) = {sig:.9e} W m^-2 K^-4 (CODATA {SIGMA_CODATA:.9e})")
    lam = np.geomspace(10e-9, 1e-2, 400_001)
    flux = math.pi * float(np.trapezoid(planck_lambda(lam, T_SUN), lam))
    lines.append(f"pi * int B_lambda d lambda at 5772 K = {flux:.5e} W/m^2 vs sigma T^4 = {SIGMA_CODATA * T_SUN ** 4:.5e}")
    l_calc = luminosity(R_SUN, T_SUN)
    lines.append(f"4 pi R_sun^2 sigma T_sun^4 = {l_calc:.4e} W vs nominal L_sun {L_SUN:.4e} W (rel. diff {abs(l_calc - L_SUN) / L_SUN:.1e})")
    t = np.array([3000.0, 6000.0, 12000.0])
    slope = np.diff(np.log10([luminosity(R_SUN, ti) for ti in t])) / np.diff(np.log10(t))
    lines.append(f"HR diagram: at fixed R, d log L / d log T = {slope[0]:.6f}, {slope[1]:.6f} (lines of constant radius have slope 4)")
    ok = (abs(integral - math.pi ** 4 / 15) < 1e-6 and abs(sig - SIGMA_CODATA) / SIGMA_CODATA < 1e-9
          and abs(flux / (SIGMA_CODATA * T_SUN ** 4) - 1) < 1e-4 and abs(l_calc - L_SUN) / L_SUN < 1e-3 and np.allclose(slope, 4))
    return lines, ok


def synthetic_main_sequence(n=60, alpha=3.5, beta=0.8, seed=24):
    """Illustrative main sequence: L = M^alpha, R = M^beta (solar units) with 0.05 dex scatter in L."""
    rng = np.random.default_rng(seed)
    m = np.geomspace(0.5, 20.0, n)
    lum = m ** alpha * 10 ** rng.normal(0, 0.05, n)
    rad = m ** beta
    teff = T_SUN * (lum / rad ** 2) ** 0.25  # from L = 4 pi R^2 sigma T^4 in solar units
    return m, lum, rad, teff


def check_mass_luminosity():
    lines = []
    m, lum, rad, teff = synthetic_main_sequence()
    slope, intercept = np.polyfit(np.log10(m), np.log10(lum), 1)
    lines.append(f"synthetic main sequence (60 stars, L = M^3.5 x 0.05 dex scatter): fitted log L = {slope:.3f} log M + {intercept:+.3f}")
    for i in (0, 20, 40, 59):
        lines.append(f"  M = {m[i]:6.2f} Msun  L = {lum[i]:10.3e} Lsun  R = {rad[i]:5.2f} Rsun  Teff = {teff[i]:7.0f} K")
    m_sun = GM_SUN / G
    t_sun = 0.007 * 0.1 * m_sun * C ** 2 / L_SUN / YEAR / 1e9
    lines.append(f"Sun: M = GM/G = {m_sun:.5e} kg; t = 0.007 x 0.1 x M c^2 / L = {t_sun:.2f} Gyr")
    life = lambda mass: t_sun * mass / mass ** 3.5
    lines.append(f"t(M) = t_sun M / L = t_sun M^-2.5: 2 Msun {life(2.0):.2f} Gyr, 10 Msun {life(10.0) * 1000:.0f} Myr, 0.5 Msun {life(0.5):.0f} Gyr")
    ok = abs(slope - 3.5) < 0.05 and abs(t_sun - 10.36) < 0.01 and teff[-1] > teff[0]
    return lines, ok


def check_distance_ladder():
    lines = []
    rng = np.random.default_rng(2024)
    p_mas = 2.01  # l Car, HST FGS parallax (Benedict et al. 2007)
    d_small = 1000 / p_mas
    d_exact = AU / math.tan(math.radians(p_mas / 3.6e6)) / PC
    lines.append(f"parallax 2.01 mas: d = 1/p = {d_small:.1f} pc (exact 1 au / tan p: rel. diff {abs(d_exact - d_small) / d_small:.1e}); mu = {distance_modulus(d_small):.2f}")
    # Rung 1: Galactic Cepheids with parallaxes calibrate the P-L relation
    n1 = 40
    d1 = rng.uniform(300, 2000, n1)
    logp1 = rng.uniform(0.4, 1.6, n1)
    mabs1 = A_PL * (logp1 - 1) + B_PL + rng.normal(0, 0.10, n1)
    m1 = mabs1 + distance_modulus(d1)
    par = 1000 / d1 + rng.normal(0, 0.02, n1)  # mas
    a_fit, b_fit = np.polyfit(logp1 - 1, m1 - distance_modulus(1000 / par), 1)
    lines.append(f"rung 1 ({n1} Cepheids, sigma_parallax 0.02 mas): P-L slope {a_fit:.3f}, zero point {b_fit:.3f} (true {A_PL}, {B_PL})")
    # Rung 2: Cepheids in supernova hosts give host distances; each host's supernova peak then calibrates M_SN
    m_sn_true, n_hosts = -19.3, 8
    d_hosts = rng.uniform(10e6, 40e6, n_hosts)
    m_sn_each = []
    for d_host in d_hosts:
        logp2 = rng.uniform(0.8, 1.8, 25)
        m2 = A_PL * (logp2 - 1) + B_PL + rng.normal(0, 0.10, 25) + distance_modulus(d_host)
        mu_host = float(np.mean(m2 - (a_fit * (logp2 - 1) + b_fit)))
        m_sn_each.append(m_sn_true + distance_modulus(d_host) + rng.normal(0, 0.10) - mu_host)
    m_sn_cal = float(np.mean(m_sn_each))
    lines.append(f"rung 2 ({n_hosts} hosts at 10-40 Mpc, 25 Cepheids + 1 SN Ia each): M_SN = {m_sn_cal:.3f} (true {m_sn_true}); hosts span {min(m_sn_each):.3f} .. {max(m_sn_each):.3f}")
    # Rung 3: Hubble-flow supernovae, low-z approximation cz = H0 d
    h0_true, n3 = 70.0, 60
    z = rng.uniform(0.01, 0.05, n3)
    d3 = C / 1000 * z / h0_true * 1e6  # pc
    msn = m_sn_true + distance_modulus(d3) + rng.normal(0, 0.12, n3)
    v = C / 1000 * z
    fit_h0 = lambda m_cal: float(np.sum(v * 10 ** ((msn - m_cal + 5) / 5) / 1e6) / np.sum((10 ** ((msn - m_cal + 5) / 5) / 1e6) ** 2))
    h0_fit, h0_one = fit_h0(m_sn_cal), fit_h0(m_sn_each[0])
    lines.append(f"rung 3 ({n3} SNe, 0.01 < z < 0.05): H0 = {h0_fit:.2f} km/s/Mpc (true {h0_true}); calibrating on host 1 alone gives {h0_one:.2f}")
    mc = 10 ** (rng.normal(0, 0.1, 200_000) / 5)
    lines.append(f"error propagation: sigma_mu = 0.10 mag -> sigma_d/d = (ln 10 / 5) 0.10 = {math.log(10) / 5 * 0.1:.4f}; Monte Carlo {np.std(mc):.4f}")
    ok = (abs(a_fit - A_PL) < 0.15 and abs(b_fit - B_PL) < 0.05 and abs(m_sn_cal - m_sn_true) < 0.06
          and abs(h0_fit - h0_true) < 2.5 and abs(np.std(mc) - math.log(10) / 5 * 0.1) < 1e-3 and f"{d_small:.1f}" == "497.5")
    return lines, ok


CHECKS = {"stefan_boltzmann": check_stefan_boltzmann, "mass_luminosity": check_mass_luminosity,
          "distance_ladder": check_distance_ladder}


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
