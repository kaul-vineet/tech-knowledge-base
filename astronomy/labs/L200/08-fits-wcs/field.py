"""Synthetic, seeded star field for lesson 8 (not a real image)."""
import numpy as np


def synthetic_field(seed=8, n=64):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:n, 0:n]
    img = rng.normal(100.0, 5.0, (n, n))  # sky background + noise
    for x0, y0, f in zip(rng.uniform(5, n - 5, 12), rng.uniform(5, n - 5, 12), rng.uniform(500, 5000, 12)):
        img += f / (2 * np.pi * 1.5**2) * np.exp(-((xx - x0) ** 2 + (yy - y0) ** 2) / (2 * 1.5**2))
    return img.astype(np.float32)
