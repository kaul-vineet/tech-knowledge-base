# 09 · Aperture photometry

Measure five synthetic stars with a circular aperture and a median sky annulus, predict their SNR with the CCD equation, then calibrate magnitudes.

Read the concept note first: `../../../content/concepts/L200/09-aperture-photometry.md`.

## Run
```bash
python photometry.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L200\09-aperture-photometry` on Windows, `cd labs/L200/09-aperture-photometry` on macOS).

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux; deterministic, identical on every run)
`python photometry.py`:
```
star  true(e-)  measured(e-)  ratio   sky/px  SNR
   0     20000       20006.2  1.000   100.21  102.6
   1      8000        7774.1  0.972    99.99   48.4
   2      3000        3046.8  1.016    99.50   21.0
   3      1000         827.5  0.827   101.15    6.0
   4       300         436.0  1.453    99.28    3.2
aperture r=6 px holds 0.99966 of a star's light (Gaussian PSF)
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
r=2.0: star0 SNR   99.6   star3 SNR  10.4
r=3.0: star0 SNR  118.3   star3 SNR  11.2
r=4.0: star0 SNR  118.5   star3 SNR   9.7
r=6.0: star0 SNR  102.6   star3 SNR   6.0
r=9.0: star0 SNR   74.1   star3 SNR   2.3
median sky 102.29 -> net 19877.2 e- | mean sky 118.43 -> net 18059.1 e- (true 20000)
```

## Build it (your task)
Implement calibrate(results, ref_index, ref_mag): instrumental magnitudes -2.5 log10(net / EXPTIME), a zero point from the reference star, calibrated magnitudes, and errors 1.0857 / SNR; non-detections (net <= 0) give NaN.

Hints:
- zero_point = ref_mag - instrumental[ref_index].
- 2.5 / ln(10) = 1.0857: a 1% flux error is about 0.011 mag.
- Return a list of (mag, err) tuples in star order.

Check: `python -m unittest test_build_task -v` checks `solution/` by default. To check **your** edited file:
```bash
BUILD_TARGET=mine python -m unittest test_build_task -v      # macOS / Linux
$env:BUILD_TARGET = "mine"; python -m unittest test_build_task -v   # Windows PowerShell
```
Observed on the shipped (unfinished) file: `Ran 3 tests ... FAILED (errors=3)`. The reference solution output (`python solution/photometry.py`):
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

## Library equivalent (pending-ci)
`photometry_photutils.py` measures the same stars with photutils 3.1.1 (CircularAperture, CircularAnnulus, ApertureStats median, subpixel 5). **Not run yet** (pending-ci).

## Notes
The image is synthetic and seeded; `python photometry.py --export` writes field.fits for AstroImageJ or DS9.

## Files
- `photometry.py` - main lab code (calibrate unfinished)
- `solution/photometry.py` - buildTask solution
- `photometry_photutils.py` - photutils 3.1.1 equivalent (pending-ci)
- `test_photometry.py` - aperture area, sky, flux within 3 sigma, noise-free exactness
- `test_build_task.py` - buildTask check (BUILD_TARGET=mine switch)
- `try_it.py` - tryIt script
