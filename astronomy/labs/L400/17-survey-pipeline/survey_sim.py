"""Seeded SYNTHETIC survey night for lesson 17: 48 raw 128 x 128 frames (float32 bytes, as a camera server sends
them), the master bias and flat, and the truth list of every star (frame, x, y, flux in e-).

Sky has a moonlight gradient (300 e- on the left edge to 900 e- on the right), the flat has 20 % vignetting.
"""
import numpy as np

SIZE, N_FRAMES, BIAS, GAIN, READ_E = 128, 48, 500.0, 1.0, 5.0
YY, XX = np.mgrid[0:SIZE, 0:SIZE].astype(float)
FLAT = 1.0 - 0.20 * (((XX - 63.5) ** 2 + (YY - 63.5) ** 2) / (2 * 63.5 ** 2))
SKY = 300.0 + 600.0 * XX / (SIZE - 1)
PSF_SIGMA = 1.3


def night(seed=17, n_frames=N_FRAMES):
    rng = np.random.default_rng(seed)
    raws, truth = [], []
    for f in range(n_frames):
        n = 40
        x, y = rng.uniform(6, SIZE - 6, n), rng.uniform(6, SIZE - 6, n)
        flux = 1500.0 * rng.uniform(0, 1, n) ** -0.8  # power law, brightest few 10^5 e-
        img = SKY.copy()
        for xi, yi, fi in zip(x, y, flux):
            img += fi * np.exp(-((XX - xi) ** 2 + (YY - yi) ** 2) / (2 * PSF_SIGMA ** 2)) / (2 * np.pi * PSF_SIGMA ** 2)
        e = rng.poisson(img * FLAT).astype(float) + rng.normal(0, READ_E, img.shape)
        raws.append((BIAS + e / GAIN).astype("<f4").tobytes())
        truth += [(f, float(a), float(b), float(c)) for a, b, c in zip(x, y, flux)]
    return raws, np.full((SIZE, SIZE), BIAS), FLAT.copy(), truth


def snr(flux, x):
    """Peak-pixel signal-to-noise of a star at column x (sky + read noise), used to define 'detectable'."""
    peak = flux / (2 * np.pi * PSF_SIGMA ** 2)
    sky = 300.0 + 600.0 * x / (SIZE - 1)
    return peak / np.sqrt(sky + READ_E ** 2)
