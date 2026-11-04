"""L200 FITS images and WCS: a minimal FITS writer/reader (2880-byte blocks) and a TAN (gnomonic) WCS.

python fitslite.py      # writes star_field.fits (synthetic, seeded), reads it back, converts pixels to sky
Pixel convention: FITS pixel (1, 1) is the CENTRE of the first pixel; numpy index [0, 0] is the same pixel.
"""
from pathlib import Path

import numpy as np

from field import synthetic_field

BLOCK = 2880  # every FITS header and data unit is padded to a multiple of 2880 bytes (36 cards x 80 chars)
DTYPES = {8: ">u1", 16: ">i2", 32: ">i4", -32: ">f4", -64: ">f8"}  # BITPIX -> big-endian numpy dtype


def card(key, value):
    if isinstance(value, str):
        return f"{key:<8}= '{value:<8}'".ljust(80)  # strings: quote in column 11, at least 8 characters
    v = "T" if value is True else repr(value)
    return f"{key:<8}= {v:>20}".ljust(80)  # fixed format: keyword in columns 1-8, '= ' in 9-10, value ends col 30


def write_fits(path, data, extra):
    data = np.asarray(data)
    bitpix = {v: k for k, v in DTYPES.items()}[data.dtype.newbyteorder(">").str]
    cards = [card("SIMPLE", True), card("BITPIX", bitpix), card("NAXIS", data.ndim)]
    cards += [card(f"NAXIS{i + 1}", n) for i, n in enumerate(data.shape[::-1])]  # NAXIS1 = columns (fastest axis)
    cards += [card(k, v) for k, v in extra.items()] + ["END".ljust(80)]
    header = "".join(cards).encode("ascii")
    raw = data.astype(DTYPES[bitpix]).tobytes()
    with open(path, "wb") as f:
        f.write(header + b" " * (-len(header) % BLOCK))  # header padded with spaces
        f.write(raw + b"\0" * (-len(raw) % BLOCK))  # data padded with zeros


def parse_value(text):
    text = text.split("/")[0].strip() if not text.strip().startswith("'") else text.strip()
    if text.startswith("'"):
        return text[1:text.index("'", 1)].rstrip()
    if text in ("T", "F"):
        return text == "T"
    return float(text) if any(c in text for c in ".EeDd") else int(text)


def read_fits(path):
    raw = Path(path).read_bytes()
    header, pos = {}, 0
    while True:
        block = raw[pos:pos + BLOCK].decode("ascii")
        pos += BLOCK
        for i in range(0, BLOCK, 80):
            key, rest = block[i:i + 8].strip(), block[i + 8:i + 80]
            if key == "END":
                shape = [header[f"NAXIS{n}"] for n in range(header["NAXIS"], 0, -1)]
                count = int(np.prod(shape))
                data = np.frombuffer(raw, DTYPES[header["BITPIX"]], count, pos).reshape(shape)
                return header, data.astype(data.dtype.newbyteorder("="))
            if rest.startswith("= "):
                header[key] = parse_value(rest[2:])


def pixel_to_sky(h, x, y):
    """FITS pixel (1-based) -> (RA, Dec) degrees for CTYPE RA---TAN / DEC--TAN with a CD matrix."""
    dx, dy = np.asarray(x, float) - h["CRPIX1"], np.asarray(y, float) - h["CRPIX2"]
    xi = np.radians(h["CD1_1"] * dx + h["CD1_2"] * dy)  # intermediate world coordinates (standard coords)
    eta = np.radians(h["CD2_1"] * dx + h["CD2_2"] * dy)
    ra0, dec0 = np.radians(h["CRVAL1"]), np.radians(h["CRVAL2"])
    den = np.cos(dec0) - eta * np.sin(dec0)  # inverse gnomonic projection: the tangent plane back onto the sphere
    ra = ra0 + np.arctan2(xi, den)
    dec = np.arctan2(eta * np.cos(dec0) + np.sin(dec0), np.hypot(xi, den))
    return np.degrees(ra) % 360, np.degrees(dec)


def sky_to_pixel(h, ra, dec):
    raise NotImplementedError("build task: invert pixel_to_sky (gnomonic projection, then the inverse CD matrix)")


WCS = {"CTYPE1": "RA---TAN", "CTYPE2": "DEC--TAN", "CRPIX1": 32.5, "CRPIX2": 32.5, "CRVAL1": 83.8221,
       "CRVAL2": -5.3911, "CD1_1": -2.7778e-4, "CD1_2": 0.0, "CD2_1": 0.0, "CD2_2": 2.7778e-4, "BUNIT": "adu"}


def main():
    path = Path("star_field.fits")
    write_fits(path, synthetic_field(), WCS)
    size = path.stat().st_size
    h, data = read_fits(path)
    print(f"wrote {path} ({size} bytes = {size // BLOCK} blocks of {BLOCK}); header cards: {len(h) + 1} incl. END")
    print(f"read back: shape {data.shape}, dtype {data.dtype}, identical: {np.array_equal(data, synthetic_field())}")
    for x, y in ((32.5, 32.5), (1, 1), (64, 64)):
        ra, dec = pixel_to_sky(h, x, y)
        print(f"pixel ({x:>4}, {y:>4}) -> RA {ra:.6f} Dec {dec:+.6f}")
    row, col = (int(i) for i in np.unravel_index(np.argmax(data), data.shape))
    print(f"brightest pixel: numpy [row {row}, col {col}] = FITS pixel ({col + 1}, {row + 1})")


if __name__ == "__main__":
    main()
