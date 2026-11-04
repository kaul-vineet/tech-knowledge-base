"""Minimal FITS image writer (2880-byte blocks, 80-character cards, big-endian float32) so DS9 or Siril can open
the lab's master frames. Not a general FITS library - use astropy.io.fits for real work."""
from pathlib import Path

import numpy as np


def write_fits(path, data, cards=()):
    data = np.asarray(data, dtype=">f4")
    header = [("SIMPLE", "T"), ("BITPIX", "-32"), ("NAXIS", "2"), ("NAXIS1", str(data.shape[1])),
              ("NAXIS2", str(data.shape[0]))] + list(cards)
    text = "".join(f"{k:<8}= {v:>20}".ljust(80) for k, v in header) + "END".ljust(80)
    text += " " * (-len(text) % 2880)
    raw = data.tobytes()  # FITS stores the first axis (x) fastest, as numpy row-major does
    Path(path).write_bytes(text.encode("ascii") + raw + b"\0" * (-len(raw) % 2880))
