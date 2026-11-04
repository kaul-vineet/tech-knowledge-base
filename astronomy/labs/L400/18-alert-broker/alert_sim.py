"""Seeded SYNTHETIC sky for lesson 18: a deep reference image and 8 nights x 2 exposures (20 min apart).

Truth (known to the tests, not to the broker):
  - a supernova appears at (40.0, 90.0) from night 3, brightening;
  - catalogued variable star V1 (a known variable) pulses +/- 0.5 mag;
  - an asteroid crosses the field: one dot per exposure, 4 px apart within a night;
  - a cosmic-ray hit in some exposures.
Seeing (PSF sigma 1.5-2.1 px) and transparency (flux x 0.75-1.0) change every night; the reference has
sigma 1.2 px and full transparency - so naive subtraction leaves a residual at EVERY star.
"""
import numpy as np

SIZE, SKY, READ = 128, 200.0, 5.0
YY, XX = np.mgrid[0:SIZE, 0:SIZE].astype(float)
REF_SIGMA = 1.2
SN_POS, VAR_INDEX = (40.0, 90.0), 5


def stars(seed=18):
    rng = np.random.default_rng(seed)
    x, y = rng.uniform(8, SIZE - 8, 50), rng.uniform(8, SIZE - 8, 50)
    flux = 3000.0 * rng.uniform(0, 1, 50) ** -0.7
    return x, y, flux


def known_variables():
    x, y, _ = stars()
    return [("V1", float(x[VAR_INDEX]), float(y[VAR_INDEX]))]


def render(points, sigma):
    img = np.full((SIZE, SIZE), SKY)
    for x, y, f in points:
        img += f * np.exp(-((XX - x) ** 2 + (YY - y) ** 2) / (2 * sigma ** 2)) / (2 * np.pi * sigma ** 2)
    return img


def reference(seed=18):
    x, y, f = stars(seed)
    rng = np.random.default_rng(seed + 1)
    img = render(zip(x, y, f), REF_SIGMA)
    return img + rng.normal(0, np.sqrt(img / 16 + READ ** 2 / 16))  # deep: 16 stacked exposures


def nights(seed=18, n=8):
    """Yields dicts: night, exposure ('a'/'b'), mjd, sigma, image."""
    x, y, f = stars(seed)
    rng = np.random.default_rng(seed + 2)
    out = []
    for night in range(n):
        sigma, transp = rng.uniform(1.5, 2.1), rng.uniform(0.75, 1.0)
        ff = f.copy()
        ff[VAR_INDEX] *= 10 ** (-0.4 * 0.5 * np.sin(2 * np.pi * night / 3.0))  # known variable
        for k, expo in enumerate("ab"):
            pts = list(zip(x, y, ff * transp))
            if night >= 3:  # supernova rises from night 3
                pts.append((SN_POS[0], SN_POS[1], transp * 4000.0 * (night - 2)))
            ax, ay = 20.0 + 11.0 * night + 4.0 * k, 25.0 + 9.0 * night + 1.0 * k  # asteroid, 4.1 px per 20 min
            pts.append((ax, ay, transp * 6000.0))
            img = render(pts, sigma)
            img = rng.poisson(img).astype(float) + rng.normal(0, READ, img.shape)
            if (night + k) % 3 == 0:  # cosmic ray
                cy, cx = rng.integers(10, SIZE - 10, 2)
                img[cy, cx] += 3000.0
            out.append({"night": night, "exposure": expo, "mjd": 61400.0 + night + k * 20 / 1440, "sigma": sigma,
                        "image": img, "truth_asteroid": (ax, ay)})
    return out
