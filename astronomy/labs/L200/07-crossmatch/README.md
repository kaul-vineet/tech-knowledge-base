# 07 · Catalogues and cross-matching

Match 2042 sources to a 2000-source catalogue across RA 0/360 with unit vectors and a k-d tree; then make the match one-to-one.

Read the concept note first: `../../../content/concepts/L200/07-crossmatch.md`.

## Run
```bash
python crossmatch.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L200\07-crossmatch` on Windows, `cd labs/L200/07-crossmatch` on macOS).

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux; deterministic, identical on every run)
`python crossmatch.py`:
```
A 2000 sources, B 2042 sources (1812 true counterparts); the field wraps: 549 sources at RA 359.x deg
matched 1842 within 1 arcsec; correct 1812/1812; median sep 0.233 arcsec
k-d tree distance evaluations: 38,999 vs brute force 4,084,000
A sources claimed by more than one B source (blends): 25
RA 359.9999 vs 0.0001 at Dec 28: naive |dRA| = 359.9998 deg, true separation = 0.6357 arcsec
```

## Test
```bash
python -m unittest -v
```
Observed: `Ran 10 tests ... OK (skipped=1)` - library comparisons are skipped locally (not installed) and run in CI.

## Try it
```bash
python try_it.py
```
Observed:
```
radius 0.5 arcsec: matched 1768, correct 1743/1812
radius 1.0 arcsec: matched 1842, correct 1812/1812
radius 3.0 arcsec: matched 1842, correct 1812/1812
leaf size   4: 12,568 distance evaluations
leaf size  16: 38,999 distance evaluations
leaf size 256: 517,250 distance evaluations
```

## Build it (your task)
Make match_one_to_one() return at most one B source per A source: when several B sources claim the same A source (blends), keep the closest and mark the others unmatched (-1).

Hints:
- Sort the matched B rows by separation, closest first (np.argsort with NaN replaced by inf).
- Walk through them and remember which A indices are taken (a set).
- Copy idx/sep before changing them.

Check: `python -m unittest test_build_task -v` checks `solution/` by default. To check **your** edited file:
```bash
BUILD_TARGET=mine python -m unittest test_build_task -v      # macOS / Linux
$env:BUILD_TARGET = "mine"; python -m unittest test_build_task -v   # Windows PowerShell
```
Observed on the shipped (unfinished) file: `Ran 3 tests ... FAILED (failures=1)`. The reference solution output (`python solution/crossmatch.py`):
```
A 2000 sources, B 2042 sources (1812 true counterparts); the field wraps: 549 sources at RA 359.x deg
matched 1842 within 1 arcsec; correct 1812/1812; median sep 0.233 arcsec
k-d tree distance evaluations: 38,999 vs brute force 4,084,000
A sources claimed by more than one B source (blends): 25
one-to-one: 1817 matches, true counterparts kept 1807/1812, duplicates left 0
RA 359.9999 vs 0.0001 at Dec 28: naive |dRA| = 359.9998 deg, true separation = 0.6357 arcsec
```

## Library equivalent (pending-ci)
`crossmatch_astropy.py` compares the pairs with Astropy 8.0.2 `match_to_catalog_sky` and SciPy 1.18.1 `cKDTree`. **Not run yet** (pending-ci).

## Notes
Catalogues are synthetic and seeded (not real stars). `python crossmatch.py --export` writes cat_a.csv / cat_b.csv for TOPCAT.

## Files
- `crossmatch.py` - main lab code (match_one_to_one unfinished)
- `kdtree.py` - numpy k-d tree with an evaluation counter
- `solution/crossmatch.py` - buildTask solution
- `crossmatch_astropy.py` - Astropy + SciPy cKDTree equivalent (pending-ci)
- `test_crossmatch.py` - separation, tree vs brute force, match counts
- `test_build_task.py` - buildTask check (BUILD_TARGET=mine switch)
- `try_it.py` - tryIt script
