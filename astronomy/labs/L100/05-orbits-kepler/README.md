# 05 · Orbits

Solve Kepler's equation with Newton's method and compute Earth, Mars and Jupiter positions from JPL's approximate elements.

Read the concept note first: `../../../content/concepts/05-orbits-kepler.md`.

## Run
```bash
python kepler.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L100\05-orbits-kepler` on Windows, `cd labs/L100/05-orbits-kepler` on macOS).

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux; deterministic, identical on every run)
`python kepler.py`:
```
JD(TDB) 2461342.5 | Kepler: M=1.0 rad, e=0.5 -> E = 1.498701133518 rad
EM Bary  helio x=+0.81174 y=+0.57275 z=-0.00003 au  r=0.99346 au  period 1.0000 yr
Mars     helio x=-0.24837 y=+1.57099 z=+0.03901 au  r=1.59098 au  period 1.8808 yr
Jupiter  helio x=-3.64944 y=+3.86168 z=+0.06561 au  r=5.31369 au  period 11.8677 yr
Mars     geocentric RA 139.6593 deg (9.3106 h)  Dec +17.2889 deg  distance 1.4567 au
Jupiter  geocentric RA 146.1564 deg (9.7438 h)  Dec +14.2936 deg  distance 5.5429 au
```

## Test
```bash
python -m unittest -v
```
Observed: `Ran 7 tests ... OK (skipped=1)` - library comparisons are skipped locally (not installed) and run in CI.

## Try it
```bash
python try_it.py
```
Observed:
```
e=0.1: fixed-point needs 9 iterations; Newton gives the same E = 1.088597752
e=0.9: fixed-point needs 20 iterations; Newton gives the same E = 1.862086687
closest Mars-Earth distance 2026-2027: 0.6778 au at JD 2461456.5 (2027-02-20)
```

## Library equivalent (pending-ci)
`kepler_skyfield.py` compares Mars with Skyfield 1.55 and JPL DE421 (downloads de421.bsp, about 17 MB). **Not run yet** (pending-ci).

## Notes
Elements: JPL *Approximate Positions of the Planets*, Table 1 (valid 1800-2050; Mars nominal error 40 arcsec in longitude).

## Files
- `kepler.py` - main lab code (JPL Table 1 elements embedded)
- `kepler_skyfield.py` - Skyfield 1.55 + DE421 equivalent (pending-ci)
- `test_kepler.py` - Kepler residuals, Earth distance, third law
- `try_it.py` - tryIt script
