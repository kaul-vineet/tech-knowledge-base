"""Processing step (astronomy): Gaia-like astrometry rows -> distance and absolute magnitude.
Rows come from astronomy L400 #21 inputs.rows() (SYNTHETIC values, real licence + credit texts); conversions from
astronomy L100 #4 units.py. Inverting a parallax is only honest when the fractional error is small: Bailer-Jones (2015)
shows it becomes non-trivial above ~20 %, so rows with parallax/error < 5 get distance null and method 'needs-prior'."""
import numpy as np

from _kb import INPUTS, UNITS

MIN_PARALLAX_SNR = 5.0  # = fractional parallax error <= 20 %


def rows_for(version: int, seed: int = 21) -> list:
    """Release v carries 12 + 4v rows (the catalogue grows); parallax errors are a separate seeded stream."""
    rows = INPUTS.rows(n=12 + 4 * version, seed=seed)
    err = np.random.default_rng(seed + 600).uniform(0.02, 0.6, len(rows))
    for r, e in zip(rows, err):
        r["parallax_error"] = round(float(e), 4)
    return rows


def process(rows: list) -> list:
    out = []
    for r in rows:
        snr = r["parallax"] / r["parallax_error"]
        rec = {"source_id": r["source_id"], "ra": r["ra"], "dec": r["dec"], "parallax_mas": r["parallax"],
               "parallax_error_mas": r["parallax_error"], "tmag": r["tmag"], "parallax_snr": snr}
        if snr >= MIN_PARALLAX_SNR:
            d = UNITS.parallax_distance_pc(r["parallax"] / 1000.0)  # mas -> arcsec -> pc (full double precision)
            rec.update(distance_pc=d, abs_mag_t=r["tmag"] - UNITS.distance_modulus(d), method="inverse-parallax")
        else:
            rec.update(distance_pc=None, abs_mag_t=None, method="needs-prior")
        out.append(rec)
    return out


def catalogue(version: int) -> dict:
    return {"columns": {"distance_pc": "pc", "abs_mag_t": "mag", "parallax_mas": "mas", "ra": "deg", "dec": "deg"},
            "min_parallax_snr": MIN_PARALLAX_SNR, "rows": process(rows_for(version))}
