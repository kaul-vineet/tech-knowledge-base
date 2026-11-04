# L100 research evidence — Astronomy & Astrophysics (applied)

Method: SPEC.md research method. Sources retrieved 2026-10-29 with web_fetch / web_search unless marked. Score = implementable / current / authoritative / open / transferable / depth (0-2 each); keep ≥ 8/12. Numbers in concept notes and the primer are recomputed by `research/concept_examples_L100.py` (observed output: `concept_examples_L100_observed.txt`).

---

## Lesson 1 — Workbench
**Questions:** Which versions of Astropy, Skyfield, photutils (and REBOUND for L200) are current, with macOS arm64 and Windows wheels? Which sky simulator is open source and installable on both machines?

| Source | Decision | Score | Reason |
|---|---|---|---|
| PyPI astropy | kept | 11 | 8.0.2, 2026-10-15, BSD-3-Clause, Python ≥ 3.11; wheels macOS 11+ ARM64, Windows x86-64 and ARM64 |
| PyPI skyfield | kept | 10 | 1.55, 2026-08-07, MIT, `py3-none-any` wheel; README shows `load('de421.bsp')` |
| PyPI photutils | kept | 10 | 3.1.1, 2026-10-16, BSD-3-Clause, Python ≥ 3.12, macOS ARM64 + Windows wheels |
| stellarium.org + Homebrew cask API | kept | 10 | Site lists 26.3 (macOS 11+ universal; Windows x86_64 Qt6; Windows ARM64); cask `stellarium` at 26.2 |
| PyPI scipy, numpy, Python/winget/brew pages | supporting | — | Retrieved by this KB on 2026-10-28 (shared WORKSTATION-SETUP, simulation topic); not re-fetched |

**Key facts:** astropy 8.0.2 requires Python ≥ 3.11 (https://pypi.org/project/astropy/); photutils 3.1.1 requires ≥ 3.12 (https://pypi.org/project/photutils/); Stellarium system requirements: OpenGL 3.3 recommended, 2.1 minimum (https://stellarium.org/).

## Lesson 2 — Coordinates
**Questions:** How do I get local sidereal time from a UTC timestamp? What accuracy does the simple J2000 transform give?

| Source | Decision | Score | Reason |
|---|---|---|---|
| USNO "Computing Approximate Sidereal Time" | kept | 11 | GMST = 18.697375 + 24.065709824279 D (h); ~0.1 s accuracy; local = + longitude/15 |
| whiz.tools / airmass.org / calculator sites (search results) | dropped | ≤ 6 | Secondary calculators; airmass.org is useful background but not authoritative |
| SIMBAD star positions | not retrieved | — | Script queries returned no text; positions used are approximate SIMBAD-listed J2000 values (KNOWN-GAPS) |

**Key facts:** altitude/azimuth formulas are standard spherical trigonometry (cross-checked in CI against Astropy AltAz). Precession since J2000 is ~0.37° (≈50″/yr: Wallace & Capitaine 2006 eq. 4 gives the IAU 2006 precession angle ψ̄ ≈ 5038.48″ t per century; the lab ignores it and says so in the README and lesson overview) — the reason for the 0.6° CI tolerance.

## Lesson 3 — Time systems
**Questions:** What is TAI−UTC today and when does the table expire? Which official value or formula can a sidereal-time function be checked against?

| Source | Decision | Score | Reason |
|---|---|---|---|
| IERS Bulletin C 72 | kept | 12 | UTC−TAI = −37 s from 2017-01-01; no leap second at end of December 2026 |
| IERS Leap_Second.dat | kept | 12 | Full TAI−UTC table from 1972; "File expires on 28 June 2027" |
| USNO sidereal time page (aa.usno.navy.mil/faq/GAST) | kept | 11 | Short and full GMST formulas, "adapted from those given in section 2.6.2 of USNO Circular No. 179 (2005)"; short form: "loss of precision of 0.1 second per century"; GMST at 0h UT1 "is tabulated in The Astronomical Almanac"; max equation of the equinoxes ~1.1 s |
| Wallace & Capitaine 2006, A&A 459, 981 (syrte.obspm.fr/iau2006/aa06_459.IAU06prec.pdf) | kept (primary) | 12 | Appendix worked example: UTC 2006 January 15 21h24m37.5s, UT1−UTC = +0.3341 s, UT1 = 2400000.5 + 53750.892104561342593, TT = 2400000.5 + 53750.892855138888889 → ERA 76.265431053522° = 5h05m03.703452845s; EO −277.646996035″; GST 05h05m22.213252581s. Same paper gives ERA eq. (3) and says SOFA-style procedures derive GST from ERA and EO |
| IERS Conventions (2010), Chapter 5 (icc5.pdf) | kept | 12 | Eq. 5.14: ERA(Tu) = 2π(0.7790572732640 + 1.00273781191135448 Tu), Tu = JD(UT1) − 2451545.0 |
| Swiss Ephemeris 1987 tables (astro.com, astrology publisher) | **dropped (2026-10-29 review)** | — | Replaced by the official USNO and IERS formulas above; not a primary source |
| SOFA cookbook (sofa_pn_c.pdf), USNO Circular 179 PDF, ERFA test file | tried | — | Fetches returned only the tables of contents (or nothing), so no SOFA test value or GMST−ERA (eq. 5.32) polynomial is quoted |

**Key facts:** TT = TAI + 32.184 s (definition, also used by USNO); J2000.0 = 2000-01-01 12:00 TT → 11:58:55.816 UTC (computed: 32 + 32.184 s); lab ERA = published ERA to 0.00001 s and GMST + USNO equation of the equinoxes = published GST to 0.023 s (Wallace & Capitaine 2006 example); our short GMST agrees with USNO's full formula to 0.002–0.010 s on four dates (1987-01-01, J2000.0, 2026-10-29 0h and 15:30 UTC) and equals the IERS ERA at J2000.0 to 0.0016 s (rounding of 18.697375 h) (tests).

## Lesson 4 — Units and magnitudes
**Questions:** Exact definitions of au, pc, ly; magnitude/flux relation.

| Source | Decision | Score | Reason |
|---|---|---|---|
| Astropy units (PyPI page; API used in `units_astropy.py`) | kept | 10 | Reference implementation for the CI cross-check |
| IAU 2012 B2 / 2015 B2 resolutions | not retrieved | — | Values (au = 149 597 870 700 m; pc = 648000/π au) are definitions; resolution PDFs not fetched (KNOWN-GAPS) |

## Lesson 5 — Orbits
**Questions:** Which approximate elements are official, valid when, and how accurate? How should Kepler's equation be solved?

| Source | Decision | Score | Reason |
|---|---|---|---|
| JPL SSD "Approximate Positions of the Planets" | kept | 12 | Table 1 elements + rates (1800-2050), algorithm, Newton iteration with E0 = M + e* sin M, tol 1e-6°, Mars error 40″/2″/25,000 km |
| JPL Horizons API | not retrieved | — | API URL returned no text; Skyfield + DE421 in CI is the reference instead |

**Key facts:** Mars 2026-10-29 0h TDB: RA 139.6593°, Dec +17.2889°, 1.4567 au (lab); closest approach 0.6778 au on 2027-02-20 (tryIt).

## Lesson 6 — Light and spectra
| Source | Decision | Score | Reason |
|---|---|---|---|
| NIST CODATA Wien constant | kept | 12 | b = 2.897 771 955… × 10⁻³ m K (exact) |
| Astropy BlackBody (via PyPI/API) | kept | 10 | CI cross-check |

**Key facts:** h, c, k are exact SI values (2019 redefinition; NIST pages for h, k not re-fetched); σ = 5.670374419e-8 (CODATA, not re-fetched); the numerical Planck peak equals b/T to 4 decimals (test).
