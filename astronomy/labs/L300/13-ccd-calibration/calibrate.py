"""L300 CCD calibration: bias, dark, flat, cosmic-ray cleaning, then the light curve of a CONSTANT star.

calibrated = (light - master_bias - master_dark) / master_flat      (ccdproc / Siril: Lc = (L - D) / (F - O))
The star drifts across the vignetting and a dust donut: a wrong flat turns that path into fake variability.
python calibrate.py   ->  light-curve summary; calib_log.jsonl (one JSON line per step/frame); master_flat.fits
"""
import json
from pathlib import Path

import numpy as np

import camera
from fitsmini import write_fits

HERE = Path(__file__).resolve().parent
AP_R, ANN_IN, ANN_OUT, CR_SIGMA = 5.0, 8.0, 12.0, 6.0


def sigma_clip_mean(stack, k=3.0):
    """Combine frames pixel by pixel, rejecting values > k robust sigmas from the median (cosmic rays, satellites)."""
    med = np.median(stack, axis=0)
    mad = 1.4826 * np.median(np.abs(stack - med), axis=0) + 1e-9  # robust sigma (ccdproc: 1.4826 x MAD)
    keep = np.abs(stack - med) <= k * mad
    return np.where(keep, stack, 0).sum(axis=0) / np.maximum(keep.sum(axis=0), 1)


def masters(f):
    bias = sigma_clip_mean(f["bias"])
    dark = sigma_clip_mean(f["dark"]) - bias  # dark current + hot pixels for EXPTIME, bias removed
    flat = sigma_clip_mean(f["flat"])  # raw flat frames, combined
    flat = flat / np.median(flat)  # normalise to median 1
    return bias, dark, flat


def median3(img):
    p = np.pad(img, 1, mode="edge")
    win = np.lib.stride_tricks.sliding_window_view(p, (3, 3))
    return np.median(win, axis=(-2, -1))


def clean_cosmics(img, read_adu):
    """L.A.Cosmic idea, simplified: a cosmic ray is a SHARP outlier - far above its 3x3 median AND more than
    3x brighter (above sky) than the mean of its 4 neighbours. A star's PSF (FWHM 3 px) spreads light: its peak
    is only ~1.4x its neighbours, so stars survive."""
    med, sky = median3(img), np.median(img)
    p = np.pad(img, 1, mode="edge")
    neighbours = (p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]) / 4
    noise = np.sqrt(read_adu ** 2 + np.clip(img, 0, None) / camera.GAIN)  # read + photon noise per pixel, ADU
    hit = (img - med > CR_SIGMA * noise) & (img - sky > 3.0 * (neighbours - sky))
    return np.where(hit, neighbours, img), int(hit.sum())  # repair with the neighbours' mean (keeps star wings)


def photometry(img, x0, y0):
    """Aperture sum minus median sky from an annulus (photutils CircularAperture + CircularAnnulus)."""
    r = np.hypot(camera.XX - x0, camera.YY - y0)
    sky = np.median(img[(r >= ANN_IN) & (r < ANN_OUT)])
    ap = r < AP_R
    return float(img[ap].sum() - sky * ap.sum()), float(sky)


def run(seed=13, clean=True, log_path=HERE / "calib_log.jsonl"):
    f = camera.frames(seed)
    bias, dark, flat = masters(f)
    log = [{"step": "master_bias", "median_adu": round(float(np.median(bias)), 2)},
           {"step": "master_dark", "median_adu": round(float(np.median(dark)), 2), "max_adu": round(float(dark.max()), 1)},
           {"step": "master_flat", "min": round(float(flat.min()), 4), "max": round(float(flat.max()), 4)}]
    noise = camera.READ_E / camera.GAIN
    flux = []
    for i, raw in enumerate(f["light"]):
        sci = (raw - bias - dark) / flat
        n_cr = 0
        if clean:
            sci, n_cr = clean_cosmics(sci, noise)
        fl, sky = photometry(sci, camera.star_x(i), camera.Y_STAR)
        flux.append(fl)
        log.append({"frame": i, "x": round(camera.star_x(i), 2), "flux_adu": round(fl, 1), "sky_adu": round(sky, 2),
                    "cosmics_cleaned": n_cr})
    flux = np.array(flux)
    rel = flux / np.median(flux)
    expected = np.sqrt(camera.STAR_E) / camera.STAR_E  # photon-noise floor of a constant star (relative)
    robust = 1.4826 * np.median(np.abs(rel - np.median(rel)))  # one stray cosmic ray cannot fake a trend
    summary = {"rms_percent": round(100 * float(rel.std()), 3), "robust_rms_percent": round(100 * float(robust), 3),
               "expected_noise_percent": round(100 * expected, 3), "variable": bool(robust > 2 * expected)}
    log.append({"step": "light_curve", **summary})
    if log_path:
        Path(log_path).write_text("".join(json.dumps(x) + "\n" for x in log), encoding="utf-8")
    return rel, summary, flat


if __name__ == "__main__":
    rel, summary, flat = run()
    write_fits(HERE / "master_flat.fits", flat, [("OBJECT", "'master flat'")])
    print("relative flux, every 5th frame:", " ".join(f"{v:.4f}" for v in rel[::5]))
    print(json.dumps(summary))
    print("master_flat min/max:", round(float(flat.min()), 4), round(float(flat.max()), 4), "(true response 0.75/1.00)")
