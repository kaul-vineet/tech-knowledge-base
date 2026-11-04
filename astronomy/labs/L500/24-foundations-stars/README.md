# 24 · Foundations II: stars and radiation - luminosity, the HR diagram and the distance ladder

Numerical checks of the three theorems in lesson 24: the Planck integral and sigma from exact constants, L = 4 pi R^2 sigma T^4 against the IAU nominal Sun and the slope-4 radius lines of the HR diagram; a seeded synthetic main sequence (mass-luminosity fit, lifetimes); and a seeded synthetic distance ladder (parallax -> Cepheid P-L -> 8 SN Ia hosts -> Hubble flow), plus the real l Car parallax.

Read the concept note first: `../../../content/concepts/L500/24-foundations-stars.md`. Python 3.12 + numpy only (no extra packages).

## Run
```bash
python stars.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L500\24-foundations-stars` on Windows, `cd labs/L500/24-foundations-stars` on macOS). Runtime: about 2 s.

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux; seeded, identical on every run)
```
[stefan_boltzmann] PASS
  int_0^inf x^3/(e^x - 1) dx: quadrature 6.4939394023, series 6*sum(1/n^4) 6.4939391504, pi^4/15 6.4939394023
  sigma = 2 pi^5 k^4 / (15 c^2 h^3) = 5.670374419e-08 W m^-2 K^-4 (CODATA 5.670374419e-08)
  pi * int B_lambda d lambda at 5772 K = 6.29386e+07 W/m^2 vs sigma T^4 = 6.29386e+07
  4 pi R_sun^2 sigma T_sun^4 = 3.8280e+26 W vs nominal L_sun 3.8280e+26 W (rel. diff 2.4e-06)
  HR diagram: at fixed R, d log L / d log T = 4.000000, 4.000000 (lines of constant radius have slope 4)
[mass_luminosity] PASS
  synthetic main sequence (60 stars, L = M^3.5 x 0.05 dex scatter): fitted log L = 3.481 log M + +0.002
    M =   0.50 Msun  L =  1.033e-01 Lsun  R =  0.57 Rsun  Teff =    4317 K
    M =   1.75 Msun  L =  6.026e+00 Lsun  R =  1.56 Rsun  Teff =    7236 K
    M =   6.10 Msun  L =  5.061e+02 Lsun  R =  4.25 Rsun  Teff =   13285 K
    M =  20.00 Msun  L =  3.265e+04 Lsun  R = 10.99 Rsun  Teff =   23410 K
  Sun: M = GM/G = 1.98848e+30 kg; t = 0.007 x 0.1 x M c^2 / L = 10.36 Gyr
  t(M) = t_sun M / L = t_sun M^-2.5: 2 Msun 1.83 Gyr, 10 Msun 33 Myr, 0.5 Msun 59 Gyr
[distance_ladder] PASS
  parallax 2.01 mas: d = 1/p = 497.5 pc (exact 1 au / tan p: rel. diff 1.1e-16); mu = 8.48
  rung 1 (40 Cepheids, sigma_parallax 0.02 mas): P-L slope -2.334, zero point -4.055 (true -2.43, -4.05)
  rung 2 (8 hosts at 10-40 Mpc, 25 Cepheids + 1 SN Ia each): M_SN = -19.338 (true -19.3); hosts span -19.424 .. -19.184
  rung 3 (60 SNe, 0.01 < z < 0.05): H0 = 68.68 km/s/Mpc (true 70.0); calibrating on host 1 alone gives 67.24
  error propagation: sigma_mu = 0.10 mag -> sigma_d/d = (ln 10 / 5) 0.10 = 0.0461; Monte Carlo 0.0461
ALL CHECKS PASS
```

## Test
```bash
python -m unittest -v
```
Observed: `Ran 4 tests ... OK`.

## How this is verified
`python research/l500_checks.py` (from the astronomy folder) re-runs every theorem check, compares it with the `checkOutput` recorded in `content/L500.json` (numbers within 2 units of the last printed digit), and recomputes every numeric answer in the problem sets.
