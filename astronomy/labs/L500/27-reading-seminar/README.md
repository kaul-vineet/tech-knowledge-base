# 27 · Reading seminar: Hubble (1929) and the Gaia DR3 summary

Recomputes the papers' own numbers before you critique them: Hubble's K = 500 as a Hubble time, NGC 7619's distance and absolute magnitude, the 'K of 530' cross-check, and two Gaia DR3 fractions. Read the papers themselves (links in content/L500.json); this repository summarises them and does not reproduce them.

Read the concept note first: `../../../content/concepts/L500/27-reading-seminar.md`. Python 3.12 + numpy only (no extra packages).

## Run
```bash
python reading_checks.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L500\27-reading-seminar` on Windows, `cd labs/L500/27-reading-seminar` on macOS). Runtime: instant.

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux; seeded, identical on every run)
```
Hubble 1929: K = 500 km/s/Mpc -> 1/K = 1.96 Gyr
NGC 7619: v = +3910 km/s (solar-motion corrected) / K = 7.82 Mpc (paper: 7.8 x 10^6 pc)
NGC 7619: m = 11.8 at 7.8 Mpc -> M = -17.66 (paper: -17.65)
22 nebulae without individual distances: 745 km/s at 1.4 Mpc -> K = 532 (paper: 530)
modern H0 = 67.4: NGC 7619 at 58.0 Mpc; K/H0 = 7.42 (the 1929 distance scale was too short by this factor)
Gaia DR3: >33 million radial velocities / ~1500 million sources with class probabilities = 2.2%
Gaia DR3: 34 months of data = 2.83 yr
```

## Test
```bash
python -m unittest -v
```
Observed: `Ran 2 tests ... OK`.

## How this is verified
`python research/l500_checks.py` (from the astronomy folder) re-runs every theorem check, compares it with the `checkOutput` recorded in `content/L500.json` (numbers within 2 units of the last printed digit), and recomputes every numeric answer in the problem sets.
