# Explain runs - every command quoted in content/explain/NN.md

Recorded for EXPLAIN-SPEC.md. Every "What you see" / "See it in numbers" block in `content/explain/` quotes output
from the runs below; `research/explain_checks.py` checks that every number in those blocks appears in this log.

- Date: 2026-11-02 (UTC times per command below). Linux sandbox, Python 3.12.15 + numpy 2.5.3 only; astropy,
  astroplan, skyfield, scipy, photutils, ccdproc, rebound, healpy, pyvo, lightkurve are NOT installed, so every
  library-equivalent test is skipped here ("pending-ci") and is described in the explanations as
  "Expected (not run here)" from the lab READMEs/official docs, never with invented numbers.
- Labs were run one at a time from their own folder (`cd labs/...`), exactly as written. `BUILD_TARGET=mine` runs test
  the shipped (unfixed) file; plain runs of `test_build_task` test `solution/`.
- Files a run writes (star_field.fits, calib_log.jsonl, master_flat.fits, work/, release/, data/, scorecard.jsonl,
  prov.jsonl, pipeline_metrics.jsonl, labs/data/) were restored to their pre-run bytes or removed afterwards, so the
  lab folders are unchanged.
- Passing-test lines (`... ok`) are omitted from unittest listings; every `Ran N tests` summary, failure and skip is kept.

Differences from the lab READMEs / lesson JSON are listed at the end.

### [01] `cd labs/L100/01-setup-workbench && python check_env.py`
run 2026-11-02 12:36 UTC, exit 0, 24 s
```
Python 3.12.15 on Linux x86_64
  numpy     pin 2.5.3   installed 2.5.3
  astropy   pin 8.0.2   not installed -> runs in CI
  skyfield  pin 1.55    not installed -> runs in CI
  scipy     pin 1.18.1  not installed -> runs in CI
  photutils pin 3.1.1   not installed -> runs in CI
data folders: data/raw, data/cache, data/derived
seed 42 stars (RA deg, mag): [(278.6242, 8.97), (157.9962, 2.94), (309.0953, 11.76)]
READY for local labs
```

### [01] `cd labs/L100/01-setup-workbench && python try_it.py`
run 2026-11-02 12:36 UTC, exit 0, 17 s
```
unseeded fields equal? False
seed 42 first star: (278.6242, 8.97) | seed 43 first star: (234.8277, 10.39)
```

### [01] `cd labs/L100/01-setup-workbench && python -m unittest -v`
run 2026-11-02 12:37 UTC, exit 0, 58 s
```

----------------------------------------------------------------------
Ran 5 tests in 0.218s

OK
```

### [02] `cd labs/L100/02-coordinates && python sky.py`
run 2026-11-02 12:39 UTC, exit 0, 17 s
```
observer lat +28.46 lon +77.03 | 2026-10-29 15:30 UTC | JD 2461343.14583 | LST 23.1671 h
star        alt(deg)  az(deg)  up?
Deneb          56.27   310.07  UP
Altair         39.35   257.43  UP
Vega           33.52   299.71  UP
Fomalhaut      31.84   183.17  UP
Polaris        28.93     0.65  UP
Capella        18.97    47.24  UP
Betelgeuse     -6.27    78.05  below
Arcturus      -24.58   311.22  below
Sirius        -28.46    94.49  below
Canopus       -33.23   136.60  below
```

### [02] `cd labs/L100/02-coordinates && python sky.py --lat 51.4778 --lon -0.0015 --utc 2026-10-29T21:00`
run 2026-11-02 12:39 UTC, exit 0, 17 s
```
observer lat +51.48 lon -0.00 | 2026-10-29 21:00 UTC | JD 2461343.37500 | LST 23.5468 h
star        alt(deg)  az(deg)  up?
Deneb          61.31   274.65  UP
Polaris        52.00     0.84  UP
Vega           38.62   286.48  UP
Capella        36.38    59.40  UP
Altair         27.98   247.23  UP
Fomalhaut       8.53   187.72  UP
Betelgeuse      2.33    81.02  UP
Arcturus      -10.88   321.15  below
Sirius        -24.22    86.64  below
Canopus       -44.90   123.45  below
```

### [02] `cd labs/L100/02-coordinates && python agent_assist.py --fake`
run 2026-11-02 12:40 UTC, exit 0, 22 s
```
1. agent proposed: {"visible": ["Vega", "Altair", "Sirius", "Polaris", "Canopus"], "reason": "bright stars that are usually seen on autumn evenings"}
2. code decided (altitude > 0): up = ['Altair', 'Capella', 'Deneb', 'Fomalhaut', 'Polaris', 'Vega']
   overruled (agent said visible, code says below): ['Canopus', 'Sirius']; missed: ['Capella', 'Deneb', 'Fomalhaut']; unknown names: none
3. agent explained: Deneb is highest at 56.27 degrees altitude; Canopus is lowest at -33.23 degrees, well below the horizon. Sirius rises at about 22:40 local time.
4. code checked 4 quoted numbers: 2 match the table; UNVERIFIED (treat as the model's guess): 22, 40
```

### [02] `cd labs/L100/02-coordinates && python -m unittest -v`
run 2026-11-02 12:40 UTC, exit 0, 48 s
```
test_astropy_agrees_within_precession (test_sky.TestAstropyEquivalent.test_astropy_agrees_within_precession) ... skipped 'astropy not installed (runs in CI)'

----------------------------------------------------------------------
Ran 12 tests in 1.020s

OK (skipped=1)
```

### [03] `cd labs/L100/03-time-systems && python timescales.py`
run 2026-11-02 12:45 UTC, exit 0, 19 s
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

### [03] `cd labs/L100/03-time-systems && python timescales.py --utc 2027-01-01T00:00 --lon -0.0015`
run 2026-11-02 12:45 UTC, exit 0, 1 s
```
JD(UTC)    2461406.500000
MJD(UTC)   61406.000000
TAI-UTC s  37
TT-UTC s   69.184000
JD(TT)     2461406.500801
GMST 06h41m41.31s | LST at -0.00 deg: 06h41m40.95s
J2000.0 in UTC: 2000-01-01T11:58:55.816+00:00
Worked example 2006-01-15 21:24:37.5 UTC: ERA 05h05m03.70s (published 05h05m03.70s) | GAST 05h05m22.19s (published 05h05m22.21s, diff -0.023 s)
GMST short vs USNO full formula: 06h41m41.31s (diff -0.005 s)
J2000.0 GMST 18h41m50.55s | IERS ERA 18h41m50.55s (diff +0.0016 s)
```

### [03] `cd labs/L100/03-time-systems && python -m unittest -v`
run 2026-11-02 12:45 UTC, exit 0, 17 s
```
test_astropy_scales_and_gmst (test_timescales.TestAstropyEquivalent.test_astropy_scales_and_gmst) ... skipped 'astropy not installed (runs in CI)'

----------------------------------------------------------------------
Ran 11 tests in 0.001s

OK (skipped=1)
```

### [04] `cd labs/L100/04-units-magnitudes && python units.py`
run 2026-11-02 12:46 UTC, exit 0, 13 s
```
1 AU = 149597870700 m | 1 ly = 9460730472580800 m | 1 pc = 3.085678e+16 m
1 pc = 206264.806 AU = 3.2616 ly | light from 1 AU takes 499.005 s
5 mag brighter = x100.0 flux | 1 mag = x2.5119
flux x2 -> -0.7526 mag
star with M = 4.83 at   10 pc: m =   4.83 (distance modulus  0.00)
star with M = 4.83 at  100 pc: m =   9.83 (distance modulus  5.00)
star with M = 4.83 at 1000 pc: m =  14.83 (distance modulus 10.00)
same star at 1 AU (the Sun): m = -26.74
parallax 0.1 arcsec -> 10.0 pc; modulus 5.00 -> 100.0 pc
```

### [04] `cd labs/L100/04-units-magnitudes && python -m unittest -v`
run 2026-11-02 12:47 UTC, exit 0, 2 s
```
test_astropy_constants_agree (test_units.TestAstropyEquivalent.test_astropy_constants_agree) ... skipped 'astropy not installed (runs in CI)'

----------------------------------------------------------------------
Ran 8 tests in 0.003s

OK (skipped=1)
```

### [05] `cd labs/L100/05-orbits-kepler && python kepler.py`
run 2026-11-02 12:47 UTC, exit 0, 2 s
```
JD(TDB) 2461342.5 | Kepler: M=1.0 rad, e=0.5 -> E = 1.498701133518 rad
EM Bary  helio x=+0.81174 y=+0.57275 z=-0.00003 au  r=0.99346 au  period 1.0000 yr
Mars     helio x=-0.24837 y=+1.57099 z=+0.03901 au  r=1.59098 au  period 1.8808 yr
Jupiter  helio x=-3.64944 y=+3.86168 z=+0.06561 au  r=5.31369 au  period 11.8677 yr
Mars     geocentric RA 139.6593 deg (9.3106 h)  Dec +17.2889 deg  distance 1.4567 au
Jupiter  geocentric RA 146.1564 deg (9.7438 h)  Dec +14.2936 deg  distance 5.5429 au
```

### [05] `cd labs/L100/05-orbits-kepler && python -m unittest -v`
run 2026-11-02 12:47 UTC, exit 0, 3 s
```
test_within_jpl_error_budget (test_kepler.TestSkyfieldEquivalent.test_within_jpl_error_budget) ... skipped 'skyfield not installed (runs in CI)'

----------------------------------------------------------------------
Ran 7 tests in 0.005s

OK (skipped=1)
```

### [06] `cd labs/L100/06-light-spectra && python light.py`
run 2026-11-02 12:47 UTC, exit 0, 3 s
```
Sun              T=  5772 K  Wien b/T =   502.0 nm  numerical peak =   502.0 nm
Betelgeuse-like  T=  3600 K  Wien b/T =   804.9 nm  numerical peak =   804.9 nm
Rigel-like       T= 12100 K  Wien b/T =   239.5 nm  numerical peak =   239.5 nm
Sun: pi * integral B = 6.2939e+07 W/m^2 vs sigma T^4 = 6.2939e+07 W/m^2
H-alpha observed at 656.50 nm: v = +100.5 km/s (z = 0.000335)
z = 0.001: cz =       300 km/s  relativistic Doppler v =       300 km/s
z = 0.1  : cz =     29979 km/s  relativistic Doppler v =     28487 km/s
z = 1.0  : cz =    299792 km/s  relativistic Doppler v =    179875 km/s
```

### [06] `cd labs/L100/06-light-spectra && python -m unittest -v`
run 2026-11-02 12:48 UTC, exit 0, 2 s
```
test_astropy_blackbody_and_constants (test_light.TestAstropyEquivalent.test_astropy_blackbody_and_constants) ... skipped 'astropy not installed (runs in CI)'

----------------------------------------------------------------------
Ran 8 tests in 0.115s

OK (skipped=1)
```

### [07] `cd labs/L200/07-crossmatch && python crossmatch.py`
run 2026-11-02 12:48 UTC, exit 0, 4 s
```
A 2000 sources, B 2042 sources (1812 true counterparts); the field wraps: 549 sources at RA 359.x deg
matched 1842 within 1 arcsec; correct 1812/1812; median sep 0.233 arcsec
k-d tree distance evaluations: 38,999 vs brute force 4,084,000
A sources claimed by more than one B source (blends): 25
RA 359.9999 vs 0.0001 at Dec 28: naive |dRA| = 359.9998 deg, true separation = 0.6357 arcsec
```

### [07] `cd labs/L200/07-crossmatch && python solution/crossmatch.py`
run 2026-11-02 12:48 UTC, exit 0, 10 s
```
A 2000 sources, B 2042 sources (1812 true counterparts); the field wraps: 549 sources at RA 359.x deg
matched 1842 within 1 arcsec; correct 1812/1812; median sep 0.233 arcsec
k-d tree distance evaluations: 38,999 vs brute force 4,084,000
A sources claimed by more than one B source (blends): 25
one-to-one: 1817 matches, true counterparts kept 1807/1812, duplicates left 0
RA 359.9999 vs 0.0001 at Dec 28: naive |dRA| = 359.9998 deg, true separation = 0.6357 arcsec
```

### [07] `cd labs/L200/07-crossmatch && BUILD_TARGET=mine python -m unittest test_build_task -v`
run 2026-11-02 12:48 UTC, exit 1, 10 s
```
test_no_a_source_claimed_twice (test_build_task.TestOneToOne.test_no_a_source_claimed_twice) ... FAIL

======================================================================
FAIL: test_no_a_source_claimed_twice (test_build_task.TestOneToOne.test_no_a_source_claimed_twice)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L200/07-crossmatch/test_build_task.py", line 29, in test_no_a_source_claimed_twice
    self.assertEqual(len(used), len(set(used.tolist())))
AssertionError: 1842 != 1817

----------------------------------------------------------------------
Ran 3 tests in 1.255s

FAILED (failures=1)
```

### [07] `cd labs/L200/07-crossmatch && python -m unittest -v`
run 2026-11-02 12:48 UTC, exit 0, 16 s
```
test_astropy_and_scipy_find_the_same_pairs (test_crossmatch.TestLibraryEquivalent.test_astropy_and_scipy_find_the_same_pairs) ... skipped 'astropy/scipy not installed (runs in CI)'

----------------------------------------------------------------------
Ran 10 tests in 1.356s

OK (skipped=1)
```

### [08] `cd labs/L200/08-fits-wcs && python fitslite.py`
run 2026-11-02 12:50 UTC, exit 0, 15 s
```
wrote star_field.fits (20160 bytes = 7 blocks of 2880); header cards: 17 incl. END
read back: shape (64, 64), dtype float32, identical: True
pixel (32.5, 32.5) -> RA 83.822100 Dec -5.391100
pixel (   1,    1) -> RA 83.830889 Dec -5.399850
pixel (  64,   64) -> RA 83.813311 Dec -5.382350
brightest pixel: numpy [row 45, col 51] = FITS pixel (52, 46)
```

### [08] `cd labs/L200/08-fits-wcs && python solution/fitslite.py`
run 2026-11-02 12:50 UTC, exit 0, 6 s
```
wrote star_field.fits (20160 bytes = 7 blocks of 2880); header cards: 17 incl. END
read back: shape (64, 64), dtype float32, identical: True
pixel (32.5, 32.5) -> RA 83.822100 Dec -5.391100 -> back to pixel (32.500000, 32.500000)
pixel (   1,    1) -> RA 83.830889 Dec -5.399850 -> back to pixel (1.000000, 1.000000)
pixel (  64,   64) -> RA 83.813311 Dec -5.382350 -> back to pixel (64.000000, 64.000000)
brightest pixel: numpy [row 45, col 51] = FITS pixel (52, 46)
```

### [08] `cd labs/L200/08-fits-wcs && BUILD_TARGET=mine python -m unittest test_build_task -v`
run 2026-11-02 12:51 UTC, exit 1, 4 s
```
test_crval_maps_to_crpix (test_build_task.TestSkyToPixel.test_crval_maps_to_crpix) ... ERROR
test_round_trip_whole_image (test_build_task.TestSkyToPixel.test_round_trip_whole_image) ... ERROR
test_round_trip_with_rotation (test_build_task.TestSkyToPixel.test_round_trip_with_rotation) ... ERROR

======================================================================
ERROR: test_crval_maps_to_crpix (test_build_task.TestSkyToPixel.test_crval_maps_to_crpix)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L200/08-fits-wcs/test_build_task.py", line 23, in test_crval_maps_to_crpix
    x, y = target.sky_to_pixel(target.WCS, 83.8221, -5.3911)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/workspace/working/kb/astronomy/labs/L200/08-fits-wcs/fitslite.py", line 75, in sky_to_pixel
    raise NotImplementedError("build task: invert pixel_to_sky (gnomonic projection, then the inverse CD matrix)")
NotImplementedError: build task: invert pixel_to_sky (gnomonic projection, then the inverse CD matrix)

======================================================================
ERROR: test_round_trip_whole_image (test_build_task.TestSkyToPixel.test_round_trip_whole_image)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L200/08-fits-wcs/test_build_task.py", line 30, in test_round_trip_whole_image
    bx, by = target.sky_to_pixel(target.WCS, ra, dec)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/workspace/working/kb/astronomy/labs/L200/08-fits-wcs/fitslite.py", line 75, in sky_to_pixel
    raise NotImplementedError("build task: invert pixel_to_sky (gnomonic projection, then the inverse CD matrix)")
NotImplementedError: build task: invert pixel_to_sky (gnomonic projection, then the inverse CD matrix)

======================================================================
ERROR: test_round_trip_with_rotation (test_build_task.TestSkyToPixel.test_round_trip_with_rotation)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L200/08-fits-wcs/test_build_task.py", line 36, in test_round_trip_with_rotation
    bx, by = target.sky_to_pixel(h, ra, dec)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/workspace/working/kb/astronomy/labs/L200/08-fits-wcs/fitslite.py", line 75, in sky_to_pixel
    raise NotImplementedError("build task: invert pixel_to_sky (gnomonic projection, then the inverse CD matrix)")
NotImplementedError: build task: invert pixel_to_sky (gnomonic projection, then the inverse CD matrix)

----------------------------------------------------------------------
Ran 3 tests in 0.007s

FAILED (errors=3)
```

### [08] `cd labs/L200/08-fits-wcs && python -m unittest -v`
run 2026-11-02 12:51 UTC, exit 0, 5 s
```
test_astropy_reads_our_file_and_agrees (test_fitslite.TestAstropyEquivalent.test_astropy_reads_our_file_and_agrees) ... skipped 'astropy not installed (runs in CI)'

----------------------------------------------------------------------
Ran 10 tests in 0.193s

OK (skipped=1)
```

### [09] `cd labs/L200/09-aperture-photometry && python photometry.py`
run 2026-11-02 12:51 UTC, exit 0, 3 s
```
star  true(e-)  measured(e-)  ratio   sky/px  SNR
   0     20000       20006.2  1.000   100.21  102.6
   1      8000        7774.1  0.972    99.99   48.4
   2      3000        3046.8  1.016    99.50   21.0
   3      1000         827.5  0.827   101.15    6.0
   4       300         436.0  1.453    99.28    3.2
aperture r=6 px holds 0.99966 of a star's light (Gaussian PSF)
```

### [09] `cd labs/L200/09-aperture-photometry && python solution/photometry.py`
run 2026-11-02 12:51 UTC, exit 0, 5 s
```
star  true(e-)  measured(e-)  ratio   sky/px  SNR
   0     20000       20006.2  1.000   100.21  102.6
   1      8000        7774.1  0.972    99.99   48.4
   2      3000        3046.8  1.016    99.50   21.0
   3      1000         827.5  0.827   101.15    6.0
   4       300         436.0  1.453    99.28    3.2
star 0: V = 10.000 +/- 0.011 (reference: star 0 = 10.000)
star 1: V = 11.026 +/- 0.022 (reference: star 0 = 10.000)
star 2: V = 12.043 +/- 0.052 (reference: star 0 = 10.000)
star 3: V = 13.459 +/- 0.181 (reference: star 0 = 10.000)
star 4: V = 14.154 +/- 0.338 (reference: star 0 = 10.000)
aperture r=6 px holds 0.99966 of a star's light (Gaussian PSF)
```

### [09] `cd labs/L200/09-aperture-photometry && python -m unittest -v`
run 2026-11-02 12:51 UTC, exit 0, 3 s
```
test_photutils_agrees (test_photometry.TestPhotutilsEquivalent.test_photutils_agrees) ... skipped 'photutils not installed (runs in CI)'

----------------------------------------------------------------------
Ran 11 tests in 0.311s

OK (skipped=1)
```

### [10] `cd labs/L200/10-light-curves && python periods.py`
run 2026-11-02 12:52 UTC, exit 0, 2 s
```
1104 points over 29.3 d (23 clear nights)
variable true P 0.5671 d | LS best 0.5669 d (power 0.770) | next peak 1.3074 d | skew +0.01
transit  true P 3.2127 d | LS best 0.3211 d (power 0.032) | next peak 1.5998 d | skew +0.82
1-day alias of the variable: 1 / (1/0.5671 - 1) = 1.3100 d
```

### [10] `cd labs/L200/10-light-curves && python solution/periods.py`
run 2026-11-02 12:52 UTC, exit 0, 51 s
```
1104 points over 29.3 d (23 clear nights)
variable true P 0.5671 d | LS best 0.5669 d (power 0.770) | next peak 1.3074 d | skew +0.01
transit  true P 3.2127 d | LS best 0.3211 d (power 0.032) | next peak 1.5998 d | skew +0.82
variable   bootstrap FAP (100 shuffles) = 0.010
transit    bootstrap FAP (100 shuffles) = 0.010
pure noise bootstrap FAP (100 shuffles) = 0.386
1-day alias of the variable: 1 / (1/0.5671 - 1) = 1.3100 d
```

### [10] `cd labs/L200/10-light-curves && python agent_assist.py --fake`
run 2026-11-02 12:53 UTC, exit 0, 12 s
```
1. agent proposed: class='pulsating variable', period=1.31 d
2. code decided: class='pulsating variable' (agent agrees), period=0.5669 d -> agent period overruled: 1-day alias of the code's period
3. agent explained: The periodogram peaks at 0.5669 days, so the star repeats every 0.5669 days. The false-alarm probability is below 0.001%, so the signal is certain.
4. code checked 3 quoted numbers: 2 match; UNVERIFIED (treat as the model's guess): 0.001
```

### [10] `cd labs/L200/10-light-curves && python -m unittest -v`
run 2026-11-02 12:53 UTC, exit 0, 11 s
```
test_astropy_lombscargle_matches (test_periods.TestAstropyEquivalent.test_astropy_lombscargle_matches) ... skipped 'astropy not installed (runs in CI)'

----------------------------------------------------------------------
Ran 13 tests in 8.222s

OK (skipped=1)
```

### [11] `cd labs/L200/11-nbody && python nbody.py`
run 2026-11-02 12:53 UTC, exit 0, 5 s
```
Euler    12 yr, dt=0.001 yr: |dE/E| = 1.24e-02, Earth-Sun distance 1.55347 au, centre of mass moved 0.0315 au
leapfrog 12 yr, dt=0.001 yr: |dE/E| = 1.22e-12, Earth-Sun distance 1.00000 au, centre of mass moved 0.0315 au
Jupiter period from Kepler's third law: 11.867 yr
```

### [11] `cd labs/L200/11-nbody && python solution/nbody.py`
run 2026-11-02 12:53 UTC, exit 0, 14 s
```
Euler    12 yr, dt=0.001 yr: |dE/E| = 1.24e-02, Earth-Sun distance 1.55347 au, centre of mass moved 0.0000 au
leapfrog 12 yr, dt=0.001 yr: |dE/E| = 1.26e-12, Earth-Sun distance 1.00000 au, centre of mass moved 0.0000 au
Jupiter period from Kepler's third law: 11.867 yr
```

### [11] `cd labs/L200/11-nbody && BUILD_TARGET=mine python -m unittest test_build_task -v`
run 2026-11-02 12:54 UTC, exit 1, 6 s
```
test_centre_of_mass_at_origin (test_build_task.TestCentreOfMassFrame.test_centre_of_mass_at_origin) ... FAIL
test_system_no_longer_drifts (test_build_task.TestCentreOfMassFrame.test_system_no_longer_drifts) ... FAIL
test_total_momentum_is_zero (test_build_task.TestCentreOfMassFrame.test_total_momentum_is_zero) ... FAIL

======================================================================
FAIL: test_centre_of_mass_at_origin (test_build_task.TestCentreOfMassFrame.test_centre_of_mass_at_origin)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L200/11-nbody/test_build_task.py", line 28, in test_centre_of_mass_at_origin
    self.assertLess(np.abs(target.MASSES @ pos).max(), 1e-15)
AssertionError: np.float64(0.00496640196) not less than 1e-15

======================================================================
FAIL: test_system_no_longer_drifts (test_build_task.TestCentreOfMassFrame.test_system_no_longer_drifts)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L200/11-nbody/test_build_task.py", line 32, in test_system_no_longer_drifts
    self.assertLess(com_shift, 1e-9)
AssertionError: np.float64(0.005254320653384874) not less than 1e-09

======================================================================
FAIL: test_total_momentum_is_zero (test_build_task.TestCentreOfMassFrame.test_total_momentum_is_zero)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L200/11-nbody/test_build_task.py", line 24, in test_total_momentum_is_zero
    self.assertLess(np.abs(target.MASSES @ vel).max(), 1e-15)
AssertionError: np.float64(0.0026296084103068222) not less than 1e-15

----------------------------------------------------------------------
Ran 3 tests in 0.673s

FAILED (failures=3)
```

### [11] `cd labs/L200/11-nbody && python -m unittest -v`
run 2026-11-02 12:54 UTC, exit 0, 2 s
```
test_rebound_agrees_on_earth_distance (test_nbody.TestReboundEquivalent.test_rebound_agrees_on_earth_distance) ... skipped 'rebound not installed (runs in CI)'

----------------------------------------------------------------------
Ran 10 tests in 0.434s

OK (skipped=1)
```

### [12] `cd labs/L300/12-observation-planning && python plan.py --check`
run 2026-11-02 12:54 UTC, exit 0, 2 s
```
Gurgaon, India 2026-11-24: astronomical darkness 18:50-05:20 local (10-min grid)
{"target": "Sirius", "start": "18:50", "alt_deg": -34.6, "airmass": -1.76, "moon_sep_deg": 59.5}
{"target": "Deneb", "start": "19:50", "alt_deg": 50.7, "airmass": 1.29, "moon_sep_deg": 84.0}
{"target": "Betelgeuse", "start": "22:10", "alt_deg": 31.5, "airmass": 1.92, "moon_sep_deg": 32.7}
{"target": "Vega", "start": "23:10", "alt_deg": -6.3, "airmass": -9.17, "moon_sep_deg": 106.2}
{"target": "Fomalhaut", "start": "00:10", "alt_deg": -3.2, "airmass": -18.11, "moon_sep_deg": 92.5}
{"target": "Altair", "start": "01:10", "alt_deg": -35.0, "airmass": -1.74, "moon_sep_deg": 115.9}
unscheduled: ['Aldebaran', 'Capella']
blocks below 30 deg altitude: ['Sirius', 'Vega', 'Fomalhaut', 'Altair']
```

### [12] `cd labs/L300/12-observation-planning && python solution/plan.py --check`
run 2026-11-02 12:54 UTC, exit 0, 3 s
```
Gurgaon, India 2026-11-24: astronomical darkness 18:50-05:20 local (10-min grid)
{"target": "Deneb", "start": "18:50", "alt_deg": 60.8, "airmass": 1.14, "moon_sep_deg": 83.7}
{"target": "Betelgeuse", "start": "22:10", "alt_deg": 31.5, "airmass": 1.91, "moon_sep_deg": 32.7}
{"target": "Sirius", "start": "00:10", "alt_deg": 30.2, "airmass": 1.98, "moon_sep_deg": 57.5}
unscheduled: ['Aldebaran', 'Altair', 'Capella', 'Fomalhaut', 'Vega']
blocks below 30 deg altitude: []
```

### [12] `cd labs/L300/12-observation-planning && BUILD_TARGET=mine python -m unittest test_build_task`
run 2026-11-02 12:54 UTC, exit 1, 6 s
```
.FFF/mnt/workspace/working/kb/astronomy/labs/L300/12-observation-planning/plan.py:27: RuntimeWarning: divide by zero encountered in scalar divide
  return 1.0 / np.sin(np.radians(alt_deg))
FFFFFFFFFFFF
======================================================================
FAIL: test_below_horizon_never_passes_the_limit (test_build_task.TestHorizonSafeAirmass.test_below_horizon_never_passes_the_limit) (alt=-60.0)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/12-observation-planning/test_build_task.py", line 28, in test_below_horizon_never_passes_the_limit
    self.assertFalse(float(target.airmass(alt)) <= target.MAX_AIRMASS)
AssertionError: True is not false

======================================================================
FAIL: test_below_horizon_never_passes_the_limit (test_build_task.TestHorizonSafeAirmass.test_below_horizon_never_passes_the_limit) (alt=-10.0)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/12-observation-planning/test_build_task.py", line 28, in test_below_horizon_never_passes_the_limit
    self.assertFalse(float(target.airmass(alt)) <= target.MAX_AIRMASS)
AssertionError: True is not false

======================================================================
FAIL: test_below_horizon_never_passes_the_limit (test_build_task.TestHorizonSafeAirmass.test_below_horizon_never_passes_the_limit) (alt=-0.5)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/12-observation-planning/test_build_task.py", line 28, in test_below_horizon_never_passes_the_limit
    self.assertFalse(float(target.airmass(alt)) <= target.MAX_AIRMASS)
AssertionError: True is not false

======================================================================
FAIL: test_every_scheduled_block_is_really_above_30_degrees (test_build_task.TestHorizonSafeAirmass.test_every_scheduled_block_is_really_above_30_degrees) (target='Sirius', minutes=0)
Re-check start, middle and end with ephem.py directly, independent of the file under test.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/12-observation-planning/test_build_task.py", line 46, in test_every_scheduled_block_is_really_above_30_degrees
    self.assertGreaterEqual(float(alt), 29.9)
AssertionError: -34.57441377066762 not greater than or equal to 29.9

======================================================================
FAIL: test_every_scheduled_block_is_really_above_30_degrees (test_build_task.TestHorizonSafeAirmass.test_every_scheduled_block_is_really_above_30_degrees) (target='Sirius', minutes=30)
Re-check start, middle and end with ephem.py directly, independent of the file under test.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/12-observation-planning/test_build_task.py", line 46, in test_every_scheduled_block_is_really_above_30_degrees
    self.assertGreaterEqual(float(alt), 29.9)
AssertionError: -27.97313911123101 not greater than or equal to 29.9

======================================================================
FAIL: test_every_scheduled_block_is_really_above_30_degrees (test_build_task.TestHorizonSafeAirmass.test_every_scheduled_block_is_really_above_30_degrees) (target='Sirius', minutes=60)
Re-check start, middle and end with ephem.py directly, independent of the file under test.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/12-observation-planning/test_build_task.py", line 46, in test_every_scheduled_block_is_really_above_30_degrees
    self.assertGreaterEqual(float(alt), 29.9)
AssertionError: -21.40312243279169 not greater than or equal to 29.9

======================================================================
FAIL: test_every_scheduled_block_is_really_above_30_degrees (test_build_task.TestHorizonSafeAirmass.test_every_scheduled_block_is_really_above_30_degrees) (target='Vega', minutes=0)
Re-check start, middle and end with ephem.py directly, independent of the file under test.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/12-observation-planning/test_build_task.py", line 46, in test_every_scheduled_block_is_really_above_30_degrees
    self.assertGreaterEqual(float(alt), 29.9)
AssertionError: -6.259268335034689 not greater than or equal to 29.9

======================================================================
FAIL: test_every_scheduled_block_is_really_above_30_degrees (test_build_task.TestHorizonSafeAirmass.test_every_scheduled_block_is_really_above_30_degrees) (target='Vega', minutes=30)
Re-check start, middle and end with ephem.py directly, independent of the file under test.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/12-observation-planning/test_build_task.py", line 46, in test_every_scheduled_block_is_really_above_30_degrees
    self.assertGreaterEqual(float(alt), 29.9)
AssertionError: -10.232014721198166 not greater than or equal to 29.9

======================================================================
FAIL: test_every_scheduled_block_is_really_above_30_degrees (test_build_task.TestHorizonSafeAirmass.test_every_scheduled_block_is_really_above_30_degrees) (target='Vega', minutes=60)
Re-check start, middle and end with ephem.py directly, independent of the file under test.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/12-observation-planning/test_build_task.py", line 46, in test_every_scheduled_block_is_really_above_30_degrees
    self.assertGreaterEqual(float(alt), 29.9)
AssertionError: -13.771491469760168 not greater than or equal to 29.9

======================================================================
FAIL: test_every_scheduled_block_is_really_above_30_degrees (test_build_task.TestHorizonSafeAirmass.test_every_scheduled_block_is_really_above_30_degrees) (target='Fomalhaut', minutes=0)
Re-check start, middle and end with ephem.py directly, independent of the file under test.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/12-observation-planning/test_build_task.py", line 46, in test_every_scheduled_block_is_really_above_30_degrees
    self.assertGreaterEqual(float(alt), 29.9)
AssertionError: -3.1649245463022617 not greater than or equal to 29.9

======================================================================
FAIL: test_every_scheduled_block_is_really_above_30_degrees (test_build_task.TestHorizonSafeAirmass.test_every_scheduled_block_is_really_above_30_degrees) (target='Fomalhaut', minutes=30)
Re-check start, middle and end with ephem.py directly, independent of the file under test.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/12-observation-planning/test_build_task.py", line 46, in test_every_scheduled_block_is_really_above_30_degrees
    self.assertGreaterEqual(float(alt), 29.9)
AssertionError: -8.856649239388844 not greater than or equal to 29.9

======================================================================
FAIL: test_every_scheduled_block_is_really_above_30_degrees (test_build_task.TestHorizonSafeAirmass.test_every_scheduled_block_is_really_above_30_degrees) (target='Fomalhaut', minutes=60)
Re-check start, middle and end with ephem.py directly, independent of the file under test.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/12-observation-planning/test_build_task.py", line 46, in test_every_scheduled_block_is_really_above_30_degrees
    self.assertGreaterEqual(float(alt), 29.9)
AssertionError: -14.72138641363439 not greater than or equal to 29.9

======================================================================
FAIL: test_every_scheduled_block_is_really_above_30_degrees (test_build_task.TestHorizonSafeAirmass.test_every_scheduled_block_is_really_above_30_degrees) (target='Altair', minutes=0)
Re-check start, middle and end with ephem.py directly, independent of the file under test.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/12-observation-planning/test_build_task.py", line 46, in test_every_scheduled_block_is_really_above_30_degrees
    self.assertGreaterEqual(float(alt), 29.9)
AssertionError: -34.97141272905266 not greater than or equal to 29.9

======================================================================
FAIL: test_every_scheduled_block_is_really_above_30_degrees (test_build_task.TestHorizonSafeAirmass.test_every_scheduled_block_is_really_above_30_degrees) (target='Altair', minutes=30)
Re-check start, middle and end with ephem.py directly, independent of the file under test.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/12-observation-planning/test_build_task.py", line 46, in test_every_scheduled_block_is_really_above_30_degrees
    self.assertGreaterEqual(float(alt), 29.9)
AssertionError: -40.054547582220245 not greater than or equal to 29.9

======================================================================
FAIL: test_every_scheduled_block_is_really_above_30_degrees (test_build_task.TestHorizonSafeAirmass.test_every_scheduled_block_is_really_above_30_degrees) (target='Altair', minutes=60)
Re-check start, middle and end with ephem.py directly, independent of the file under test.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/12-observation-planning/test_build_task.py", line 46, in test_every_scheduled_block_is_really_above_30_degrees
    self.assertGreaterEqual(float(alt), 29.9)
AssertionError: -44.54993654557436 not greater than or equal to 29.9

----------------------------------------------------------------------
Ran 3 tests in 0.173s

FAILED (failures=15)
```

### [12] `cd labs/L300/12-observation-planning && python -m unittest test_build_task -v`
run 2026-11-02 12:54 UTC, exit 0, 3 s
```
test_every_scheduled_block_is_really_above_30_degrees (test_build_task.TestHorizonSafeAirmass.test_every_scheduled_block_is_really_above_30_degrees)

----------------------------------------------------------------------
Ran 3 tests in 0.302s

OK
```

### [12] `cd labs/L300/12-observation-planning && python try_it.py`
run 2026-11-02 12:55 UTC, exit 0, 14 s
```
1. Sydney dark 21:30-03:50 | scheduled ['Fomalhaut@21:30', 'Sirius@23:10', 'Betelgeuse@00:10'] | unscheduled ['Aldebaran', 'Altair', 'Capella', 'Deneb', 'Vega']
2. Gurgaon, Moon >= 45 deg | scheduled ['Deneb@18:50', 'Sirius@00:10'] | unscheduled ['Aldebaran', 'Altair', 'Betelgeuse', 'Capella', 'Fomalhaut', 'Vega']
```

### [12] `cd labs/L300/12-observation-planning && python solution/urgent.py`
run 2026-11-02 12:55 UTC, exit 0, 1 s
```
{"target": "Altair", "start": "18:50", "alt_deg": 45.3, "airmass": 1.41, "moon_sep_deg": 112.7}
{"target": "Deneb", "start": "19:50", "alt_deg": 50.7, "airmass": 1.29, "moon_sep_deg": 84.0}
{"target": "Betelgeuse", "start": "22:10", "alt_deg": 31.5, "airmass": 1.91, "moon_sep_deg": 32.7}
{"target": "Sirius", "start": "00:10", "alt_deg": 30.2, "airmass": 1.98, "moon_sep_deg": 57.5}
unscheduled: ['Aldebaran', 'Capella', 'Fomalhaut', 'Vega']
```

### [12] `cd labs/L300/12-observation-planning && python -m unittest -v`
run 2026-11-02 12:55 UTC, exit 0, 14 s
```
test_every_scheduled_block_is_really_above_30_degrees (test_build_task.TestHorizonSafeAirmass.test_every_scheduled_block_is_really_above_30_degrees)
test_low_precision_sun_and_moon_agree_with_astropy (test_plan.TestAstroplanEquivalent.test_low_precision_sun_and_moon_agree_with_astropy) ... skipped 'astropy/astroplan not installed (pending-ci)'

----------------------------------------------------------------------
Ran 14 tests in 0.547s

OK (skipped=1)
```

### [13] `cd labs/L300/13-ccd-calibration && python calibrate.py`
run 2026-11-02 12:55 UTC, exit 0, 2 s
```
relative flux, every 5th frame: 0.9971 1.0070 1.0082 1.0031 1.0043 0.9881
{"rms_percent": 0.88, "robust_rms_percent": 0.899, "expected_noise_percent": 0.224, "variable": true}
master_flat min/max: 0.8527 1.0792 (true response 0.75/1.00)
```

### [13] `cd labs/L300/13-ccd-calibration && head -3 calib_log.jsonl`
run 2026-11-02 12:56 UTC, exit 0, 0 s
```
{"step": "master_bias", "median_adu": 999.95}
{"step": "master_dark", "median_adu": 2.04, "max_adu": 205.1}
{"step": "master_flat", "min": 0.8527, "max": 1.0792}
```

### [13] `cd labs/L300/13-ccd-calibration && grep -o '"cosmics_cleaned": [0-9]*' calib_log.jsonl | sort | uniq -c`
run 2026-11-02 12:56 UTC, exit 0, 0 s
```
     29 "cosmics_cleaned": 3
      1 "cosmics_cleaned": 4
```

### [13] `cd labs/L300/13-ccd-calibration && python solution/calibrate.py`
run 2026-11-02 12:56 UTC, exit 0, 11 s
```
relative flux, every 5th frame: 1.0002 1.0051 1.0022 1.0063 1.0033 1.0020
{"rms_percent": 0.389, "robust_rms_percent": 0.382, "expected_noise_percent": 0.224, "variable": false}
master_flat min/max: 0.813 1.1009 (true response 0.75/1.00)
```

### [13] `cd labs/L300/13-ccd-calibration && BUILD_TARGET=mine python -m unittest test_build_task`
run 2026-11-02 12:56 UTC, exit 1, 13 s
```
FFFFFFFFFFFF
======================================================================
FAIL: test_constant_star_is_not_variable (test_build_task.TestFlatField.test_constant_star_is_not_variable)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/13-ccd-calibration/test_build_task.py", line 26, in test_constant_star_is_not_variable
    self.assertFalse(s["variable"])
AssertionError: True is not false

======================================================================
FAIL: test_master_flat_matches_the_true_response (test_build_task.TestFlatField.test_master_flat_matches_the_true_response)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/13-ccd-calibration/test_build_task.py", line 32, in test_master_flat_matches_the_true_response
    self.assertLess(float(np.abs(flat / truth - 1).max()), 0.03)
AssertionError: 0.05086357058515789 not less than 0.03

======================================================================
FAIL: test_other_nights_are_not_variable_either (test_build_task.TestFlatField.test_other_nights_are_not_variable_either) (seed=20)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/13-ccd-calibration/test_build_task.py", line 37, in test_other_nights_are_not_variable_either
    self.assertFalse(target.run(seed=seed, log_path=None)[1]["variable"])
AssertionError: True is not false

======================================================================
FAIL: test_other_nights_are_not_variable_either (test_build_task.TestFlatField.test_other_nights_are_not_variable_either) (seed=21)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/13-ccd-calibration/test_build_task.py", line 37, in test_other_nights_are_not_variable_either
    self.assertFalse(target.run(seed=seed, log_path=None)[1]["variable"])
AssertionError: True is not false

======================================================================
FAIL: test_other_nights_are_not_variable_either (test_build_task.TestFlatField.test_other_nights_are_not_variable_either) (seed=22)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/13-ccd-calibration/test_build_task.py", line 37, in test_other_nights_are_not_variable_either
    self.assertFalse(target.run(seed=seed, log_path=None)[1]["variable"])
AssertionError: True is not false

======================================================================
FAIL: test_other_nights_are_not_variable_either (test_build_task.TestFlatField.test_other_nights_are_not_variable_either) (seed=23)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/13-ccd-calibration/test_build_task.py", line 37, in test_other_nights_are_not_variable_either
    self.assertFalse(target.run(seed=seed, log_path=None)[1]["variable"])
AssertionError: True is not false

======================================================================
FAIL: test_other_nights_are_not_variable_either (test_build_task.TestFlatField.test_other_nights_are_not_variable_either) (seed=24)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/13-ccd-calibration/test_build_task.py", line 37, in test_other_nights_are_not_variable_either
    self.assertFalse(target.run(seed=seed, log_path=None)[1]["variable"])
AssertionError: True is not false

======================================================================
FAIL: test_other_nights_are_not_variable_either (test_build_task.TestFlatField.test_other_nights_are_not_variable_either) (seed=25)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/13-ccd-calibration/test_build_task.py", line 37, in test_other_nights_are_not_variable_either
    self.assertFalse(target.run(seed=seed, log_path=None)[1]["variable"])
AssertionError: True is not false

======================================================================
FAIL: test_other_nights_are_not_variable_either (test_build_task.TestFlatField.test_other_nights_are_not_variable_either) (seed=26)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/13-ccd-calibration/test_build_task.py", line 37, in test_other_nights_are_not_variable_either
    self.assertFalse(target.run(seed=seed, log_path=None)[1]["variable"])
AssertionError: True is not false

======================================================================
FAIL: test_other_nights_are_not_variable_either (test_build_task.TestFlatField.test_other_nights_are_not_variable_either) (seed=27)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/13-ccd-calibration/test_build_task.py", line 37, in test_other_nights_are_not_variable_either
    self.assertFalse(target.run(seed=seed, log_path=None)[1]["variable"])
AssertionError: True is not false

======================================================================
FAIL: test_other_nights_are_not_variable_either (test_build_task.TestFlatField.test_other_nights_are_not_variable_either) (seed=28)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/13-ccd-calibration/test_build_task.py", line 37, in test_other_nights_are_not_variable_either
    self.assertFalse(target.run(seed=seed, log_path=None)[1]["variable"])
AssertionError: True is not false

======================================================================
FAIL: test_other_nights_are_not_variable_either (test_build_task.TestFlatField.test_other_nights_are_not_variable_either) (seed=29)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/13-ccd-calibration/test_build_task.py", line 37, in test_other_nights_are_not_variable_either
    self.assertFalse(target.run(seed=seed, log_path=None)[1]["variable"])
AssertionError: True is not false

----------------------------------------------------------------------
Ran 3 tests in 10.810s

FAILED (failures=12)
```

### [13] `cd labs/L300/13-ccd-calibration && python -m unittest test_build_task -v`
run 2026-11-02 12:56 UTC, exit 0, 10 s
```

----------------------------------------------------------------------
Ran 3 tests in 6.565s

OK
```

### [13] `cd labs/L300/13-ccd-calibration && python solution/gain.py`
run 2026-11-02 12:56 UTC, exit 0, 20 s
```
measured gain 1.473 e-/ADU (true 1.5), read noise 6.89 e- (true 7.0)
```

### [13] `cd labs/L300/13-ccd-calibration && python try_it.py`
run 2026-11-02 12:56 UTC, exit 0, 25 s
```
1. no cleaning: frame 17 relative flux 1.1640; plain rms 2.96%, robust rms 0.377%, variable=False
2. shipped flat, 30k e- flats: robust rms 0.366%, variable=False, flat min 0.8267 (fixed pipeline gives 0.813 at 6k e-)
```

### [13] `cd labs/L300/13-ccd-calibration && python -m unittest -v`
run 2026-11-02 12:57 UTC, exit 0, 33 s
```
test_ccdproc_light_curve_is_also_flat (test_calibrate.TestCcdprocEquivalent.test_ccdproc_light_curve_is_also_flat) ... skipped 'astropy/ccdproc not installed (pending-ci)'

----------------------------------------------------------------------
Ran 12 tests in 16.702s

OK (skipped=1)
```

### [14] `cd labs/L300/14-plate-solving && python platesolve.py`
run 2026-11-02 12:58 UTC, exit 0, 9 s
```
{"field": "orion", "solved": true, "n_matched": 32, "rms_arcsec": 0.373, "pointing_error_arcsec": 0.07, "scale_arcsec_px": 2.0045, "rotation_deg": 11.991}
{"field": "cassiopeia", "solved": false}
```

### [14] `cd labs/L300/14-plate-solving && python try_it.py`
run 2026-11-02 12:58 UTC, exit 0, 17 s
```
1. orion      Dec -5.4: invariants flat [1.049 1.083] vs TAN [1.051 1.078] (max relative difference 0.004; match tolerance 0.008)
1. cassiopeia Dec +62.1: invariants flat [1.049 1.083] vs TAN [1.097 1.685] (max relative difference 0.357; match tolerance 0.008)
2. TOL 0.008: 12 voted pairs, 8 agree with the best geometry
2. TOL 0.05: 12 voted pairs, 3 agree with the best geometry
```

### [14] `cd labs/L300/14-plate-solving && python solution/platesolve.py`
run 2026-11-02 12:58 UTC, exit 0, 13 s
```
{"field": "orion", "solved": true, "n_matched": 32, "rms_arcsec": 0.359, "pointing_error_arcsec": 0.07, "scale_arcsec_px": 2.0001, "rotation_deg": 11.99}
{"field": "cassiopeia", "solved": true, "n_matched": 23, "rms_arcsec": 0.503, "pointing_error_arcsec": 0.05, "scale_arcsec_px": 2.0002, "rotation_deg": -32.999}
```

### [14] `cd labs/L300/14-plate-solving && BUILD_TARGET=mine python -m unittest test_build_task`
run 2026-11-02 12:58 UTC, exit 1, 19 s
```
FFF
======================================================================
FAIL: test_both_fields_solve_to_sub_arcsecond_accuracy (test_build_task.TestTanProjection.test_both_fields_solve_to_sub_arcsecond_accuracy) (field='cassiopeia')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/14-plate-solving/test_build_task.py", line 26, in test_both_fields_solve_to_sub_arcsecond_accuracy
    self.assertTrue(r["solved"])
AssertionError: False is not true

======================================================================
FAIL: test_pixel_scale_is_the_camera_scale (test_build_task.TestTanProjection.test_pixel_scale_is_the_camera_scale) (field='orion')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/14-plate-solving/test_build_task.py", line 35, in test_pixel_scale_is_the_camera_scale
    self.assertAlmostEqual(r.get("scale_arcsec_px", 0.0), fields.SCALE_ARCSEC, delta=0.001)
AssertionError: 2.0045 != 2.0 within 0.001 delta (0.0045000000000001705 difference)

======================================================================
FAIL: test_pixel_scale_is_the_camera_scale (test_build_task.TestTanProjection.test_pixel_scale_is_the_camera_scale) (field='cassiopeia')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/14-plate-solving/test_build_task.py", line 35, in test_pixel_scale_is_the_camera_scale
    self.assertAlmostEqual(r.get("scale_arcsec_px", 0.0), fields.SCALE_ARCSEC, delta=0.001)
AssertionError: 0.0 != 2.0 within 0.001 delta (2.0 difference)

----------------------------------------------------------------------
Ran 2 tests in 15.370s

FAILED (failures=3)
```

### [14] `cd labs/L300/14-plate-solving && python -m unittest test_build_task -v`
run 2026-11-02 12:59 UTC, exit 0, 19 s
```

----------------------------------------------------------------------
Ran 2 tests in 14.710s

OK
```

### [14] `cd labs/L300/14-plate-solving && python solution/search.py`
run 2026-11-02 12:59 UTC, exit 0, 16 s
```
plain solve, hint 0.8 deg off: {"field": "orion", "solved": false}
search (5 hints tried): {"field": "orion", "solved": true, "n_matched": 32, "rms_arcsec": 0.359, "pointing_error_arcsec": 0.07, "scale_arcsec_px": 2.0001, "rotation_deg": 11.99}
```

### [14] `cd labs/L300/14-plate-solving && python -m unittest -v`
run 2026-11-02 12:59 UTC, exit 0, 40 s
```
test_astropy_scale_matches (test_platesolve.TestAstropyEquivalent.test_astropy_scale_matches) ... skipped 'astropy not installed (pending-ci)'

----------------------------------------------------------------------
Ran 9 tests in 35.419s

OK (skipped=1)
```

### [15] `cd labs/L300/15-honest-uncertainty && python transit_fit.py`
run 2026-11-02 13:01 UTC, exit 0, 14 s
```
{"param": "t0_h", "true": 0.12, "fit": 0.15667, "sigma_formal": 0.00601, "sigma_bootstrap": 0.0128}
{"param": "depth", "true": 0.01, "fit": 0.00963, "sigma_formal": 0.00013, "sigma_bootstrap": 0.00026}
{"param": "T14_h", "true": 2.5, "fit": 2.41574, "sigma_formal": 0.0256, "sigma_bootstrap": 0.04615}
{"param": "T12_h", "true": 0.3, "fit": 0.19103, "sigma_formal": 0.02184, "sigma_bootstrap": 0.04232}
reduced chi^2 with the reported flux_err: 4.13
1-sigma coverage over 200 seeded datasets: {'t0_h': 0.36, 'depth': 0.335, 'T14_h': 0.275, 'T12_h': 0.22}
```

### [15] `cd labs/L300/15-honest-uncertainty && python solution/transit_fit.py`
run 2026-11-02 13:02 UTC, exit 0, 51 s
```
{"param": "t0_h", "true": 0.12, "fit": 0.15667, "sigma_formal": 0.01222, "sigma_bootstrap": 0.0128}
{"param": "depth", "true": 0.01, "fit": 0.00963, "sigma_formal": 0.00026, "sigma_bootstrap": 0.00026}
{"param": "T14_h", "true": 2.5, "fit": 2.41574, "sigma_formal": 0.05204, "sigma_bootstrap": 0.04615}
{"param": "T12_h", "true": 0.3, "fit": 0.19103, "sigma_formal": 0.0444, "sigma_bootstrap": 0.04232}
reduced chi^2 with the reported flux_err: 4.13
1-sigma coverage over 200 seeded datasets: {'t0_h': 0.73, 'depth': 0.615, 'T14_h': 0.555, 'T12_h': 0.56}
```

### [15] `cd labs/L300/15-honest-uncertainty && BUILD_TARGET=mine python -m unittest test_build_task`
run 2026-11-02 13:02 UTC, exit 1, 46 s
```
FF
======================================================================
FAIL: test_coverage_near_68_percent (test_build_task.TestHonestErrors.test_coverage_near_68_percent)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/15-honest-uncertainty/test_build_task.py", line 22, in test_coverage_near_68_percent
    self.assertTrue(0.60 <= cov[0] <= 0.78, cov)  # t0
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: np.False_ is not true : [0.36  0.335 0.275 0.22 ]

======================================================================
FAIL: test_formal_error_agrees_with_bootstrap (test_build_task.TestHonestErrors.test_formal_error_agrees_with_bootstrap)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/15-honest-uncertainty/test_build_task.py", line 30, in test_formal_error_agrees_with_bootstrap
    self.assertTrue(((ratio > 0.75) & (ratio < 1.33)).all(), ratio)
AssertionError: np.False_ is not true : [0.45460682 0.4750136 ]

----------------------------------------------------------------------
Ran 2 tests in 18.276s

FAILED (failures=2)
```

### [15] `cd labs/L300/15-honest-uncertainty && python -m unittest test_build_task -v`
run 2026-11-02 13:03 UTC, exit 0, 10 s
```

----------------------------------------------------------------------
Ran 2 tests in 5.833s

OK
```

### [15] `cd labs/L300/15-honest-uncertainty && python mcmc.py`
run 2026-11-02 13:03 UTC, exit 0, 16 s
```
{"param": "t0_h", "median": 0.15549, "minus": 0.01154, "plus": 0.01158}
{"param": "depth", "median": 0.00962, "minus": 0.00026, "plus": 0.00025}
{"param": "T14_h", "median": 2.36204, "minus": 0.08882, "plus": 0.07084}
{"param": "T12_h", "median": 0.15619, "minus": 0.06958, "plus": 0.05944}
{"param": "noise_scale_s", "median": 2.03536, "minus": 0.09109, "plus": 0.09312}
acceptance 0.270; autocorrelation time 35 steps; effective samples 430
```

### [15] `cd labs/L300/15-honest-uncertainty && python solution/report.py`
run 2026-11-02 13:04 UTC, exit 0, 18 s
```
{"param": "t0_h", "median": 0.15549, "plus": 0.01158, "minus": 0.01154, "gaussian": true}
{"param": "depth", "median": 0.00962, "plus": 0.00025, "minus": 0.00026, "gaussian": true}
{"param": "T14_h", "median": 2.36204, "plus": 0.07084, "minus": 0.08882, "gaussian": false}
{"param": "T12_h", "median": 0.15619, "plus": 0.05944, "minus": 0.06958, "gaussian": false}
```

### [15] `cd labs/L300/15-honest-uncertainty && python try_it.py`
run 2026-11-02 13:04 UTC, exit 0, 25 s
```
1. flux_err = true scatter: coverage {'t0_h': 0.73, 'depth': 0.625, 'T14_h': 0.545, 'T12_h': 0.56}
2. 1000 steps: acceptance 0.277, tau 25, chain/tau 32 (emcee docs: > ~50 is often enough), s = 2.024
```

### [16] `cd labs/L300/16-reproducible-pipelines && python pipeline.py`
run 2026-11-02 13:05 UTC, exit 0, 34 s
```
v1 input        : {'period_d': 0.43049, 'power': 0.5201}
v1 re-run       : {'period_d': 0.43049, 'power': 0.5201}
v2 (corrected)  : {'period_d': 0.43049, 'power': 0.5201}   <- true period 0.3011 d
{"activity": "detrend", "used": {"entity": "lightcurve.csv", "sha256": "4c4576852c83"}, "upstream_sha256": "2a2afa4414a8", "params": {"window_nights": 5}, "code_sha256": "6d5af32b5516", "generated_sha256": "d3c83e662e46", "cache": "miss"}
{"activity": "best_period", "used": {"entity": "lightcurve.csv", "sha256": "4c4576852c83"}, "upstream_sha256": "d3c83e662e46", "params": {}, "code_sha256": "eaac370b4f42", "generated_sha256": "dab630b559eb", "cache": "miss"}
{"activity": "detrend", "used": {"entity": "lightcurve.csv", "sha256": "4c4576852c83"}, "upstream_sha256": "2a2afa4414a8", "params": {"window_nights": 5}, "code_sha256": "6d5af32b5516", "generated_sha256": "d3c83e662e46", "cache": "hit"}
{"activity": "best_period", "used": {"entity": "lightcurve.csv", "sha256": "4c4576852c83"}, "upstream_sha256": "d3c83e662e46", "params": {}, "code_sha256": "eaac370b4f42", "generated_sha256": "dab630b559eb", "cache": "hit"}
{"activity": "detrend", "used": {"entity": "lightcurve.csv", "sha256": "6141395bece9"}, "upstream_sha256": "5a283c0d0f18", "params": {"window_nights": 5}, "code_sha256": "6d5af32b5516", "generated_sha256": "d3c83e662e46", "cache": "hit"}
{"activity": "best_period", "used": {"entity": "lightcurve.csv", "sha256": "6141395bece9"}, "upstream_sha256": "d3c83e662e46", "params": {}, "code_sha256": "eaac370b4f42", "generated_sha256": "dab630b559eb", "cache": "hit"}
```

### [16] `cd labs/L300/16-reproducible-pipelines && python solution/pipeline.py`
run 2026-11-02 13:06 UTC, exit 0, 44 s
```
v1 input        : {'period_d': 0.43049, 'power': 0.5201}
v1 re-run       : {'period_d': 0.43049, 'power': 0.5201}
v2 (corrected)  : {'period_d': 0.30112, 'power': 0.882}   <- true period 0.3011 d
{"activity": "detrend", "used": {"entity": "lightcurve.csv", "sha256": "4c4576852c83"}, "upstream_sha256": "2a2afa4414a8", "params": {"window_nights": 5}, "code_sha256": "6d5af32b5516", "generated_sha256": "d3c83e662e46", "cache": "miss"}
{"activity": "best_period", "used": {"entity": "lightcurve.csv", "sha256": "4c4576852c83"}, "upstream_sha256": "d3c83e662e46", "params": {}, "code_sha256": "eaac370b4f42", "generated_sha256": "dab630b559eb", "cache": "miss"}
{"activity": "detrend", "used": {"entity": "lightcurve.csv", "sha256": "4c4576852c83"}, "upstream_sha256": "2a2afa4414a8", "params": {"window_nights": 5}, "code_sha256": "6d5af32b5516", "generated_sha256": "d3c83e662e46", "cache": "hit"}
{"activity": "best_period", "used": {"entity": "lightcurve.csv", "sha256": "4c4576852c83"}, "upstream_sha256": "d3c83e662e46", "params": {}, "code_sha256": "eaac370b4f42", "generated_sha256": "dab630b559eb", "cache": "hit"}
{"activity": "detrend", "used": {"entity": "lightcurve.csv", "sha256": "6141395bece9"}, "upstream_sha256": "5a283c0d0f18", "params": {"window_nights": 5}, "code_sha256": "6d5af32b5516", "generated_sha256": "8dbcf371c9c4", "cache": "miss"}
{"activity": "best_period", "used": {"entity": "lightcurve.csv", "sha256": "6141395bece9"}, "upstream_sha256": "8dbcf371c9c4", "params": {}, "code_sha256": "eaac370b4f42", "generated_sha256": "85c5f7d18979", "cache": "miss"}
```

### [16] `cd labs/L300/16-reproducible-pipelines && BUILD_TARGET=mine python -m unittest test_build_task`
run 2026-11-02 13:07 UTC, exit 1, 40 s
```
FF.
======================================================================
FAIL: test_new_release_is_recomputed (test_build_task.TestContentAddressedCache.test_new_release_is_recomputed)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/16-reproducible-pipelines/test_build_task.py", line 30, in test_new_release_is_recomputed
    self.assertEqual(corrected["period_d"], 0.30112)
AssertionError: 0.43049 != 0.30112

======================================================================
FAIL: test_parameter_change_reaches_downstream_steps (test_build_task.TestContentAddressedCache.test_parameter_change_reaches_downstream_steps)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L300/16-reproducible-pipelines/test_build_task.py", line 44, in test_parameter_change_reaches_downstream_steps
    self.assertEqual(caches(tmp), ["miss", "miss", "miss", "miss"])
AssertionError: Lists differ: ['miss', 'miss', 'miss', 'hit'] != ['miss', 'miss', 'miss', 'miss']

First differing element 3:
'hit'
'miss'

- ['miss', 'miss', 'miss', 'hit']
?                           ^ ^

+ ['miss', 'miss', 'miss', 'miss']
?                           ^ ^^


----------------------------------------------------------------------
Ran 3 tests in 38.499s

FAILED (failures=2)
```

### [16] `cd labs/L300/16-reproducible-pipelines && python -m unittest test_build_task -v`
run 2026-11-02 13:07 UTC, exit 0, 92 s
```

----------------------------------------------------------------------
Ran 3 tests in 77.841s

OK
```

### [16] `cd labs/L300/16-reproducible-pipelines && python try_it.py`
run 2026-11-02 13:09 UTC, exit 0, 23 s
```
1. shipped: window 5 -> {'period_d': 0.30112, 'power': 0.882}; window 1 -> {'period_d': 0.30112, 'power': 0.882}; cache ['miss', 'miss', 'miss', 'hit']
2. fixed, FREQ changed: before {'period_d': 0.30112, 'power': 0.882}; after {'period_d': 0.30112, 'power': 0.882}; cache ['miss', 'miss', 'hit', 'hit']
```

### [16] `cd labs/L300/16-reproducible-pipelines && python solution/lineage.py`
run 2026-11-02 13:09 UTC, exit 0, 33 s
```
{"activity": "best_period", "params": {}, "code_sha256": "eaac370b4f42", "input_file_sha256": "6141395bece9"}
{"activity": "detrend", "params": {"window_nights": 5}, "code_sha256": "6d5af32b5516", "input_file_sha256": "6141395bece9"}
```

### [16] `cd labs/L300/16-reproducible-pipelines && python -m unittest -v`
run 2026-11-02 13:10 UTC, exit 0, 117 s
```
test_joblib_path_key_is_stale_data_key_is_not (test_pipeline.TestJoblibEquivalent.test_joblib_path_key_is_stale_data_key_is_not) ... skipped 'joblib not installed (pending-ci)'

----------------------------------------------------------------------
Ran 9 tests in 99.782s

OK (skipped=1)
```

### [09] `cd labs/L200/09-aperture-photometry && BUILD_TARGET=mine python -m unittest test_build_task -v`
run 2026-11-02 13:14 UTC, exit 1, 14 s
```
test_non_detection_is_nan_not_a_crash (test_build_task.TestCalibrate.test_non_detection_is_nan_not_a_crash) ... ERROR
test_reference_star_gets_its_catalogue_magnitude (test_build_task.TestCalibrate.test_reference_star_gets_its_catalogue_magnitude) ... ERROR
test_ten_times_fainter_is_2_5_mag_and_error_from_snr (test_build_task.TestCalibrate.test_ten_times_fainter_is_2_5_mag_and_error_from_snr) ... ERROR

======================================================================
ERROR: test_non_detection_is_nan_not_a_crash (test_build_task.TestCalibrate.test_non_detection_is_nan_not_a_crash)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L200/09-aperture-photometry/test_build_task.py", line 32, in test_non_detection_is_nan_not_a_crash
    mag, _ = target.calibrate(RESULTS, 0, 10.0)[2]
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/workspace/working/kb/astronomy/labs/L200/09-aperture-photometry/photometry.py", line 48, in calibrate
    raise NotImplementedError("build task: zero point from the reference star, calibrated magnitudes and errors")
NotImplementedError: build task: zero point from the reference star, calibrated magnitudes and errors

======================================================================
ERROR: test_reference_star_gets_its_catalogue_magnitude (test_build_task.TestCalibrate.test_reference_star_gets_its_catalogue_magnitude)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L200/09-aperture-photometry/test_build_task.py", line 24, in test_reference_star_gets_its_catalogue_magnitude
    self.assertAlmostEqual(target.calibrate(RESULTS, 0, 10.0)[0][0], 10.0, places=12)
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/workspace/working/kb/astronomy/labs/L200/09-aperture-photometry/photometry.py", line 48, in calibrate
    raise NotImplementedError("build task: zero point from the reference star, calibrated magnitudes and errors")
NotImplementedError: build task: zero point from the reference star, calibrated magnitudes and errors

======================================================================
ERROR: test_ten_times_fainter_is_2_5_mag_and_error_from_snr (test_build_task.TestCalibrate.test_ten_times_fainter_is_2_5_mag_and_error_from_snr)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L200/09-aperture-photometry/test_build_task.py", line 27, in test_ten_times_fainter_is_2_5_mag_and_error_from_snr
    mag, err = target.calibrate(RESULTS, 0, 10.0)[1]
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/workspace/working/kb/astronomy/labs/L200/09-aperture-photometry/photometry.py", line 48, in calibrate
    raise NotImplementedError("build task: zero point from the reference star, calibrated magnitudes and errors")
NotImplementedError: build task: zero point from the reference star, calibrated magnitudes and errors

----------------------------------------------------------------------
Ran 3 tests in 0.488s

FAILED (errors=3)
```

### [09] `cd labs/L200/09-aperture-photometry && python try_it.py`
run 2026-11-02 13:14 UTC, exit 0, 6 s
```
r=2.0: star0 SNR   99.6   star3 SNR  10.4
r=3.0: star0 SNR  118.3   star3 SNR  11.2
r=4.0: star0 SNR  118.5   star3 SNR   9.7
r=6.0: star0 SNR  102.6   star3 SNR   6.0
r=9.0: star0 SNR   74.1   star3 SNR   2.3
median sky 102.29 -> net 19877.2 e- | mean sky 118.43 -> net 18059.1 e- (true 20000)
```

### [10] `cd labs/L200/10-light-curves && BUILD_TARGET=mine python -m unittest test_build_task -v`
run 2026-11-02 13:15 UTC, exit 1, 3 s
```
test_pure_noise_is_not_significant (test_build_task.TestBootstrapFap.test_pure_noise_is_not_significant) ... ERROR
test_real_signal_has_tiny_fap (test_build_task.TestBootstrapFap.test_real_signal_has_tiny_fap) ... ERROR
test_reproducible_with_seed (test_build_task.TestBootstrapFap.test_reproducible_with_seed) ... ERROR

======================================================================
ERROR: test_pure_noise_is_not_significant (test_build_task.TestBootstrapFap.test_pure_noise_is_not_significant)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L200/10-light-curves/test_build_task.py", line 32, in test_pure_noise_is_not_significant
    self.assertGreater(target.bootstrap_fap(self.t, noise, self.f, n=30), 0.05)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/workspace/working/kb/astronomy/labs/L200/10-light-curves/periods.py", line 53, in bootstrap_fap
    raise NotImplementedError("build task: false-alarm probability by shuffling the magnitudes")
NotImplementedError: build task: false-alarm probability by shuffling the magnitudes

======================================================================
ERROR: test_real_signal_has_tiny_fap (test_build_task.TestBootstrapFap.test_real_signal_has_tiny_fap)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L200/10-light-curves/test_build_task.py", line 28, in test_real_signal_has_tiny_fap
    self.assertLessEqual(target.bootstrap_fap(self.t, target.variable_star(self.t), self.f, n=30), 1 / 31 + 1e-12)
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/workspace/working/kb/astronomy/labs/L200/10-light-curves/periods.py", line 53, in bootstrap_fap
    raise NotImplementedError("build task: false-alarm probability by shuffling the magnitudes")
NotImplementedError: build task: false-alarm probability by shuffling the magnitudes

======================================================================
ERROR: test_reproducible_with_seed (test_build_task.TestBootstrapFap.test_reproducible_with_seed)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L200/10-light-curves/test_build_task.py", line 36, in test_reproducible_with_seed
    self.assertEqual(target.bootstrap_fap(self.t, y, self.f, n=20, seed=1),
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/workspace/working/kb/astronomy/labs/L200/10-light-curves/periods.py", line 53, in bootstrap_fap
    raise NotImplementedError("build task: false-alarm probability by shuffling the magnitudes")
NotImplementedError: build task: false-alarm probability by shuffling the magnitudes

----------------------------------------------------------------------
Ran 3 tests in 0.266s

FAILED (errors=3)
```

### [02] `cd labs/L100/02-coordinates && python try_it.py`
run 2026-11-02 13:15 UTC, exit 0, 1 s
```
15:30 UTC up: Deneb, Altair, Vega, Fomalhaut, Polaris, Capella
18:30 UTC up: Capella, Betelgeuse, Polaris, Deneb, Fomalhaut, Sirius, Vega
Canopus from Gurgaon: alt -33.23 deg az 136.60 deg
Canopus from Sydney: alt  59.20 deg az 138.16 deg
```

### [13] `cd labs/L300/13-ccd-calibration && python calibrate.py`
run 2026-11-02 13:15 UTC, exit 0, 22 s
```
relative flux, every 5th frame: 0.9971 1.0070 1.0082 1.0031 1.0043 0.9881
{"rms_percent": 0.88, "robust_rms_percent": 0.899, "expected_noise_percent": 0.224, "variable": true}
master_flat min/max: 0.8527 1.0792 (true response 0.75/1.00)
```

### [13] `cd labs/L300/13-ccd-calibration && python /mnt/workspace/.copilot-state/1e67a17a-e6e7-4b32-b095-e8f8e0f4a9bd/session-state/host/files/astro_explain/cosmics.py`
run 2026-11-02 13:16 UTC, exit 0, 2 s
```
cosmics_cleaned per frame: [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
```

### [17] `cd labs/L400/17-survey-pipeline && python survey.py`
run 2026-11-02 13:17 UTC, exit 0, 39 s
```
{"option": "A", "frames_per_s": 272.7, "detections": 172, "completeness": 0.1745, "purity": 1.0, "catalogue_sha": "cb7b9698de2d"}
{"option": "B", "frames_per_s": 3.9, "detections": 172, "completeness": 0.1745, "purity": 1.0, "catalogue_sha": "cb7b9698de2d"}
{"option": "C", "frames_per_s": 244.2, "detections": 172, "completeness": 0.1745, "purity": 1.0, "catalogue_sha": "cb7b9698de2d"}
```

### [17] `cd labs/L400/17-survey-pipeline && head -3 pipeline_metrics.jsonl`
run 2026-11-02 13:17 UTC, exit 0, 3 s
```
{"option": "A", "unit": 0, "frames": 1, "ingest_s": 6e-05, "calibrate_s": 0.0001, "detect_s": 0.0596}
{"option": "A", "unit": 1, "frames": 1, "ingest_s": 5e-05, "calibrate_s": 5e-05, "detect_s": 0.03462}
{"option": "A", "unit": 2, "frames": 1, "ingest_s": 0.00014, "calibrate_s": 5e-05, "detect_s": 0.00866}
```

### [17] `cd labs/L400/17-survey-pipeline && python solution/survey.py`
run 2026-11-02 13:18 UTC, exit 0, 40 s
```
{"option": "A", "frames_per_s": 231.1, "detections": 1808, "completeness": 0.9729, "purity": 0.984, "catalogue_sha": "b51fb7f42583"}
{"option": "B", "frames_per_s": 1.9, "detections": 1808, "completeness": 0.9729, "purity": 0.984, "catalogue_sha": "b51fb7f42583"}
{"option": "C", "frames_per_s": 117.4, "detections": 1808, "completeness": 0.9729, "purity": 0.984, "catalogue_sha": "b51fb7f42583"}
```

### [17] `cd labs/L400/17-survey-pipeline && BUILD_TARGET=mine python -m unittest test_build_task test_fitness`
run 2026-11-02 13:18 UTC, exit 1, 73 s
```
FFF..
======================================================================
FAIL: test_background_error_below_two_percent_of_sky (test_build_task.TestMeshBackground.test_background_error_below_two_percent_of_sky)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/17-survey-pipeline/test_build_task.py", line 28, in test_background_error_below_two_percent_of_sky
    self.assertLess(float(np.percentile(err, 99)), 0.02)
AssertionError: 0.9687442122207449 not less than 0.02

======================================================================
FAIL: test_completeness_on_the_night (test_build_task.TestMeshBackground.test_completeness_on_the_night)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/17-survey-pipeline/test_build_task.py", line 33, in test_completeness_on_the_night
    self.assertGreaterEqual(target.score(rows, truth)[0], 0.95)
AssertionError: 0.1745 not greater than or equal to 0.95

======================================================================
FAIL: test_detection_quality (test_fitness.TestSurveyFitness.test_detection_quality)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/17-survey-pipeline/test_fitness.py", line 30, in test_detection_quality
    self.assertGreaterEqual(comp, 0.95)
AssertionError: 0.1745 not greater than or equal to 0.95

----------------------------------------------------------------------
Ran 5 tests in 47.363s

FAILED (failures=3)
```

### [17] `cd labs/L400/17-survey-pipeline && python -m unittest test_build_task test_fitness -v`
run 2026-11-02 13:19 UTC, exit 0, 35 s
```

----------------------------------------------------------------------
Ran 5 tests in 21.801s

OK
```

### [17] `cd labs/L400/17-survey-pipeline && python try_it.py`
run 2026-11-02 13:20 UTC, exit 0, 31 s
```
1. 3 sigma, 32 px mesh: 2597 detections, completeness 0.9739, purity 0.7624
2. 5 sigma, 64 px mesh: 1799 detections, completeness 0.9729, purity 0.98
```

### [18] `cd labs/L400/18-alert-broker && python alerts.py`
run 2026-11-02 13:21 UTC, exit 0, 9 s
```
{"option": "A", "alerts_per_night": 192.4, "real_fraction": 0.027, "classes": {"bogus": 944, "moving": 155, "transient": 440}, "schema_errors": 0}
{"option": "B", "alerts_per_night": 74.4, "real_fraction": 0.045, "classes": {"moving": 155, "transient": 440}, "schema_errors": 0}
{"option": "C", "alerts_per_night": 58.2, "real_fraction": 0.045, "classes": {"moving": 155, "transient": 311}, "schema_errors": 0}
option C, night 7: 70 alerts; first 5:
{"night": 7, "exposure": "a", "objectId": "AKB034006", "class": "transient", "flux": 247.3, "n_prv": 5}
{"night": 7, "exposure": "a", "objectId": "AKB036007", "class": "transient", "flux": -980.9, "n_prv": 5}
{"night": 7, "exposure": "a", "objectId": "AKB033008", "class": "transient", "flux": 869.2, "n_prv": 1}
{"night": 7, "exposure": "a", "objectId": "AKB036009", "class": "transient", "flux": -659.9, "n_prv": 2}
{"night": 7, "exposure": "a", "objectId": "AKB015016", "class": "moving", "flux": 122.9, "n_prv": 1}
```

### [18] `cd labs/L400/18-alert-broker && python solution/alerts.py`
run 2026-11-02 13:21 UTC, exit 0, 10 s
```
{"option": "A", "alerts_per_night": 9.8, "real_fraction": 0.462, "classes": {"bogus": 44, "known_variable": 3, "moving": 18, "transient": 13}, "schema_errors": 0}
{"option": "B", "alerts_per_night": 4.2, "real_fraction": 0.882, "classes": {"known_variable": 3, "moving": 18, "transient": 13}, "schema_errors": 0}
{"option": "C", "alerts_per_night": 3.5, "real_fraction": 0.857, "classes": {"known_variable": 2, "moving": 18, "transient": 8}, "schema_errors": 0}
option C, night 7: 4 alerts; first 5:
{"night": 7, "exposure": "a", "objectId": "AKB034041", "class": "transient", "flux": 110.4, "n_prv": 0}
{"night": 7, "exposure": "a", "objectId": "AKB049044", "class": "moving", "flux": 4137.9, "n_prv": 0}
{"night": 7, "exposure": "a", "objectId": "AKB020045", "class": "transient", "flux": 15141.0, "n_prv": 4}
{"night": 7, "exposure": "b", "objectId": "AKB050044", "class": "moving", "flux": 4601.3, "n_prv": 0}
```

### [18] `cd labs/L400/18-alert-broker && python agent_assist.py`
run 2026-11-02 13:21 UTC, exit 0, 34 s
```
{"candid": 23, "code_class": "known_variable", "class_ok": false, "unverified": ["2.5"], "publish": false}
{"candid": 33, "code_class": "moving", "class_ok": true, "unverified": ["2.5"], "publish": false}
{"candid": 32, "code_class": "transient", "class_ok": true, "unverified": ["2.5"], "publish": false}
```

### [18] `cd labs/L400/18-alert-broker && BUILD_TARGET=mine python -m unittest test_build_task test_fitness`
run 2026-11-02 13:22 UTC, exit 1, 35 s
```
F.F...
======================================================================
FAIL: test_constant_stars_vanish (test_build_task.TestMatchedDifference.test_constant_stars_vanish)
Same stars, worse seeing and 20% less transparency, no noise: the difference must be ~0.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/18-alert-broker/test_build_task.py", line 31, in test_constant_stars_vanish
    self.assertLess(float(np.abs(resid).max()), 0.02 * float(np.abs(new - sim.SKY).max()))
AssertionError: 1965.0921745653166 not less than 20.113176951249866

======================================================================
FAIL: test_alert_volume_and_purity (test_fitness.TestBrokerFitness.test_alert_volume_and_purity)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/18-alert-broker/test_fitness.py", line 35, in test_alert_volume_and_purity
    self.assertLessEqual(self.summary["alerts_per_night"], 6)
AssertionError: 58.2 not less than or equal to 6

----------------------------------------------------------------------
Ran 6 tests in 8.356s

FAILED (failures=2)
```

### [18] `cd labs/L400/18-alert-broker && python -m unittest test_build_task test_fitness -v`
run 2026-11-02 13:22 UTC, exit 0, 8 s
```
test_constant_stars_vanish (test_build_task.TestMatchedDifference.test_constant_stars_vanish)

----------------------------------------------------------------------
Ran 6 tests in 4.723s

OK
```

### [18] `cd labs/L400/18-alert-broker && python try_it.py`
run 2026-11-02 13:23 UTC, exit 0, 7 s
```
1. PSF matched, flux not, option A: 43.8 alerts/night, classes {'bogus': 320, 'known_variable': 2, 'moving': 18, 'transient': 10}
1. PSF matched, flux not, option C: 3.0 alerts/night, classes {'known_variable': 1, 'moving': 18, 'transient': 5}
2. no known-variable catalogue: V1 alerts classified as ['transient', 'transient']
```

### [19] `cd labs/L400/19-big-catalogues && python catalog.py`
run 2026-11-02 13:24 UTC, exit 0, 12 s
```
{"option": "A brute force", "build_s": 0.64, "ms_per_query": 12.3663, "wrong_cones": 0, "sources_found": 16738, "tested_per_query": 1000000}
{"option": "B zones h=0.1", "build_s": 0.94, "ms_per_query": 0.2379, "wrong_cones": 374, "sources_found": 12765, "tested_per_query": 27}
{"option": "C zones h=1.0", "build_s": 0.87, "ms_per_query": 0.0716, "wrong_cones": 374, "sources_found": 12765, "tested_per_query": 43}
SELECT source_id, ra, dec FROM gaiadr3.gaia_source WHERE 1 = CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', 83.82, -5.39, 0.05))
```

### [19] `cd labs/L400/19-big-catalogues && python solution/catalog.py`
run 2026-11-02 13:24 UTC, exit 0, 20 s
```
{"option": "A brute force", "build_s": 0.3, "ms_per_query": 12.4148, "wrong_cones": 0, "sources_found": 16738, "tested_per_query": 1000000}
{"option": "B zones h=0.1", "build_s": 0.74, "ms_per_query": 0.3439, "wrong_cones": 0, "sources_found": 16738, "tested_per_query": 39}
{"option": "C zones h=1.0", "build_s": 0.75, "ms_per_query": 0.0765, "wrong_cones": 0, "sources_found": 16738, "tested_per_query": 62}
SELECT source_id, ra, dec FROM gaiadr3.gaia_source WHERE 1 = CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', 83.82, -5.39, 0.05))
```

### [19] `cd labs/L400/19-big-catalogues && BUILD_TARGET=mine python -m unittest test_build_task test_fitness`
run 2026-11-02 13:24 UTC, exit 1, 26 s
```
FFFFFFF.F.
======================================================================
FAIL: test_high_declination_and_poles (test_build_task.TestExactConeSearch.test_high_declination_and_poles) (cone=(10.0, 75.0, 1.0))
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/19-big-catalogues/test_build_task.py", line 30, in check
    np.testing.assert_array_equal(self.zones.query(*c), self.brute.query(*c))
  File "/opt/venv/lib/python3.12/site-packages/numpy/testing/_private/utils.py", line 1128, in assert_array_equal
    assert_array_compare(operator.__eq__, actual, desired, err_msg=err_msg,
  File "/opt/venv/lib/python3.12/site-packages/numpy/testing/_private/utils.py", line 847, in assert_array_compare
    raise AssertionError(msg)
AssertionError: 
Arrays are not equal

(shapes (4,), (18,) mismatch)
 ACTUAL: array([ 43338,  49643,  93001, 127083])
 DESIRED: array([  9811,  13168,  24592,  43338,  49643,  88124,  91691,  93001,
       103484, 126363, 127083, 139748, 157248, 157795, 180940, 184594,
       198220, 198680])

======================================================================
FAIL: test_high_declination_and_poles (test_build_task.TestExactConeSearch.test_high_declination_and_poles) (cone=(200.0, -88.0, 0.8))
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/19-big-catalogues/test_build_task.py", line 30, in check
    np.testing.assert_array_equal(self.zones.query(*c), self.brute.query(*c))
  File "/opt/venv/lib/python3.12/site-packages/numpy/testing/_private/utils.py", line 1128, in assert_array_equal
    assert_array_compare(operator.__eq__, actual, desired, err_msg=err_msg,
  File "/opt/venv/lib/python3.12/site-packages/numpy/testing/_private/utils.py", line 847, in assert_array_compare
    raise AssertionError(msg)
AssertionError: 
Arrays are not equal

(shapes (0,), (10,) mismatch)
 ACTUAL: array([], dtype=int64)
 DESIRED: array([  8232,  30478,  73280,  73454,  91766, 112354, 144215, 163602,
       169074, 189668])

======================================================================
FAIL: test_high_declination_and_poles (test_build_task.TestExactConeSearch.test_high_declination_and_poles) (cone=(33.0, 89.6, 0.5))
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/19-big-catalogues/test_build_task.py", line 30, in check
    np.testing.assert_array_equal(self.zones.query(*c), self.brute.query(*c))
  File "/opt/venv/lib/python3.12/site-packages/numpy/testing/_private/utils.py", line 1128, in assert_array_equal
    assert_array_compare(operator.__eq__, actual, desired, err_msg=err_msg,
  File "/opt/venv/lib/python3.12/site-packages/numpy/testing/_private/utils.py", line 847, in assert_array_compare
    raise AssertionError(msg)
AssertionError: 
Arrays are not equal

(shapes (0,), (6,) mismatch)
 ACTUAL: array([], dtype=int64)
 DESIRED: array([ 48262,  58908, 113024, 124739, 152723, 182376])

======================================================================
FAIL: test_high_declination_and_poles (test_build_task.TestExactConeSearch.test_high_declination_and_poles) (cone=(300.0, -60.0, 2.0))
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/19-big-catalogues/test_build_task.py", line 30, in check
    np.testing.assert_array_equal(self.zones.query(*c), self.brute.query(*c))
  File "/opt/venv/lib/python3.12/site-packages/numpy/testing/_private/utils.py", line 1128, in assert_array_equal
    assert_array_compare(operator.__eq__, actual, desired, err_msg=err_msg,
  File "/opt/venv/lib/python3.12/site-packages/numpy/testing/_private/utils.py", line 847, in assert_array_compare
    raise AssertionError(msg)
AssertionError: 
Arrays are not equal

(shapes (32,), (56,) mismatch)
 ACTUAL: array([   340,   5001,  16389,  18880,  20991,  28854,  32925,  46860,
        67858,  70366,  75326,  84300,  95892, 101303, 103910, 104244,
       105756, 108454, 108483, 114967, 122467, 124399, 125310, 128357,
       155303, 157811, 158286, 160905, 176092, 182920, 185466, 198779])
 DESIRED: array([   340,   1933,   4543,   5001,  11870,  14154,  14168,  16389,
        18037,  18880,  20991,  28854,  31208,  32821,  32925,  34074,
        37962,  39246,  46860,  67858,  70366,  75326,  84300,  92580,...

======================================================================
FAIL: test_ra_wrap (test_build_task.TestExactConeSearch.test_ra_wrap) (cone=(0.1, 5.0, 0.6))
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/19-big-catalogues/test_build_task.py", line 30, in check
    np.testing.assert_array_equal(self.zones.query(*c), self.brute.query(*c))
  File "/opt/venv/lib/python3.12/site-packages/numpy/testing/_private/utils.py", line 1128, in assert_array_equal
    assert_array_compare(operator.__eq__, actual, desired, err_msg=err_msg,
  File "/opt/venv/lib/python3.12/site-packages/numpy/testing/_private/utils.py", line 847, in assert_array_compare
    raise AssertionError(msg)
AssertionError: 
Arrays are not equal

(shapes (2,), (4,) mismatch)
 ACTUAL: array([ 35689, 180563])
 DESIRED: array([ 35689,  73237, 110706, 180563])

======================================================================
FAIL: test_ra_wrap (test_build_task.TestExactConeSearch.test_ra_wrap) (cone=(359.9, -20.0, 0.6))
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/19-big-catalogues/test_build_task.py", line 30, in check
    np.testing.assert_array_equal(self.zones.query(*c), self.brute.query(*c))
  File "/opt/venv/lib/python3.12/site-packages/numpy/testing/_private/utils.py", line 1128, in assert_array_equal
    assert_array_compare(operator.__eq__, actual, desired, err_msg=err_msg,
  File "/opt/venv/lib/python3.12/site-packages/numpy/testing/_private/utils.py", line 847, in assert_array_compare
    raise AssertionError(msg)
AssertionError: 
Arrays are not equal

(shapes (2,), (4,) mismatch)
 ACTUAL: array([152749, 187512])
 DESIRED: array([137323, 152749, 166804, 187512])

======================================================================
FAIL: test_ra_wrap (test_build_task.TestExactConeSearch.test_ra_wrap) (cone=(0.0, 45.0, 1.0))
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/19-big-catalogues/test_build_task.py", line 30, in check
    np.testing.assert_array_equal(self.zones.query(*c), self.brute.query(*c))
  File "/opt/venv/lib/python3.12/site-packages/numpy/testing/_private/utils.py", line 1128, in assert_array_equal
    assert_array_compare(operator.__eq__, actual, desired, err_msg=err_msg,
  File "/opt/venv/lib/python3.12/site-packages/numpy/testing/_private/utils.py", line 847, in assert_array_compare
    raise AssertionError(msg)
AssertionError: 
Arrays are not equal

(shapes (6,), (13,) mismatch)
 ACTUAL: array([  5272,  22937, 167405, 182484, 183080, 189177])
 DESIRED: array([  5272,  11730,  12209,  12546,  22937,  69179,  91964, 112332,
       167405, 182484, 183080, 188453, 189177])

======================================================================
FAIL: test_exact_on_every_cone (test_fitness.TestCatalogueFitness.test_exact_on_every_cone)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/19-big-catalogues/test_fitness.py", line 32, in test_exact_on_every_cone
    self.assertEqual(target.measure(self.index, self.cones, self.ref)[2], 0)
AssertionError: 374 != 0

----------------------------------------------------------------------
Ran 5 tests in 18.652s

FAILED (failures=8)
```

### [19] `cd labs/L400/19-big-catalogues && python -m unittest test_build_task test_fitness -v`
run 2026-11-02 13:25 UTC, exit 0, 13 s
```

----------------------------------------------------------------------
Ran 5 tests in 10.769s

OK
```

### [19] `cd labs/L400/19-big-catalogues && python try_it.py`
run 2026-11-02 13:25 UTC, exit 0, 10 s
```
1. zones h=0.01: 2.006 ms/query (brute 14.88), wrong cones 0
1. zones h=1.0: 0.042 ms/query (brute 14.88), wrong cones 0
2. radius 5 deg: brute 6.69 ms, zones h=1.0 0.95 ms -> 7x, wrong 0
```

### [20] `cd labs/L400/20-model-comparison && python compare.py`
run 2026-11-02 13:30 UTC, exit 0, 44 s
```
{"model": "disk only", "k": 1, "chi2": 3267.95, "bic": 3271.64, "aic": 3269.95, "runs_z": -6.05, "params": [2.118]}
{"model": "disk + cored halo", "k": 3, "chi2": 43.24, "bic": 54.3, "aic": 49.24, "runs_z": -1.27, "params": [1.087, 2.109, 4.57]}
{"model": "disk + NFW halo", "k": 3, "chi2": 67.83, "bic": 78.9, "aic": 73.83, "runs_z": -1.27, "params": [0.801, 120.916, 8.884]}
{"model": "disk + halo + wiggles", "k": 6, "chi2": 40.63, "bic": 62.76, "aic": 52.63, "runs_z": 0.64, "params": [0.421, 16.35, 1.715, -6.637, 5.243, -2.308]}
select() picks: disk + halo + wiggles
{"option": "A chi2", "picks_over_50_datasets": {"disk + halo + wiggles": 50}}
{"option": "B BIC", "picks_over_50_datasets": {"disk + cored halo": 50}}
{"option": "C holdout R>20", "picks_over_50_datasets": {"disk + NFW halo": 5, "disk + cored halo": 43, "disk + halo + wiggles": 2}}
```

### [20] `cd labs/L400/20-model-comparison && python solution/compare.py`
run 2026-11-02 13:31 UTC, exit 0, 33 s
```
{"model": "disk only", "k": 1, "chi2": 3267.95, "bic": 3271.64, "aic": 3269.95, "runs_z": -6.05, "params": [2.118]}
{"model": "disk + cored halo", "k": 3, "chi2": 43.24, "bic": 54.3, "aic": 49.24, "runs_z": -1.27, "params": [1.087, 2.109, 4.57]}
{"model": "disk + NFW halo", "k": 3, "chi2": 67.83, "bic": 78.9, "aic": 73.83, "runs_z": -1.27, "params": [0.801, 120.916, 8.884]}
{"model": "disk + halo + wiggles", "k": 6, "chi2": 40.63, "bic": 62.76, "aic": 52.63, "runs_z": 0.64, "params": [0.421, 16.35, 1.715, -6.637, 5.243, -2.308]}
select() picks: disk + cored halo
{"option": "A chi2", "picks_over_50_datasets": {"disk + halo + wiggles": 50}}
{"option": "B BIC", "picks_over_50_datasets": {"disk + cored halo": 50}}
{"option": "C holdout R>20", "picks_over_50_datasets": {"disk + NFW halo": 5, "disk + cored halo": 43, "disk + halo + wiggles": 2}}
```

### [20] `cd labs/L400/20-model-comparison && BUILD_TARGET=mine python -m unittest test_build_task test_fitness`
run 2026-11-02 13:32 UTC, exit 1, 55 s
```
FFFFFFFFFFF.F
======================================================================
FAIL: test_published_curve (test_build_task.TestPenalisedSelection.test_published_curve)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/20-model-comparison/test_build_task.py", line 24, in test_published_curve
    self.assertEqual(target.select(g.R, v, err)[0], "disk + cored halo")
AssertionError: 'disk + halo + wiggles' != 'disk + cored halo'
- disk + halo + wiggles
+ disk + cored halo


======================================================================
FAIL: test_ten_more_galaxies (test_build_task.TestPenalisedSelection.test_ten_more_galaxies) (seed=30)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/20-model-comparison/test_build_task.py", line 30, in test_ten_more_galaxies
    self.assertNotEqual(target.select(g.R, v, err)[0], "disk + halo + wiggles")
AssertionError: 'disk + halo + wiggles' == 'disk + halo + wiggles'

======================================================================
FAIL: test_ten_more_galaxies (test_build_task.TestPenalisedSelection.test_ten_more_galaxies) (seed=31)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/20-model-comparison/test_build_task.py", line 30, in test_ten_more_galaxies
    self.assertNotEqual(target.select(g.R, v, err)[0], "disk + halo + wiggles")
AssertionError: 'disk + halo + wiggles' == 'disk + halo + wiggles'

======================================================================
FAIL: test_ten_more_galaxies (test_build_task.TestPenalisedSelection.test_ten_more_galaxies) (seed=32)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/20-model-comparison/test_build_task.py", line 30, in test_ten_more_galaxies
    self.assertNotEqual(target.select(g.R, v, err)[0], "disk + halo + wiggles")
AssertionError: 'disk + halo + wiggles' == 'disk + halo + wiggles'

======================================================================
FAIL: test_ten_more_galaxies (test_build_task.TestPenalisedSelection.test_ten_more_galaxies) (seed=33)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/20-model-comparison/test_build_task.py", line 30, in test_ten_more_galaxies
    self.assertNotEqual(target.select(g.R, v, err)[0], "disk + halo + wiggles")
AssertionError: 'disk + halo + wiggles' == 'disk + halo + wiggles'

======================================================================
FAIL: test_ten_more_galaxies (test_build_task.TestPenalisedSelection.test_ten_more_galaxies) (seed=34)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/20-model-comparison/test_build_task.py", line 30, in test_ten_more_galaxies
    self.assertNotEqual(target.select(g.R, v, err)[0], "disk + halo + wiggles")
AssertionError: 'disk + halo + wiggles' == 'disk + halo + wiggles'

======================================================================
FAIL: test_ten_more_galaxies (test_build_task.TestPenalisedSelection.test_ten_more_galaxies) (seed=35)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/20-model-comparison/test_build_task.py", line 30, in test_ten_more_galaxies
    self.assertNotEqual(target.select(g.R, v, err)[0], "disk + halo + wiggles")
AssertionError: 'disk + halo + wiggles' == 'disk + halo + wiggles'

======================================================================
FAIL: test_ten_more_galaxies (test_build_task.TestPenalisedSelection.test_ten_more_galaxies) (seed=36)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/20-model-comparison/test_build_task.py", line 30, in test_ten_more_galaxies
    self.assertNotEqual(target.select(g.R, v, err)[0], "disk + halo + wiggles")
AssertionError: 'disk + halo + wiggles' == 'disk + halo + wiggles'

======================================================================
FAIL: test_ten_more_galaxies (test_build_task.TestPenalisedSelection.test_ten_more_galaxies) (seed=37)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/20-model-comparison/test_build_task.py", line 30, in test_ten_more_galaxies
    self.assertNotEqual(target.select(g.R, v, err)[0], "disk + halo + wiggles")
AssertionError: 'disk + halo + wiggles' == 'disk + halo + wiggles'

======================================================================
FAIL: test_ten_more_galaxies (test_build_task.TestPenalisedSelection.test_ten_more_galaxies) (seed=38)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/20-model-comparison/test_build_task.py", line 30, in test_ten_more_galaxies
    self.assertNotEqual(target.select(g.R, v, err)[0], "disk + halo + wiggles")
AssertionError: 'disk + halo + wiggles' == 'disk + halo + wiggles'

======================================================================
FAIL: test_ten_more_galaxies (test_build_task.TestPenalisedSelection.test_ten_more_galaxies) (seed=39)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/20-model-comparison/test_build_task.py", line 30, in test_ten_more_galaxies
    self.assertNotEqual(target.select(g.R, v, err)[0], "disk + halo + wiggles")
AssertionError: 'disk + halo + wiggles' == 'disk + halo + wiggles'

======================================================================
FAIL: test_selection_rate (test_fitness.TestSelectionFitness.test_selection_rate)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/20-model-comparison/test_fitness.py", line 26, in test_selection_rate
    self.assertGreaterEqual(halo / len(picks), 0.95)
AssertionError: 0.0 not greater than or equal to 0.95

----------------------------------------------------------------------
Ran 4 tests in 44.654s

FAILED (failures=12)
```

### [20] `cd labs/L400/20-model-comparison && python -m unittest test_build_task test_fitness -v`
run 2026-11-02 13:33 UTC, exit 0, 29 s
```

----------------------------------------------------------------------
Ran 4 tests in 22.418s

OK
```

### [20] `cd labs/L400/20-model-comparison && python try_it.py`
run 2026-11-02 13:33 UTC, exit 0, 6 s
```
1. NFW truth -> BIC picks disk + NFW halo {'disk only': 4281.27, 'disk + cored halo': 74.95, 'disk + NFW halo': 47.84, 'disk + halo + wiggles': 64.97}
2. R <= 8 kpc -> disk + cored halo {'disk only': (92.21, 1.504), 'disk + cored halo': (12.5, 1.19)} (bic, mass-to-light)
```

### [21] `cd labs/L400/21-open-data-practice && python release.py`
run 2026-11-02 13:34 UTC, exit 0, 15 s
```
release licence: CC-BY-4.0
{
 "files": [
  "ACKNOWLEDGEMENTS.md",
  "CITATION.cff",
  "LICENSE.txt",
  "MANIFEST.json",
  "catalogue.vot",
  "metadata.json"
 ],
 "problems": [
  "licence: release CC-BY-4.0 drops the NC condition of input gaia_dr3_astrometry (LicenseRef-CC-BY-NC-3.0-IGO)"
 ]
}
```

### [21] `cd labs/L400/21-open-data-practice && python solution/release.py`
run 2026-11-02 13:34 UTC, exit 0, 7 s
```
release licence: CC-BY-NC-4.0
{
 "files": [
  "ACKNOWLEDGEMENTS.md",
  "CITATION.cff",
  "LICENSE.txt",
  "MANIFEST.json",
  "catalogue.vot",
  "metadata.json"
 ],
 "problems": []
}
```

### [21] `cd labs/L400/21-open-data-practice && python defects.py`
run 2026-11-02 13:35 UTC, exit 0, 33 s
```
{"defect": "catalogue edited after the manifest", "A_files_present": false, "B_check": true, "B_says": ["manifest: catalogue.vot missing or changed"]}
{"defect": "CITATION.cff without message", "A_files_present": false, "B_check": true, "B_says": ["citation: required key 'message' missing"]}
{"defect": "licence relaxed to CC-BY-4.0", "A_files_present": false, "B_check": true, "B_says": ["licence: release CC-BY-4.0 drops the NC condition of input gaia_dr3_astrometry (LicenseRef-CC-BY-NC-3.0-IGO)"]}
{"defect": "Gaia credit paraphrased", "A_files_present": false, "B_check": true, "B_says": ["credit: verbatim acknowledgement for gaia_dr3_astrometry missing"]}
{"defect": "row with a missing TD", "A_files_present": false, "B_check": true, "B_says": ["votable: row 3 has 5 TD for 6 FIELD"]}
{"defect": "FIELD without unit", "A_files_present": false, "B_check": true, "B_says": ["votable: FIELD parallax has no unit"]}
caught: A 0/6, B 6/6
```

### [21] `cd labs/L400/21-open-data-practice && BUILD_TARGET=mine python -m unittest test_build_task test_fitness`
run 2026-11-02 13:35 UTC, exit 1, 8 s
```
FF..F
======================================================================
FAIL: test_conflict_goes_to_a_human (test_build_task.TestLicencePropagation.test_conflict_goes_to_a_human)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/21-open-data-practice/test_build_task.py", line 31, in test_conflict_goes_to_a_human
    with self.assertRaises(ValueError):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: ValueError not raised

======================================================================
FAIL: test_noncommercial_input_keeps_nc (test_build_task.TestLicencePropagation.test_noncommercial_input_keeps_nc)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/21-open-data-practice/test_build_task.py", line 25, in test_noncommercial_input_keeps_nc
    self.assertEqual(target.release_licence([inp("BY"), inp("BY-NC"), inp("PD")]), "CC-BY-NC-4.0")
AssertionError: 'CC-BY-4.0' != 'CC-BY-NC-4.0'
- CC-BY-4.0
+ CC-BY-NC-4.0
?       +++


======================================================================
FAIL: test_published_release_is_clean (test_fitness.TestReleaseGate.test_published_release_is_clean)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/21-open-data-practice/test_fitness.py", line 23, in test_published_release_is_clean
    self.assertEqual(target.check(target.build(Path(tmp) / "release")), [])
AssertionError: Lists differ: ['licence: release CC-BY-4.0 drops the NC [65 chars]GO)'] != []

First list contains 1 additional elements.
First extra element 0:
'licence: release CC-BY-4.0 drops the NC condition of input gaia_dr3_astrometry (LicenseRef-CC-BY-NC-3.0-IGO)'

+ []
- ['licence: release CC-BY-4.0 drops the NC condition of input '
-  'gaia_dr3_astrometry (LicenseRef-CC-BY-NC-3.0-IGO)']

----------------------------------------------------------------------
Ran 5 tests in 2.491s

FAILED (failures=3)
```

### [21] `cd labs/L400/21-open-data-practice && python -m unittest test_build_task test_fitness -v`
run 2026-11-02 13:35 UTC, exit 0, 29 s
```

----------------------------------------------------------------------
Ran 5 tests in 0.214s

OK
```

### [21] `cd labs/L400/21-open-data-practice && python try_it.py`
run 2026-11-02 13:36 UTC, exit 0, 3 s
```
1. + BY-SA input -> ValueError: NonCommercial and ShareAlike inputs conflict: needs human review
2. without Gaia -> CC-BY-4.0 | problems: []
```

### [22] `cd labs/L400/22-capstone && python run_capstone.py`
run 2026-11-02 13:38 UTC, exit 0, 195 s
```
{"milestone": "M1 load + detrend", "pass": true, "rms_over_noise": {"S07": 0.988, "S08": 0.973, "S09": 1.02, "S10": 1.0, "S11": 0.981, "S12": 0.996}}
{"milestone": "M2 BLS search", "pass": true, "period_error_percent": {"S01": 0.032, "S02": 0.049, "S03": 0.045, "S04": 0.021, "S05": 0.021}}
{"milestone": "M3 vetting", "pass": true, "candidates": ["S01", "S02", "S03"], "rejected": {"S04": "secondary eclipse at phase 0.5 (5217 ppm)", "S05": "odd/even depths differ (5937 vs 11603 ppm)"}}
{"milestone": "M4 MCMC fit", "pass": true, "depth_minus_truth_in_sigma": {"S01": 2.22, "S02": -0.95, "S03": 0.9}, "fits": {"S01": {"depth_ppm": 8169, "depth_err_ppm": 76, "t14_h": 2.71, "acceptance": 0.239, "tau": 39.1}, "S02": {"depth_ppm": 2940, "depth_err_ppm": 63, "t14_h": 3.45, "acceptance": 0.288, "tau": 33.6}, "S03": {"depth_ppm": 5096, "depth_err_ppm": 107, "t14_h": 4.23, "acceptance": 0.285, "tau": 25.0}}}
{"milestone": "M5 provenance + reproducibility", "pass": true, "inputs_hashed": 12, "s01_sha256": "3a31a29c1689", "rerun_period_d": 3.1244}
{"milestone": "M6 agent explanation", "pass": true, "explained": 6, "published": [], "overclaims_blocked": ["S04", "S05", "S06"], "unverified_numbers": ["1.8"]}
{"scorecard": "PASS", "passed": 6, "total": 6}
```

### [22] `cd labs/L400/22-capstone && python try_it.py`
run 2026-11-02 13:41 UTC, exit 0, 36 s
```
1. S03 window 0.75 d: period 12.3454 d, depth 4834 ppm, SNR 43.96
1. S03 window 0.25 d: period 12.3454 d, depth 726 ppm, SNR 6.69
2. S05 odd/even threshold 3.0 sigma -> ('rejected', ['odd/even depths differ (5937 vs 11603 ppm)'])
2. S05 odd/even threshold inf sigma -> ('planet_candidate', [])
```

### [22] `cd labs/L400/22-capstone && python -m unittest test_fitness -v`
run 2026-11-02 13:41 UTC, exit 5, 35 s
```
setUpModule (test_fitness) ... ERROR

======================================================================
ERROR: setUpModule (test_fitness)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/22-capstone/test_fitness.py", line 16, in setUpModule
    RESULTS, _ = run_capstone.analyse_all()
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/workspace/working/kb/astronomy/labs/L400/22-capstone/run_capstone.py", line 32, in analyse_all
    t, f, _ = pipeline.load(path)
              ^^^^^^^^^^^^^^^^^^^
  File "/mnt/workspace/working/kb/astronomy/labs/L400/22-capstone/pipeline.py", line 23, in load
    a = np.loadtxt(path, delimiter=",", skiprows=1, encoding="utf-8")
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/numpy/lib/_npyio_impl.py", line 1381, in loadtxt
    arr = _read(fname, dtype=dtype, comment=comment, delimiter=delimiter,
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/numpy/lib/_npyio_impl.py", line 1011, in _read
    fh = np.lib._datasource.open(fname, 'rt', encoding=encoding)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/numpy/lib/_datasource.py", line 191, in open
    ds = DataSource(destpath)
         ^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/numpy/lib/_datasource.py", line 248, in __init__
    self._destpath = os.path.abspath(destpath)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen posixpath>", line 412, in abspath
FileNotFoundError: [Errno 2] No such file or directory

----------------------------------------------------------------------
Ran 0 tests in 29.043s

FAILED (errors=1)
```

### [23] `cd labs/L500/23-foundations-mechanics && python mechanics.py`
run 2026-11-02 13:42 UTC, exit 0, 60 s
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

### [23] `cd labs/L500/23-foundations-mechanics && python -m unittest -v`
run 2026-11-02 13:44 UTC, exit 0, 32 s
```

----------------------------------------------------------------------
Ran 5 tests in 19.859s

OK
```

### [24] `cd labs/L500/24-foundations-stars && python stars.py`
run 2026-11-02 13:44 UTC, exit 0, 5 s
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

### [24] `cd labs/L500/24-foundations-stars && python -m unittest -v`
run 2026-11-02 13:44 UTC, exit 0, 10 s
```

----------------------------------------------------------------------
Ran 4 tests in 0.227s

OK
```

### [26] `cd labs/L500/26-ethics-dark-skies && python sky_numbers.py`
run 2026-11-02 13:46 UTC, exit 0, 0 s
```
mag 5 vs mag 7 satellite: 6.31x brighter; mag 4 vs 7: 15.85x
zenith satellite at  350 km: sunlit until the Sun is 18.6 deg below the horizon (into astronomical night)
zenith satellite at  550 km: sunlit until the Sun is 23.0 deg below the horizon (into astronomical night)
zenith satellite at 1200 km: sunlit until the Sun is 32.7 deg below the horizon (into astronomical night)
inputs ['CC-BY-NC-3.0-IGO'] -> release CC-BY-4.0: NOT OK (drops ['NC'])
inputs ['CC-BY-NC-3.0-IGO'] -> release CC-BY-NC-4.0: OK (keeps every input condition)
inputs ['CC-BY-NC-3.0-IGO', 'CC-BY-SA-4.0'] -> release CC-BY-NC-4.0: NOT OK (NC and SA inputs cannot both be honoured automatically - needs a person)
inputs ['CC0-1.0', 'CC-BY-4.0'] -> release CC-BY-4.0: OK (keeps every input condition)
```

### [26] `cd labs/L500/26-ethics-dark-skies && python -m unittest -v`
run 2026-11-02 13:46 UTC, exit 0, 4 s
```

----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
```

### [27] `cd labs/L500/27-reading-seminar && python reading_checks.py`
run 2026-11-02 13:46 UTC, exit 0, 0 s
```
Hubble 1929: K = 500 km/s/Mpc -> 1/K = 1.96 Gyr
NGC 7619: v = +3910 km/s (solar-motion corrected) / K = 7.82 Mpc (paper: 7.8 x 10^6 pc)
NGC 7619: m = 11.8 at 7.8 Mpc -> M = -17.66 (paper: -17.65)
22 nebulae without individual distances: 745 km/s at 1.4 Mpc -> K = 532 (paper: 530)
modern H0 = 67.4: NGC 7619 at 58.0 Mpc; K/H0 = 7.42 (the 1929 distance scale was too short by this factor)
Gaia DR3: >33 million radial velocities / ~1500 million sources with class probabilities = 2.2%
Gaia DR3: 34 months of data = 2.83 yr
```

### [27] `cd labs/L500/27-reading-seminar && python -m unittest -v`
run 2026-11-02 13:46 UTC, exit 0, 4 s
```

----------------------------------------------------------------------
Ran 2 tests in 0.006s

OK
```

### [27] `cd labs/L500/27-reading-seminar && cd ../../.. && python research/l500_checks.py`
run 2026-11-02 13:46 UTC, exit 0, 70 s
```
lessons 5 | theorem checks re-run and matched: 11 | problem numbers recomputed: 93 in 24 calculation problems + 2 exams | problems total 41
OK
```

### [25] `cd labs/L500/25-foundations-cosmology-bayes && python cosmo_bayes.py`
run 2026-11-02 13:49 UTC, exit 0, 17 s
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

### [25] `cd labs/L500/25-foundations-cosmology-bayes && python -m unittest -v`
run 2026-11-02 13:49 UTC, exit 0, 26 s
```

----------------------------------------------------------------------
Ran 4 tests in 15.197s

OK
```

### [22] `cd labs/L400/22-capstone && python -m unittest test_fitness -v`
run 2026-11-02 13:50 UTC, exit 5, 39 s
```
setUpModule (test_fitness) ... ERROR

======================================================================
ERROR: setUpModule (test_fitness)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/astronomy/labs/L400/22-capstone/test_fitness.py", line 16, in setUpModule
    RESULTS, _ = run_capstone.analyse_all()
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/workspace/working/kb/astronomy/labs/L400/22-capstone/run_capstone.py", line 32, in analyse_all
    t, f, _ = pipeline.load(path)
              ^^^^^^^^^^^^^^^^^^^
  File "/mnt/workspace/working/kb/astronomy/labs/L400/22-capstone/pipeline.py", line 23, in load
    a = np.loadtxt(path, delimiter=",", skiprows=1, encoding="utf-8")
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/numpy/lib/_npyio_impl.py", line 1381, in loadtxt
    arr = _read(fname, dtype=dtype, comment=comment, delimiter=delimiter,
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/numpy/lib/_npyio_impl.py", line 1011, in _read
    fh = np.lib._datasource.open(fname, 'rt', encoding=encoding)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/numpy/lib/_datasource.py", line 191, in open
    ds = DataSource(destpath)
         ^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/numpy/lib/_datasource.py", line 248, in __init__
    self._destpath = os.path.abspath(destpath)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen posixpath>", line 412, in abspath
FileNotFoundError: [Errno 2] No such file or directory

----------------------------------------------------------------------
Ran 0 tests in 19.064s

FAILED (errors=1)
```

### [22] `cd labs/L400/22-capstone && python -m unittest test_fitness -v`
run 2026-11-02 13:53 UTC, exit 0, ~180 s (run directly in the shell, not through the restore wrapper; see "Differences")
```
…

----------------------------------------------------------------------
Ran 4 tests in 174.210s

OK
```

## Differences from the lab READMEs / lesson JSON (2026-11-02)

All seeded, deterministic outputs (detections, hashes, completeness, purity, wrong_cones, chi2/BIC, coverage,
scorecards, L500 checks, catalogue hashes) matched the READMEs exactly. Only wall-clock numbers and two runner
issues differed:

- Lesson 17 (survey pipeline): frames_per_s varies by design. Here, shipped A 272.7 / B 3.9 / C 244.2 and solution
  A 231.1 / B 1.9 / C 117.4 frames/s; README shows e.g. C 913.7 (shipped) and 331.8 (solution), and the ADR records
  "C about 259 frames/s, A 166-241, B 10-19". On this shared, slow 1-CPU sandbox A beat C in both runs and B was
  slower than the ADR's range, so "C fastest" was NOT reproduced here; C still clears the fitness budget (>= 50 frames/s,
  `test_fitness` OK). 17.md says so explicitly.
- Lesson 19 (big catalogues): ms_per_query varies by design (brute 12.37-14.88 ms here vs 6-11 ms in the ADR).
  tryIt 2 (radius 5 deg) gave a 7x speed-up here against 21x in the README and 17-31x in the ADR. 19.md says so.
- Lesson 22 (capstone): `python run_capstone.py` took 195 s here (README: about 30 s); output identical to the README.
  `python -m unittest test_fitness -v` run through the restore wrapper failed twice in setUpModule with
  FileNotFoundError from os.getcwd() (the lab folder briefly vanished on the slow mount); run directly in a shell it
  passed: `Ran 4 tests in 174.210s`, `OK` (recorded above). scorecard.jsonl was re-written with identical bytes.
- Lesson 25: the first wrapped run failed before starting (the backup copy hit a mount error); the re-run above is the
  one quoted.
- Lesson 13: cosmic-ray counts were read from calib_log.jsonl with a small helper (cosmics.py, kept outside the topic):
  3 per frame, 4 on frame 17, as the lesson states.
