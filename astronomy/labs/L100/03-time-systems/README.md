# 03 · Time systems

Convert one UTC moment to JD, MJD, TAI and TT with the IERS leap-second table, and compute sidereal time checked against a published IAU 2006 worked example and official formulas (USNO, IERS Conventions 2010).

Read the concept note first: `../../../content/concepts/03-time-systems.md`.

## Run
```bash
python timescales.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L100\03-time-systems` on Windows, `cd labs/L100/03-time-systems` on macOS).

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux; deterministic, identical on every run)
`python timescales.py`:
```
JD(UTC)    2461343.145833
MJD(UTC)   61342.645833
TAI-UTC s  37
TT-UTC s   69.184000
JD(TT)     2461343.146634
GMST 18h01m54.54s | LST at +77.03 deg: 23h10m01.74s
J2000.0 in UTC: 2000-01-01T11:58:55.816+00:00
Worked example 2006-01-15 21:24:37.5 UTC: ERA 05h05m03.70s (published 05h05m03.70s) | GAST 05h05m22.19s (published 05h05m22.21s, diff -0.023 s)
GMST short vs USNO full formula: 18h01m54.55s (diff -0.010 s)
J2000.0 GMST 18h41m50.55s | IERS ERA 18h41m50.55s (diff +0.0016 s)
```

## Test
```bash
python -m unittest -v
```
Observed: `Ran 11 tests ... OK (skipped=1)` - library comparisons are skipped locally (not installed) and run in CI.

## Try it
```bash
python try_it.py
```
Observed:
```
2016-12-31T23:59:59 TAI-UTC = 36 s
2017-01-01T00:00:01 TAI-UTC = 37 s
lon 77.03: LST 23h10m01.74s
lon 92.03: LST 00h10m01.74s
```

## Library equivalent (pending-ci)
`time_astropy.py` compares TT-UTC and GMST with Astropy 8.0.2 `Time`. Not installed offline: **not run yet**; CI runs it (Astropy may download IERS Earth-orientation data).

## Notes
Sidereal-time checks (official and primary sources only):
- **IAU 2006 worked example** ([Wallace & Capitaine 2006, A&A 459, 981](https://syrte.obspm.fr/iau2006/aa06_459.IAU06prec.pdf), appendix; the paper behind the SOFA/IERS procedures): for UTC 2006-01-15 21:24:37.5 with UT1-UTC = +0.3341 s it gives ERA = 76.265431053522° = 5h05m03.703s and Greenwich apparent sidereal time 5h05m22.213s. `era_hours` reproduces the ERA to 0.00001 s; `gast_hours` (short GMST + USNO's approximate equation of the equinoxes) gives 5h05m22.190s, 0.023 s off (USNO quotes about 0.1 s accuracy). `test_worked_example_wallace_capitaine_2006` checks both.
- **USNO** ([Computing Approximate Sidereal Time](https://aa.usno.navy.mil/faq/GAST), adapted from USNO Circular 179 sec. 2.6.2) gives a full GMST formula (0h-UT1 split, TT-century terms) and the short form used here, which has "a loss of precision of 0.1 second per century". `test_short_formula_matches_usno_full_formula` requires agreement within 0.05 s on four dates (observed: 0.002-0.010 s).
- **IERS Conventions (2010)** eq. 5.14 defines the Earth rotation angle, ERA = 2π(0.7790572732640 + 1.00273781191135448 Tu). At J2000.0 GMST and ERA start from the same point; the lab's 18.697375 h is that turn fraction rounded (diff 0.0016 s). Away from J2000 GMST also contains precession in right ascension, so ERA alone is not a GMST check (IERS eq. 5.32 polynomial not reproduced here; Astropy in CI covers it).
- UTC stands in for UT1 (|UT1-UTC| < 0.9 s).

Leap-second values: IERS `Leap_Second.dat` (Bulletin C 72, July 2026; file expires 2027-06-28). `test_leap_table_not_expired` is time-sensitive on purpose.

## Files
- `timescales.py` - main lab code (leap-second table embedded)
- `time_astropy.py` - Astropy 8.0.2 Time equivalent (pending-ci)
- `test_timescales.py` - scales, sidereal time vs the IAU 2006 worked example and USNO / IERS formulas, freshness
- `try_it.py` - tryIt script
