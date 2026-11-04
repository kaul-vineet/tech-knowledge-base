# L300 research evidence — Astronomy & Astrophysics (applied), lessons 12–16

Method: SPEC.md research method. Sources were retrieved on 2026-10-29 with web_fetch, directly or by a research sub-agent; anything read only from a search result is marked. Each source is scored 0–2 on six criteria (implementable / current / authoritative / open / transferable / depth) and kept at ≥ 8/12. Civilian and scientific scope only. Every number in the L300 concept notes comes from a lab run; the outputs are pasted in each lab README, rendered from real runs. Fail-before / pass-after evidence: each lab's `test_build_task.py` with `BUILD_TARGET=mine` (shipped, unfixed file) against the default (solution). The results are listed under each lesson.

PyPI pins checked on 2026-10-29 (pypi.org project pages):

| package | version | released | licence | wheels |
|---|---|---|---|---|
| numpy | 2.5.3 | (KB-wide pin) | BSD-3-Clause | macOS arm64 and Windows x64 wheels |
| astropy | 8.0.2 | 2026-10-15 | BSD-3-Clause | macOS arm64 and Windows x64 wheels |
| astroplan | 0.10.1 | 2024-08-13 | BSD-3 | sdist only. **Last release about 26 months ago** (KNOWN-GAPS) |
| ccdproc | 2.5.1 | 2025-07-05 | BSD-3-Clause | pure Python |
| astroscrappy | 1.3.0 | 2025-10-31 | BSD-3-Clause | macOS arm64 and Windows x64 wheels |
| emcee | 3.1.6 | 2024-04-19 | MIT | pure Python |
| joblib | 1.6.0 | 2026-08-31 | BSD-3-Clause | pure Python, Python ≥ 3.10 |

---

## Lesson 12 — Observation planning
**Questions**
1. Which low-precision formulas for the Sun, the Moon and sidereal time are good enough for planning, and what accuracy do their authors state?
2. How are twilight and airmass defined, and where does sec z break down?
3. How does astroplan express the same constraints and schedulers?

| Source | URL | Decision | Score | Reason / key facts |
|---|---|---|---|---|
| USNO, Computing Approximate Solar Coordinates | https://aa.usno.navy.mil/faq/sun_approx | kept | 11 | g, q, L, e formulas; RA in the same quadrant as L; "about 1 arcminute within two centuries of 2000" |
| USNO, Computing Approximate Sidereal Time | https://aa.usno.navy.mil/faq/GAST | kept | 11 | GMST = 6.697375 + 0.065709824279 D0 + 1.0027379 H + 0.0000258 T² h. Test: GMST(J2000.0) = 18.697375 h |
| USNO, Rise, Set and Twilight Definitions | https://aa.usno.navy.mil/faq/RST_defs | kept | 10 | Twilight Sun altitudes −6, −12, −18° |
| P. Schlyter, How to compute planetary positions | https://www.stjarnhimlen.se/comp/ppcomp.html | kept | 9 | Moon elements and the 12 + 5 largest perturbations (all coefficients used in `ephem.py`); "1-2 arc minutes"; topocentric alt_topo = alt_geo − mpar cos alt |
| astroplan constraints (AltitudeConstraint, AirmassConstraint, AtNightConstraint, MoonSeparationConstraint) | https://astroplan.readthedocs.io/en/stable/api/astroplan.AirmassConstraint.html (and the sibling pages) | kept | 10 | `AirmassConstraint(max=None, min=1)`: "airmass is approximated by the secant of the zenith angle"; `twilight_astronomical` = −18° |
| astroplan Scheduling tutorial | https://astroplan.readthedocs.io/en/stable/tutorials/scheduling.html | kept | 9 | SequentialScheduler fills time in order; Transitioner |
| SIMBAD (8 stars, van Leeuwen 2007 Hipparcos) | https://simbad.cds.unistra.fr/simbad/sim-id?Ident=Vega (and the other 7) | kept | 10 | J2000 RA/Dec used in `TARGETS` (converted to degrees) |
| Kasten & Young 1989, Applied Optics 28, 4735 (full text, archive.org scholarly-sources copy; DOI 10.1364/AO.28.004735) | https://archive.org/download/wikipedia-scholarly-sources-corpus/10.1364%252FAO.1.000024.zip/10.1364%252FAO.28.004735.pdf | **kept (primary, 2026-10-29 review)** | 11 | Eq. 3 f(γ) = [sin γ + a(γ + b)^−c]^−1 with revised a = 0.50572, b = 6.07995°, c = 1.6364; Table II relative air mass (ISO 2533 atmosphere), e.g. 38.0868 at 0°, 5.5841 at 10°, 1.9939 at 30°; "maximum relative error of the approximating formula is now <0.5%"; argument is apparent elevation (Young's warning). The lab's solution now uses this formula and tests nine table rows |
| Wikipedia, Air mass (astronomy) | https://en.wikipedia.org/wiki/Air_mass_%28astronomy%29 | dropped (2026-10-29 review) | 6 | Was the only source of the Pickering (2002) formula; replaced by Kasten & Young 1989. Pickering's DIO 12 paper (dioi.org/jc01.pdf) was found, but its airmass footnote (fn 39) lies beyond the fetchable part |

**Key facts checked by code:** GMST(J2000.0) = 18.697375 h (`test_gmst_at_j2000_matches_usno_formula`); the Sun's declination at the June solstice is 23.436° (obliquity); the night of 2026-11-24 is a full Moon (elongation > 170°); Aldebaran is less than 30° from the Moon.
**Failure proof:** with `BUILD_TARGET=mine` the shipped file fails 2/3 tests (15 subtest failures); the solution passes 3/3.

## Lesson 13 — CCD calibration
**Questions**
1. In what order are bias, dark and flat applied, and how are the masters combined?
2. How does L.A.Cosmic separate cosmic rays from stars?
3. Which ccdproc calls correspond to each step?

| Source | URL | Decision | Score | Reason / key facts |
|---|---|---|---|---|
| astropy CCD Data Reduction Guide | https://github.com/astropy/ccd-reduction-and-photometry-guide | kept | 11 | BSD-3; the standard open guide (Craig & Chambers) |
| ccdproc API: subtract_bias, subtract_dark, flat_correct, Combiner, cosmicray_lacosmic | https://ccdproc.readthedocs.io/en/latest/api/ccdproc.Combiner.html (and siblings) | kept | 11 | sigma_clipping(3, 3); median uncertainty 1.4826 × MAD; flat "normalized by its mean or a user-supplied value"; lacosmic defaults (sigclip 4.5, …) |
| van Dokkum 2001, L.A.Cosmic, PASP 113, 1420 | https://arxiv.org/abs/astro-ph/0108003 | kept | 10 | Laplacian edge detection; fine-structure image; "222 of the 227 cosmic-rays (98 %)" |
| Siril 1.4.4 docs, Calibration | https://siril.readthedocs.io/en/stable/preprocessing/calibration.html | kept | 9 | Calibration formula "Lc = (L − D)/(F − O)" (the build-task hint); flats ≤ 80 % of full well |
| Siril download page | https://siril.org/download/ | kept (tool) | 9 | 1.4.5 released 2026-10-28; GPL-3.0 (gitlab.com/free-astro/siril) |

**Failure proof:** with `BUILD_TARGET=mine` the shipped file fails 3/3 tests (12 failures including the seed subtests); the solution passes. Shipped robust rms 0.899 % (variable), fixed 0.382 %. Over seeds 13–29, the fixed robust rms is at most 0.382 % and the shipped one at least 0.665 %. That separation chose the 2 × photon-floor (0.448 %) threshold.

## Lesson 14 — Plate solving
**Questions**
1. How do blind solvers turn star patterns into hypotheses, and how do they verify them?
2. What is the TAN projection exactly, and how is a WCS fitted to matched stars?

| Source | URL | Decision | Score | Reason / key facts |
|---|---|---|---|---|
| Lang et al. 2010, Astrometry.net, AJ 139, 1782 | https://arxiv.org/abs/0910.2233 | kept | 11 | Geometric hashing of 4–5-star asterisms; Bayesian verification; 99.9 % success rate, no false positives |
| Calabretta & Greisen 2002, WCS Paper II | https://arxiv.org/abs/astro-ph/0207413 | kept | 11 | Zenithal projections; TAN = gnomonic (Rθ = (180/π) cot θ, **derived** from eq. 16 with μ = 0; §5.1.3 was truncated in the fetch) |
| astropy `fit_wcs_from_points` | https://docs.astropy.org/en/stable/api/astropy.wcs.utils.fit_wcs_from_points.html | kept | 10 | Signature and FITS 1-based pixel note (used in `platesolve_astropy.py`) |
| Beroiz, Cabral & Sanchez 2020, astroalign | https://arxiv.org/abs/1909.02946 | kept | 10 | Invariant (L2/L1, L1/L0); RANSAC; brightest 50; MIT licence |
| astrometry.net code and packages | https://astrometry.net/use.html | kept (tool) | 9 | "Debian or Ubuntu: apt install astrometry.net / MacOS Homebrew: brew install astrometry-net / Windows: it should work in WSL" |
| Homebrew formula astrometry-net | https://formulae.brew.sh/formula/astrometry-net | kept (tool) | 9 | 0.97, Apple Silicon bottles; listed as BSD-3-Clause, but the repo README says the whole work is GPL-3.0-or-later |

**Key facts checked by code:** TAN round trip to 1e-10°; ξ/ΔRA = cos 62° at the tangent point; invariants unchanged under rotation, scale and mirror (`test_platesolve.py`).
**Failure proof:** with `BUILD_TARGET=mine`, 2/2 tests fail (3 subtests); the solution passes.

## Lesson 15 — Honest uncertainty
**Questions**
1. When is (JᵀWJ)⁻¹ the right covariance, and what does χ²_red tell you?
2. How do you check convergence of an MCMC run, and what does emcee recommend?

| Source | URL | Decision | Score | Reason / key facts |
|---|---|---|---|---|
| Hogg, Bovy & Lang 2010, Fitting a model to data | https://arxiv.org/abs/1008.4686 | kept | 11 | Weighted least squares assumes "Gaussians of known variance"; generative model |
| Hogg & Foreman-Mackey 2018, Using MCMC | https://arxiv.org/abs/1710.06068 | kept | 11 | "autocorrelation time is the most important test for convergence" |
| Foreman-Mackey et al. 2013, emcee | https://arxiv.org/abs/1202.3665 | kept | 11 | Stretch move; acceptance 0.2–0.5 |
| emcee docs: Autocorrelation analysis | https://emcee.readthedocs.io/en/stable/tutorials/autocorr/ | kept | 10 | Window M ≥ 5τ; "chains longer than about 50τ are often sufficient" (tryIt 2) |
| Seager & Mallén-Ornelas 2003 | https://arxiv.org/abs/astro-ph/0206228 | kept | 10 | ΔF = (Rp/R*)²; tT and tF contacts. The trapezoid wording is ours |
| NIST/SEMATECH e-Handbook, Bootstrap plot | https://www.itl.nist.gov/div898/handbook/eda/section3/bootplot.htm | kept | 9 | Resampling with replacement, 500–1000 samples (we use 300 for runtime; noted) |

**Failure proof:** with `BUILD_TARGET=mine` the shipped file fails 2/2 (coverage 0.36 / 0.335 / 0.275 / 0.22; formal/bootstrap ratio 0.45–0.48); the solution passes (0.73 / 0.615 / 0.555 / 0.56).

## Lesson 16 — Reproducible pipelines
**Questions**
1. What should a provenance record contain, according to a standard?
2. How do common caching libraries form their keys, and where do they go stale?

| Source | URL | Decision | Score | Reason / key facts |
|---|---|---|---|---|
| W3C PROV-DM (REC 2013-04-30) | https://www.w3.org/TR/prov-dm/ | kept | 11 | Entity, Activity, Agent; used, wasGeneratedBy, wasDerivedFrom |
| IVOA Provenance Data Model 1.0 (HAL copy of the REC) | https://hal.science/hal-03433754/document | kept | 9 | Built on W3C PROV; "An entity can be generated by only one activity". ivoa.net itself was blocked |
| Sandve et al. 2013, Ten Simple Rules for Reproducible Computational Research | https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003285 | kept | 10 | Rules 1 (track how results were produced), 3 (archive exact versions), 6 (note seeds) |
| joblib Memory user guide (v1.6.0) | https://joblib.readthedocs.io/en/stable/user_guide/memory.html | kept | 10 | Hashes the input arguments (pickle); checks function code; hash values "not guaranteed to stay constant across joblib versions" |
| joblib on PyPI | https://pypi.org/project/joblib/ | kept | 9 | 1.6.0, 2026-08-31, BSD-3-Clause |

**Failure proof:** with `BUILD_TARGET=mine` the shipped file fails 2/3 (the new release is recomputed; a parameter change reaches downstream steps); the solution passes 3/3. The JD/MJD offset is MJD = JD − 2400000.5 (the standard definition; also in L100 #3 of this topic).
