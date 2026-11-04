"""Build-task SOLUTION. L200 Aperture photometry: synthetic star field, circular aperture, background annulus, CCD-equation SNR.

Synthetic and seeded (not a real image): 101x101 pixels, gain 1 e-/ADU, sky 100 e-/pixel, read noise 5 e-,
Gaussian PSF sigma 1.5 px, five stars with known fluxes. Exposure 60 s.
python photometry.py            # add --export to write field.fits for AstroImageJ / DS9
"""
import sys

import numpy as np

SKY, READ_NOISE, SIGMA, EXPTIME = 100.0, 5.0, 1.5, 60.0
STARS = [(30.0, 30.0, 20000.0), (70.0, 30.0, 8000.0), (50.0, 50.0, 3000.0), (30.0, 72.0, 1000.0), (72.0, 70.0, 300.0)]


def make_image(seed=9, n=101):
    yy, xx = np.mgrid[0:n, 0:n]
    model = np.full((n, n), SKY)
    for x0, y0, flux in STARS:
        model += flux / (2 * np.pi * SIGMA**2) * np.exp(-((xx - x0) ** 2 + (yy - y0) ** 2) / (2 * SIGMA**2))
    rng = np.random.default_rng(seed)
    return rng.poisson(model) + rng.normal(0.0, READ_NOISE, (n, n))  # photon (Poisson) noise + read noise


def aperture_weights(shape, x0, y0, r, sub=5):
    """Fraction of each pixel inside a circle, by sub-sampling each pixel sub x sub times."""
    off = (np.arange(sub) + 0.5) / sub - 0.5
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    w = np.zeros(shape)
    for dy in off:
        for dx in off:
            w += ((xx + dx - x0) ** 2 + (yy + dy - y0) ** 2 <= r * r)
    return w / sub**2


def measure(img, x0, y0, r=6.0, r_in=10.0, r_out=15.0):
    w = aperture_weights(img.shape, x0, y0, r)
    npix = w.sum()
    yy, xx = np.mgrid[0:img.shape[0], 0:img.shape[1]]
    d2 = (xx - x0) ** 2 + (yy - y0) ** 2
    ring = img[(d2 >= r_in**2) & (d2 <= r_out**2)]
    bkg = np.median(ring)  # median: robust against a neighbour star in the annulus
    net = (w * img).sum() - npix * bkg  # aperture sum minus the sky expected under the aperture
    noise = np.sqrt(max(net, 0) + npix * (1 + npix / ring.size) * (bkg + READ_NOISE**2))  # CCD equation
    return {"net": net, "bkg": bkg, "npix": npix, "snr": net / noise}


def calibrate(results, ref_index, ref_mag):
    """Build task (solution): calibrated magnitude and 1-sigma error for every star, from one reference star."""
    inst = [-2.5 * np.log10(r["net"] / EXPTIME) if r["net"] > 0 else np.nan for r in results]  # instrumental mag
    zero_point = ref_mag - inst[ref_index]
    return [(m + zero_point, 2.5 / np.log(10) / r["snr"] if r["snr"] > 0 else np.nan)  # sigma_m = 1.0857 / SNR
            for m, r in zip(inst, results)]


def write_fits(path, img):
    cards = [f"{'SIMPLE':<8}= {'T':>20}", f"{'BITPIX':<8}= {-32:>20}", f"{'NAXIS':<8}= {2:>20}",
             f"{'NAXIS1':<8}= {img.shape[1]:>20}", f"{'NAXIS2':<8}= {img.shape[0]:>20}", "END"]
    head = "".join(c.ljust(80) for c in cards).encode("ascii")
    data = img.astype(">f4").tobytes()
    with open(path, "wb") as f:
        f.write(head + b" " * (-len(head) % 2880) + data + b"\0" * (-len(data) % 2880))


def main():
    img = make_image()
    print("star  true(e-)  measured(e-)  ratio   sky/px  SNR")
    results = []
    for i, (x, y, flux) in enumerate(STARS):
        m = measure(img, x, y)
        results.append(m)
        print(f"{i:>4} {flux:9.0f} {m['net']:13.1f} {m['net'] / flux:6.3f} {m['bkg']:8.2f} {m['snr']:6.1f}")
    for i, (mag, err) in enumerate(calibrate(results, 0, 10.0)):
        print(f"star {i}: V = {mag:6.3f} +/- {err:.3f} (reference: star 0 = 10.000)")
    print(f"aperture r=6 px holds {1 - np.exp(-36 / (2 * SIGMA**2)):.5f} of a star's light (Gaussian PSF)")
    if "--export" in sys.argv:
        write_fits("field.fits", img)  # FITS pixel = numpy index + 1: star 0 is at FITS (31, 31)
        print("wrote field.fits")


if __name__ == "__main__":
    main()
