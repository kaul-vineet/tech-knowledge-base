# L200 research evidence — Astronomy & Astrophysics (applied)

Same method as L100-evidence.md (retrieved 2026-10-29). Numbers in the L200 notes are recomputed by `research/concept_examples_L200.py` (observed output: `concept_examples_L200_observed.txt`).

## Lesson 7 — Cross-matching
**Questions:** How do libraries match catalogues? How to avoid RA wrap-around and pole problems?

| Source | Decision | Score | Reason |
|---|---|---|---|
| Astropy (PyPI; `SkyCoord.match_to_catalog_sky` used in the CI equivalent) | kept | 10 | Reference implementation |
| SciPy `cKDTree` (PyPI page retrieved by this KB 2026-10-28) | kept (supporting) | 10 | Second reference in CI |
| TOPCAT home | kept | 10 | Pair match with Sky algorithm; CDS X-Match and cone search support |

**Key facts:** chord = 2 sin(θ/2) on the unit sphere (geometry, tested against brute force); Vincenty's formula is stable for small and large angles (tested: 90° exact, pole crossing 0.2°).

## Lesson 8 — FITS and WCS
| Source | Decision | Score | Reason |
|---|---|---|---|
| FITS Standard page (fits.gsfc.nasa.gov) | kept | 11 | Version 4.0 (language-edited 2018-08-13) is current; links the standard PDF |
| SAOImage DS9 download / release notes / Zenodo | kept | 10 | 8.8 (2026-10-01); 8.7 notes; GPL-3.0-only; Homebrew cask deprecated (fails Gatekeeper) |
| Calabretta & Greisen (2002) WCS paper II | not retrieved | — | TAN formulas are the standard gnomonic projection; CI compares with astropy.wcs (WCSLIB) |

**Key facts:** 2880-byte blocks (36 cards × 80 characters), big-endian data, NAXIS1 = fastest axis, FITS pixel (1, 1) = centre of the first pixel — implemented and checked by tests and, in CI, by astropy.io.fits `verify('exception')`.

## Lesson 9 — Aperture photometry
| Source | Decision | Score | Reason |
|---|---|---|---|
| PyPI photutils | kept | 10 | 3.1.1: aperture photometry, background estimation; CI equivalent |
| AstroImageJ releases / downloads | kept | 10 | 6.0.11.00 (2026-09-10) with macOS aarch64 .pkg and Windows x64 .msi; Sigstore-signed |
| CCD equation (Merline & Howell / Howell's Handbook) | not retrieved | — | Formula used is the standard form; noise-free and 3-sigma tests check consistency (KNOWN-GAPS) |

## Lesson 10 — Light curves
| Source | Decision | Score | Reason |
|---|---|---|---|
| VanderPlas (2018), arXiv:1703.09824 | kept | 11 | Practical guide; ApJS DOI 10.3847/1538-4365/aab766; aliasing, grid spacing, normalisation |
| Astropy LombScargle (PyPI; API in the CI equivalent) | kept | 10 | `fit_mean=False, center_data=True, normalization='standard'` = classical form |

**Key facts:** frequency grid spacing 1/(n_o × baseline) with oversampling n_o = 10 (the paper's grid discussion; exact recommended range not re-read); 1-day aliases at |f ± 1| c/d (observed: 1.3074 d vs predicted 1.3100 d).

## Lesson 11 — N-body
| Source | Decision | Score | Reason |
|---|---|---|---|
| PyPI rebound | kept | 10 | 5.2.2 (2026-10-05), GPL-3.0-or-later, integrators LEAPFROG, WHFast, IAS15; "runs natively on Linux, MacOS, and Windows" |
| JPL approximate elements | supporting | 12 | Semi-major axes for Earth/Jupiter in the initial conditions |

**Key facts:** G = 4π² in au³ yr⁻² M☉⁻¹ (Kepler's third law with P = 1 yr at a = 1 au); planet masses 3.003e-6 and 9.546e-4 M☉ are standard values (not re-fetched; illustrative initial conditions).
