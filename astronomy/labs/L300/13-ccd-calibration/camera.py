"""Seeded synthetic CCD (SYNTHETIC data, not a real camera): bias, dark, flat and light frames for lesson 13.

64 x 64 pixels. Truth is known: bias 1000 ADU, gain 1.5 e-/ADU, read noise 7 e-, dark 0.05 e-/s (+ 8 hot pixels),
flat response = vignetting (-25% in the corners) x a dust donut (-12%), sky 200 e-, and one CONSTANT star that
drifts from x = 12 to x = 52 across 30 frames (poor tracking) - right through the vignetting and the donut.
Cosmic rays hit darks and lights (a seeded one lands inside the star's aperture on frame 17).
"""
import numpy as np

N, BIAS, GAIN, READ_E, DARK_E_S, EXPTIME = 64, 1000.0, 1.5, 7.0, 0.05, 60.0
SKY_E, STAR_E, FWHM, FLAT_E = 200.0, 200_000.0, 3.0, 6000.0
N_FRAMES, Y_STAR = 30, 32.0
YY, XX = np.mgrid[0:N, 0:N].astype(float)


def response():
    """True pixel response (flat field): vignetting x dust donut, mean ~0.9."""
    r2 = ((XX - 31.5) ** 2 + (YY - 31.5) ** 2) / (2 * 31.5 ** 2)
    ring = np.exp(-0.5 * ((np.hypot(XX - 40, YY - 32) - 5.0) / 1.5) ** 2)
    return (1 - 0.25 * r2) * (1 - 0.12 * ring)


def star_x(i):
    return 12.0 + 40.0 * i / (N_FRAMES - 1)


def star_image(x0, y0, flux):
    s = FWHM / 2.3548
    return flux * np.exp(-((XX - x0) ** 2 + (YY - y0) ** 2) / (2 * s * s)) / (2 * np.pi * s * s)


def hot_pixels(rng):
    hot = np.zeros((N, N))
    hot[rng.integers(0, N, 8), rng.integers(0, N, 8)] = 5.0  # e-/s
    return hot


def cosmic_rays(rng, n, img):
    for _ in range(n):
        y, x = rng.integers(2, N - 2, 2)
        img[y, x] += rng.uniform(2000, 20000)
    return img


def expose(rng, electrons):
    """Electrons -> ADU with Poisson + read noise on top of the bias level."""
    e = rng.poisson(np.clip(electrons, 0, None)).astype(float) + rng.normal(0, READ_E, (N, N))
    return BIAS + e / GAIN


def frames(seed=13):
    rng = np.random.default_rng(seed)
    hot, resp = hot_pixels(rng), response()
    bias = [expose(rng, np.zeros((N, N))) for _ in range(10)]
    dark = [expose(rng, cosmic_rays(rng, 3, (DARK_E_S + hot) * EXPTIME)) for _ in range(10)]
    flat = [expose(rng, FLAT_E * resp) for _ in range(10)]  # short twilight flats: dark current negligible
    light = []
    for i in range(N_FRAMES):
        e = (DARK_E_S + hot) * EXPTIME + resp * (SKY_E + star_image(star_x(i), Y_STAR, STAR_E))
        e = cosmic_rays(rng, 3, e)
        if i == 17:  # seeded hit inside the aperture
            e[int(Y_STAR) + 1, int(round(star_x(i))) + 1] += 30000.0
        light.append(expose(rng, e))
    return {"bias": np.array(bias), "dark": np.array(dark), "flat": np.array(flat), "light": np.array(light)}
