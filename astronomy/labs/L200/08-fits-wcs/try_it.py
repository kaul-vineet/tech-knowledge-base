"""tryIt experiments for lesson 8 (run: python try_it.py)."""
import math
import tempfile
from pathlib import Path

import fitslite as fl
from field import synthetic_field

# 1. Add 20 HISTORY-like cards. Predict: does the file grow? By how much?
with tempfile.TemporaryDirectory() as tmp:
    for n in (0, 20):
        p = Path(tmp) / f"t{n}.fits"
        fl.write_fits(p, synthetic_field(), {**fl.WCS, **{f"NOTE{i:03d}": i for i in range(n)}})
        print(f"{n:>2} extra cards: {p.stat().st_size} bytes")

# 2. Off-by-one: treat numpy index 0 as FITS pixel 0 instead of 1. Predict: how far off on the sky?
ra1, dec1 = fl.pixel_to_sky(fl.WCS, 1, 1)
ra0, dec0 = fl.pixel_to_sky(fl.WCS, 0, 0)
print(f"pixel (1,1) vs (0,0): dRA*cos(dec) = {(ra0 - ra1) * 3600 * math.cos(math.radians(dec1)):.3f} arcsec, dDec = {(dec0 - dec1) * 3600:.3f} arcsec")
