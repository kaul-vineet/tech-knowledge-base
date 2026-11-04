# 25 · Foundations III: cosmology and Bayesian data analysis

Numerical checks of the four theorems in lesson 25: Hubble's law seen from two different galaxies and the low-z d_L correction; critical density and the flat-LCDM age by integral, closed form and an RK4 Friedmann integration; detailed balance (exact transition matrix, a long chain, and a biased proposal with and without the Hastings factor); and the conjugate H0 posterior against a grid and the Metropolis sampler of lesson 15.

Read the concept note first: `../../../content/concepts/L500/25-foundations-cosmology-bayes.md`. Python 3.12 + numpy only (no extra packages).

## Run
```bash
python cosmo_bayes.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L500\25-foundations-cosmology-bayes` on Windows, `cd labs/L500/25-foundations-cosmology-bayes` on macOS). Runtime: about 10 s.

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux; seeded, identical on every run)
```
[hubble_law] PASS
  observer at galaxy 0: v/r ranges 67.4000000000 .. 67.4000000000 km/s/Mpc, min cos(angle v, r) = 1.000000000000
  observer at galaxy 137: v/r ranges 67.4000000000 .. 67.4000000000 km/s/Mpc, min cos(angle v, r) = 1.000000000000
  D_L / (cz/H0) - 1 at z = [0.001, 0.002, 0.005, 0.01, 0.02]: ['0.00076', '0.00153', '0.00381', '0.00761', '0.01516']
  small-z slope 0.7620 vs (1 - q0)/2 = 0.7638 with q0 = Om/2 - OL = -0.5275
  Hubble time 1/H0: H0 = 67.4 -> 14.51 Gyr; Hubble (1929) K = 500 -> 1.96 Gyr
[friedmann_age] PASS
  critical density 3H0^2/(8 pi G) = 8.5331e-27 kg/m^3 = 1.2608e+11 Msun/Mpc^3
  age, flat LCDM (Om = 0.315): integral 13.7962 Gyr, closed form 13.7962 Gyr, RK4 Friedmann ODE 13.7962 Gyr
  Einstein-de Sitter (Om = 1): 2/(3 H0) = 9.67 Gyr
[detailed_balance] PASS
  symmetric proposal: max |pi_i K_ij - pi_j K_ji| = 0.0e+00; max |pi K - pi| = 5.6e-17
  200000-step chain: max |frequency - pi| = 0.0027
  biased proposal 0.8/0.2: total-variation distance to pi without Hastings factor 0.175, with it 2.7e-14
[conjugate_posterior] PASS
  20 synthetic galaxies, sigma_v = 300 km/s, true H0 = 70: closed form 71.696 +/- 2.116
  grid posterior 71.696 +/- 2.116; Metropolis (55000 kept, acceptance 0.61) 71.688 +/- 2.098
  with Gaussian prior N(67.4, 0.5): posterior 67.627 +/- 0.487
  with Gaussian prior N(73.0, 1.0): posterior 72.762 +/- 0.904
ALL CHECKS PASS
```

## Test
```bash
python -m unittest -v
```
Observed: `Ran 4 tests ... OK`.

## How this is verified
`python research/l500_checks.py` (from the astronomy folder) re-runs every theorem check, compares it with the `checkOutput` recorded in `content/L500.json` (numbers within 2 units of the last printed digit), and recomputes every numeric answer in the problem sets.
