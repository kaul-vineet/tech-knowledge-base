# 14 · Plate solving (astrometry-lite): match star triangles, fit a WCS, check residuals

A camera reports star positions in pixels, and the mount's pointing is off by about 0.18°. `platesolve.py` turns those pixels into sky coordinates. It matches triangles of bright stars against a catalogue, keeps the geometry most pairs agree on (RANSAC), and fits a TAN WCS (CD matrix + CRVAL). It then reports residuals in arcseconds. There are two **synthetic** fields with known truth: "orion" near Dec −5° and "cassiopeia" near Dec +62°.

Read the concept note first: `../../../content/concepts/L300/14-plate-solving.md`. Main lab: Python 3.12 + numpy only (`fields.py`: seeded catalogues + detections and the TAN projection; `triangles.py`: invariants, votes, RANSAC, affine fit).

## Run
```bash
python platesolve.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L300\14-plate-solving` on Windows, `cd labs/L300/14-plate-solving` on macOS).

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux)
Seeded, identical on every run.
```
{"field": "orion", "solved": true, "n_matched": 32, "rms_arcsec": 0.373, "pointing_error_arcsec": 0.07, "scale_arcsec_px": 2.0045, "rotation_deg": 11.991}
{"field": "cassiopeia", "solved": false}
```

## Failure lab: break it, see it, fix it
- **Fault (shipped in `platesolve.py`):** `to_plane()` uses raw offsets (ΔRA, ΔDec) as plane coordinates. At Dec −5° a degree of RA is 0.996° on the sky, so the shapes barely change and Orion solves (rms 0.373″). The scale is still 0.2 % off (2.0045″/px). At Dec +62° it is only 0.47°, so every triangle is stretched (tryIt 1: invariants differ by 36 % against a 0.8 % tolerance) and Cassiopeia **does not solve**.
- **Fix (your build task):** project with the gnomonic (TAN) projection that the FITS WCS standard (Calabretta & Greisen 2002) and the camera use (`fields.tan_project` / `tan_deproject`; `solution/platesolve.py`).
- **Proof:** `test_build_task.py`. With `BUILD_TARGET=mine` on the shipped file, both tests fail (3 subtest failures: Cassiopeia twice, plus Orion's 2.0045″ scale); on the solution both pass (rms < 0.6″, pointing < 1″, rotation within 0.05°, scale within 0.001″/px). `TestFailureLab` in `test_platesolve.py` keeps the fault reproducible.

## Test
```bash
python -m unittest -v
```
Observed: `Ran 9 tests ... OK (skipped=1)` - the astropy test is skipped locally (not installed) and runs in CI.

## Try it
```bash
python try_it.py
```
Observed:
```
1. orion      Dec -5.4: invariants flat [1.049 1.083] vs TAN [1.051 1.078] (max relative difference 0.004; match tolerance 0.008)
1. cassiopeia Dec +62.1: invariants flat [1.049 1.083] vs TAN [1.097 1.685] (max relative difference 0.357; match tolerance 0.008)
2. TOL 0.008: 12 voted pairs, 8 agree with the best geometry
2. TOL 0.05: 12 voted pairs, 3 agree with the best geometry
```

## Build it (hardening task)
Replace `to_plane()` / `from_plane()` in `platesolve.py` with the TAN projection, so that triangles keep their shape at every declination.

Hints:
- `fields.tan_project(ra, dec, ra0, dec0)` and `fields.tan_deproject(xi, eta, ra0, dec0)` already exist (the test data uses them).
- At the tangent point, ξ ≈ ΔRA · cos(Dec): the missing cos(Dec) is the whole bug at small offsets.

Check your file: `BUILD_TARGET=mine python -m unittest test_build_task -v` (PowerShell: `$env:BUILD_TARGET = "mine"`, then `python -m unittest test_build_task -v`). Shipped file: `Ran 2 tests ... FAILED (failures=3)`; after the fix: `OK`. Without the variable the test checks `solution/platesolve.py` (observed: `Ran 2 tests ... OK`).
Reference solution output (`python solution/platesolve.py`):
```
{"field": "orion", "solved": true, "n_matched": 32, "rms_arcsec": 0.359, "pointing_error_arcsec": 0.07, "scale_arcsec_px": 2.0001, "rotation_deg": 11.99}
{"field": "cassiopeia", "solved": true, "n_matched": 23, "rms_arcsec": 0.503, "pointing_error_arcsec": 0.05, "scale_arcsec_px": 2.0002, "rotation_deg": -32.999}
```

## Stretch (after the build task)
If the hint is 0.8° off, the catalogue window around it misses the field. Do not give up: retry on rings of hints 0.4° apart **on the sky** (RA steps divided by cos Dec), and accept the first solution with at least 10 matched stars.
Check: `python -m unittest test_stretch -v` (observed: `Ran 1 test ... OK`). Reference (`python solution/search.py`):
```
plain solve, hint 0.8 deg off: {"field": "orion", "solved": false}
search (5 hints tried): {"field": "orion", "solved": true, "n_matched": 32, "rms_arcsec": 0.359, "pointing_error_arcsec": 0.07, "scale_arcsec_px": 2.0001, "rotation_deg": 11.99}
```

## Derived formula: the TAN projection
The gnomonic (TAN) formulas in `fields.tan_project()` are **derived here, not quoted**: §5.1.3 of Calabretta & Greisen (2002) could not be read in full. Sketch: rotate the star's unit vector into a frame whose z-axis points at the tangent point (ra0, dec0). Its components are x = cos δ sin(α−α0), y = cos δ0 sin δ − sin δ0 cos δ cos(α−α0) and z = cos c, where cos c = sin δ0 sin δ + cos δ0 cos δ cos(α−α0) (spherical law of cosines; c is the angular distance from the tangent point). Projecting from the sphere's centre onto the plane z = 1 gives ξ = x/z and η = y/z, at radius tan c = cot θ, with native latitude θ = 90° − c. This is the TAN rule R_θ = (180°/π) cot θ, which is C&G's zenithal AZP formula (eq. 16) with μ = 0. Checks: `test_tan_round_trip` (project, then deproject) here, and `platesolve_astropy.py` against `astropy.wcs` in CI. Lesson 8 uses the same projection.

## Library equivalent (pending-ci)
`platesolve_astropy.py` takes our matched stars and fits a TAN WCS with `astropy.wcs.utils.fit_wcs_from_points(..., projection="TAN")`; the test requires astropy's pixel scale to equal 2.000″/px within 0.002. On real images, astrometry.net's `solve-field` does the blind search with 4-star quads and verifies the result (Lang et al. 2010).

## Files
- `platesolve.py` - main lab code (ships the unfixed `to_plane()`)
- `fields.py` - synthetic catalogues, detections, TAN projection; `triangles.py` - matching helpers
- `platesolve_astropy.py` - astropy equivalent (pending-ci)
- `solution/platesolve.py` - buildTask solution; `solution/search.py` - stretch solution
- `try_it.py`; `test_platesolve.py` (unit tests + fault reproduction); `test_build_task.py`; `test_stretch.py`
