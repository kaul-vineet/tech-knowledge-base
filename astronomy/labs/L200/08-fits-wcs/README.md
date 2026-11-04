# 08 · FITS images and WCS

Write and read a FITS image by hand (80-character cards, 2880-byte blocks, big-endian data) and convert pixels to RA/Dec with a TAN WCS.

Read the concept note first: `../../../content/concepts/L200/08-fits-wcs.md`.

## Run
```bash
python fitslite.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L200\08-fits-wcs` on Windows, `cd labs/L200/08-fits-wcs` on macOS).

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux; deterministic, identical on every run)
`python fitslite.py`:
```
wrote star_field.fits (20160 bytes = 7 blocks of 2880); header cards: 17 incl. END
read back: shape (64, 64), dtype float32, identical: True
pixel (32.5, 32.5) -> RA 83.822100 Dec -5.391100
pixel (   1,    1) -> RA 83.830889 Dec -5.399850
pixel (  64,   64) -> RA 83.813311 Dec -5.382350
brightest pixel: numpy [row 45, col 51] = FITS pixel (52, 46)
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
 0 extra cards: 20160 bytes
20 extra cards: 23040 bytes
pixel (1,1) vs (0,0): dRA*cos(dec) = 1.000 arcsec, dDec = -1.000 arcsec
```

## Build it (your task)
Implement sky_to_pixel(h, ra, dec): the gnomonic (TAN) projection of (RA, Dec) onto the tangent plane at CRVAL, then the inverse CD matrix plus CRPIX.

Hints:
- Projection: cos c = sin d sin d0 + cos d cos d0 cos(a - a0); xi = cos d sin(a - a0) / cos c; eta = (sin d cos d0 - cos d sin d0 cos(a - a0)) / cos c.
- Convert xi, eta to degrees before undoing the CD matrix (np.linalg.solve).
- Add CRPIX: FITS pixels are 1-based.

Check: `python -m unittest test_build_task -v` checks `solution/` by default. To check **your** edited file:
```bash
BUILD_TARGET=mine python -m unittest test_build_task -v      # macOS / Linux
$env:BUILD_TARGET = "mine"; python -m unittest test_build_task -v   # Windows PowerShell
```
Observed on the shipped (unfinished) file: `Ran 3 tests ... FAILED (errors=3)`. The reference solution output (`python solution/fitslite.py`):
```
wrote star_field.fits (20160 bytes = 7 blocks of 2880); header cards: 17 incl. END
read back: shape (64, 64), dtype float32, identical: True
pixel (32.5, 32.5) -> RA 83.822100 Dec -5.391100 -> back to pixel (32.500000, 32.500000)
pixel (   1,    1) -> RA 83.830889 Dec -5.399850 -> back to pixel (1.000000, 1.000000)
pixel (  64,   64) -> RA 83.813311 Dec -5.382350 -> back to pixel (64.000000, 64.000000)
brightest pixel: numpy [row 45, col 51] = FITS pixel (52, 46)
```

## Library equivalent (pending-ci)
`fits_astropy.py` opens our file with astropy.io.fits (`verify('exception')`) and compares pixel-to-sky with astropy.wcs. **Not run yet** (pending-ci).

## Notes
The image is synthetic and seeded (12 Gaussian stars on a noisy sky), not an observation.

## Files
- `fitslite.py` - main lab code (sky_to_pixel unfinished)
- `field.py` - synthetic seeded star field
- `solution/fitslite.py` - buildTask solution
- `fits_astropy.py` - astropy.io.fits + astropy.wcs equivalent (pending-ci)
- `test_fitslite.py` - blocks, byte order, axis order, WCS
- `test_build_task.py` - buildTask check (BUILD_TARGET=mine switch)
- `try_it.py` - tryIt script
