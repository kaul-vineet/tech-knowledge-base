# 13 · Calibration frames: bias, dark, flat and cosmic-ray rejection

A seeded synthetic camera (64 × 64 px, **synthetic data**) takes 10 bias, 10 dark (60 s), 10 twilight-flat and 30 light frames of one **constant** star. Tracking is poor: the star drifts from x = 12 to x = 52, straight through the vignetting and a dust donut. `calibrate.py` builds master frames, calibrates each light, cleans cosmic rays and measures the star's light curve. Every step writes one JSON line to `calib_log.jsonl`.

Read the concept note first: `../../../content/concepts/L300/13-ccd-calibration.md`. Main lab: Python 3.12 + numpy only. The ccdproc equivalent needs the L300 pins: `python -m pip install -r ../requirements.txt` (same command on macOS and Windows).

## Run
```bash
python calibrate.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L300\13-ccd-calibration` on Windows, `cd labs/L300/13-ccd-calibration` on macOS). It also writes `master_flat.fits` (open it in SAOImage DS9 or Siril).

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux)
Seeded (seed 13), identical on every run.
```
relative flux, every 5th frame: 0.9971 1.0070 1.0082 1.0031 1.0043 0.9881
{"rms_percent": 0.88, "robust_rms_percent": 0.899, "expected_noise_percent": 0.224, "variable": true}
master_flat min/max: 0.8527 1.0792 (true response 0.75/1.00)
```
First lines of `calib_log.jsonl` and the frame with the seeded cosmic ray:
```
{"step": "master_bias", "median_adu": 999.95}
{"step": "master_dark", "median_adu": 2.04, "max_adu": 205.1}
{"step": "master_flat", "min": 0.8527, "max": 1.0792}
{"frame": 0, "x": 12.0, "flux_adu": 122892.0, "sky_adu": 122.3, "cosmics_cleaned": 3}
{"frame": 17, "x": 35.45, "flux_adu": 119922.4, "sky_adu": 124.65, "cosmics_cleaned": 4}
```

## Failure lab: break it, see it, fix it
- **Fault (shipped in `calibrate.py`):** `masters()` combines and normalises the raw flats **without subtracting the master bias**. The 1000 ADU pedestal carries no response, so the normalised flat is too flat: min 0.8527 instead of about 0.813. The dust donut and the vignetting are only partly divided out.
- **Symptom (read it in `calib_log.jsonl`):** the master_flat line shows min/max 0.8527/1.0792. The constant star's robust rms is 0.899 % against a photon-noise floor of 0.224 %, and the light curve says `"variable": true`. That is fake variability, traced along the star's path.
- **Fix (your build task):** `sigma_clip_mean(f["flat"] - bias)` before normalising (`solution/calibrate.py`). Robust rms falls to 0.382 % and the star is `variable: false`.
- **Proof:** `test_build_task.py`. With `BUILD_TARGET=mine` on the shipped file, all 3 tests fail (12 failures, counting the 10 seed subtests); on the solution all pass. `TestFailureLab` in `test_calibrate.py` keeps the fault reproducible.

## Test
```bash
python -m unittest -v
```
Observed: `Ran 12 tests ... OK (skipped=1)` - the ccdproc test is skipped locally (not installed) and runs in CI.

## Try it
```bash
python try_it.py
```
Observed:
```
1. no cleaning: frame 17 relative flux 1.1640; plain rms 2.96%, robust rms 0.377%, variable=False
2. shipped flat, 30k e- flats: robust rms 0.366%, variable=False, flat min 0.8267 (fixed pipeline gives 0.813 at 6k e-)
```

## Build it (hardening task)
Fix `masters()` in `calibrate.py` so the master flat holds only the pixel response.

Hints:
- The Siril / ccdproc formula is calibrated = (L − D) / (F − O). The flat needs its offset (bias) removed **before** normalisation.
- The flats are short twilight exposures, so dark current is negligible (0.05 e-/s).
- Check `master_flat` min/max in `calib_log.jsonl`: the true response normalised to its median is 0.821/1.094.

Check your file: `BUILD_TARGET=mine python -m unittest test_build_task -v` (PowerShell: `$env:BUILD_TARGET = "mine"`, then `python -m unittest test_build_task -v`). Shipped file: `Ran 3 tests ... FAILED (failures=12)`; after the fix: `OK`. Without the variable the test checks `solution/calibrate.py` (observed: `Ran 3 tests ... OK`).
Reference solution output (`python solution/calibrate.py`):
```
relative flux, every 5th frame: 1.0002 1.0051 1.0022 1.0063 1.0033 1.0020
{"rms_percent": 0.389, "robust_rms_percent": 0.382, "expected_noise_percent": 0.224, "variable": false}
master_flat min/max: 0.813 1.1009 (true response 0.75/1.00)
```

## Stretch (after the build task)
Measure the camera's gain and read noise from the frames themselves (photon transfer): gain = ((F̄1 + F̄2) − (B̄1 + B̄2)) / (var(F1 − F2) − var(B1 − B2)), read noise = gain · std(B1 − B2)/√2. Average over 5 frame pairs.
Check: `python -m unittest test_stretch -v` (observed: `Ran 1 test ... OK`). Reference (`python solution/gain.py`):
```
measured gain 1.473 e-/ADU (true 1.5), read noise 6.89 e- (true 7.0)
```

## Library equivalent (pending-ci)
`calibrate_ccdproc.py` repeats the reduction with `ccdproc.combine` (sigma clipping), `subtract_bias`, `subtract_dark`, `flat_correct` and `cosmicray_lacosmic` (astroscrappy). `test_calibrate.py` requires its light-curve rms to stay below 0.6 %. It is skipped here and runs in CI.

## Files
- `calibrate.py` - main lab code (ships the unfixed `masters()`)
- `camera.py` - seeded synthetic camera; `fitsmini.py` - minimal FITS writer
- `calibrate_ccdproc.py` - ccdproc equivalent (pending-ci)
- `solution/calibrate.py` - buildTask solution; `solution/gain.py` - stretch solution
- `try_it.py`; `test_calibrate.py` (unit tests + fault reproduction); `test_build_task.py`; `test_stretch.py`
- `calib_log.jsonl`, `master_flat.fits` - written by the last run
