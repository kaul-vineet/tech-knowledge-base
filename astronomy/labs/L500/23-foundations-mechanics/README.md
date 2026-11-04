# 23 · Foundations I: classical mechanics, gravitation and spherical trigonometry

Numerical checks of the four theorems in lesson 23: Kepler's third law (leapfrog period vs formula), vis-viva and escape speed (measured semi-major axis, bound/unbound launches), the virial theorem (instantaneous vs time-averaged 2K/|U|), and the spherical cosine rule / alt-az formula (random triangles, an independent rotation matrix, and lesson 2's `sky.py` imported unchanged).

Read the concept note first: `../../../content/concepts/L500/23-foundations-mechanics.md`. Python 3.12 + numpy only (no extra packages).

## Run
```bash
python mechanics.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L500\23-foundations-mechanics` on Windows, `cd labs/L500/23-foundations-mechanics` on macOS). Runtime: about 15 s.

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux; seeded, identical on every run)
```
[kepler3] PASS
  Earth (a = 1 au, GM_sun): T = 365.2569 d
  Jupiter's own mass shortens its period by a factor 0.999523 (= (1 + m/M)^-1/2)
  leapfrog circular orbit, m/M = 0.0009546: T = 0.99952317 yr vs formula 0.99952304 yr (rel. diff 1.3e-07)
[vis_viva] PASS
  e = 0.6 orbit, 100001 samples: a measured = 1.000000 au, max |v^2 - GM(2/r - 1/a)| / v^2 = 3.0e-08
  escape speed: Earth surface 11.18 km/s; from the Sun at 1 au 42.1 km/s
  launch at 0.99 v_esc from 1 au: after 100 yr r = 37.8 au, specific energy -0.785
  launch at 1.01 v_esc from 1 au: after 100 yr r = 170.3 au, specific energy +0.794
[virial] PASS
  instantaneous 2K/|U| over an e = 0.6 orbit ranges 0.400 .. 1.600
  time-averaged 2<K>/|<U>| over 3 whole orbits = 1.000000; over the first quarter orbit = 1.249
[altaz] PASS
  spherical cosine rule on 10000 random triangles: max error 1.9e-14
  sin h = sin d sin phi + cos d cos phi cos H vs rotation matrix, 20000 points: max |d alt| = 3.0e-13 deg
  lesson-2 sky.altaz vs rotation, 10 stars at Gurgaon 15:30 UTC: max |d alt| 7.1e-15 deg, max |d az| 2.8e-14 deg; Deneb alt 56.27 deg
ALL CHECKS PASS
```

## Test
```bash
python -m unittest -v
```
Observed: `Ran 5 tests ... OK`.

## How this is verified
`python research/l500_checks.py` (from the astronomy folder) re-runs every theorem check, compares it with the `checkOutput` recorded in `content/L500.json` (numbers within 2 units of the last printed digit), and recomputes every numeric answer in the problem sets.
