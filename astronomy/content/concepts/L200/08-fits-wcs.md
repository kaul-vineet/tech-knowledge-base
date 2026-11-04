**Concept: FITS files and world coordinates**

## Why it matters
Telescope images, space-mission products and survey cut-outs arrive as FITS. To measure a star you must read the pixels correctly; to name it you must turn pixel (x, y) into RA/Dec. Both steps hide classic off-by-one and byte-order bugs.

## Mental model
A FITS file is a deck of 80-character cards followed by raw numbers, all in 2880-byte blocks. The WCS cards describe a flat tangent plane touching the sky at one reference point.

```
[header: cards ... END | pad to 2880] [data: big-endian numbers | pad to 2880]
pixel (x, y) ──minus CRPIX, times CD──> tangent plane (ξ, η) ──inverse gnomonic──> RA, Dec
```

## How it works
1. **Write and read in blocks.** Header cards are ASCII, 80 characters, ending with END; header and data are each padded to a multiple of 2880 bytes → see lab step 2.
2. **Respect byte order and axis order.** Data are big-endian; NAXIS1 is the number of columns, so numpy's shape is (NAXIS2, NAXIS1) → see lab step 3.
3. **Pixel to tangent plane.** Subtract CRPIX (1-based FITS pixels) and multiply by the CD matrix (degrees per pixel, including rotation) → see lab step 4.
4. **Tangent plane to sky.** The inverse gnomonic (TAN) projection maps (ξ, η) back onto the sphere around CRVAL → see lab steps 4 and 7.

**Worked example (lab run):** a 64 × 64 float32 image with 16 header cards plus END: 2880 header bytes + 16,384 data bytes padded to 17,280, so 20,160 bytes = 7 blocks. Pixel (32.5, 32.5) maps to CRVAL (83.822100, −5.391100); pixel (1, 1) to (83.830889, −5.399850). The brightest pixel, numpy [45, 51], is FITS pixel (52, 46).

## Trade-offs
| Approach | Use when | Avoid when |
|---|---|---|
| Hand-written reader | Learning, tiny images, no dependencies | Compressed or multi-extension files |
| astropy.io.fits + astropy.wcs | Real data, SIP distortion, all projections | — (the normal choice) |
| CD matrix | Rotated or skewed images | — |

## Common mistakes
- Treating numpy index 0 as FITS pixel 0: a 1-pixel (here 1″) shift.
- Reading data as little-endian: values become nonsense.
- Swapping NAXIS1 and NAXIS2.
