"""Mass models for a disk galaxy's rotation curve (numpy only) and a seeded SYNTHETIC data set.

Units: kpc, km/s, solar masses. G = 4.30091e-6 kpc (km/s)^2 / Msun.
- Exponential (Freeman 1970) disk: V^2 = 2 G Md / Rd * y^2 [I0 K0 - I1 K1](y), y = R / (2 Rd).
- Cored isothermal-like halo, density rho0 / (1 + (r/rc)^2) (the cored form quoted by NFW 1996):
  V^2 = 4 pi G rho0 rc^2 [1 - (rc/R) arctan(R/rc)].  DERIVED here, not quoted: M(R) = int_0^R 4 pi s^2 rho(s) ds;
  s^2 / (1 + s^2/rc^2) = rc^2 [1 - 1/(1 + s^2/rc^2)] integrates to rc^2 [R - rc arctan(R/rc)], and V^2 = G M(R) / R
  for a spherical mass (shell theorem). test_cored_halo_matches_numerical_mass_integral checks it numerically.
- NFW (1996, eq. 5): (V/V200)^2 = (1/x)[ln(1 + c x) - c x/(1 + c x)] / [ln(1 + c) - c/(1 + c)], x = R/r200,
  with V200 = 10 H0 r200 (from M200 = 200 rho_crit (4/3) pi r200^3, rho_crit = 3 H^2 / 8 pi G), H0 = 70 km/s/Mpc.
The data imitate NGC 3198's shape (Begeman 1989: disk scale length 2.63 kpc, curve flat near 150 km/s out to
~11 scale lengths) but are NOT the published measurements - see KNOWN-GAPS for the real SPARC data path.
"""
import math

import numpy as np

G, H0 = 4.30091e-6, 0.070  # kpc (km/s)^2 / Msun ; km/s/kpc
RD, MD_REF = 2.63, 2.0e10  # disk scale length (kpc), reference disk mass for mass-to-light = 1
TRUE = {"ml": 1.0, "rho0": 2.8e7, "rc": 4.0}  # disk + cored halo truth
R = np.linspace(1.0, 30.0, 40)


def bessel_i(n, x, terms=60):
    k = np.arange(terms)[:, None]
    fact = np.array([math.lgamma(i + 1) for i in range(terms)])[:, None]
    return np.exp((2 * k + n) * np.log(x / 2) - fact - np.array([math.lgamma(i + n + 1) for i in range(terms)])[:, None]).sum(0)


def bessel_k(n, x, tmax=12.0, steps=6000):
    """K_n(x) = integral_0^inf exp(-x cosh t) cosh(n t) dt (trapezoid on [0, tmax])."""
    t = np.linspace(0.0, tmax, steps)[:, None]
    f = np.exp(-x * np.cosh(t)) * np.cosh(n * t)
    return np.trapezoid(f, t[:, 0], axis=0)


_DISK = {}  # cache: the disk shape depends only on the radii; the fit only scales it by mass-to-light


def v_disk2(r, ml=1.0):
    r = np.asarray(r, float)
    key = r.tobytes()
    if key not in _DISK:
        y = r / (2 * RD)
        _DISK[key] = 2 * G * MD_REF / RD * y ** 2 * (bessel_i(0, y) * bessel_k(0, y) - bessel_i(1, y) * bessel_k(1, y))
    return ml * _DISK[key]


def v_iso2(r, rho0, rc):
    return 4 * np.pi * G * rho0 * rc ** 2 * (1 - (rc / r) * np.arctan(r / rc))


def v_nfw2(r, v200, c):
    r200 = v200 / (10 * H0)
    x = r / r200
    mu = lambda u: np.log(1 + u) - u / (1 + u)  # noqa: E731
    return v200 ** 2 * mu(c * x) / (x * mu(c))


def observed(seed=20, r=R):
    """Truth (disk + cored halo) + Gaussian errors of 2-6 km/s (larger outside, as HI curves often are)."""
    rng = np.random.default_rng(seed)
    v = np.sqrt(v_disk2(r, TRUE["ml"]) + v_iso2(r, TRUE["rho0"], TRUE["rc"]))
    err = 2.0 + 4.0 * r / r.max()
    return v + rng.normal(0, err), err
