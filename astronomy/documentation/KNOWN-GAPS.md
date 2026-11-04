# Known gaps — Astronomy L100-L400 + capstone + L500

Lessons 1-11 and the documentation were built by one pass, lessons 12-22 by a second (research/PART-B-HANDOFF.md); both were merged and source-reviewed on 2026-10-29. Everything below is still open unless marked resolved.

## Not run locally (pending-ci)
- **L100/L200 library equivalents:** Astropy 8.0.2, Skyfield 1.55, SciPy 1.18.1, photutils 3.1.1 and REBOUND 5.2.2 are not installed in the sandbox (no pip network). These files were written against the current documented APIs but have **never been executed**: `sky_astropy.py`, `time_astropy.py`, `units_astropy.py`, `kepler_skyfield.py`, `light_astropy.py`, `crossmatch_astropy.py`, `fits_astropy.py`, `photometry_photutils.py`, `periods_astropy.py`, `nbody_rebound.py`. Their tests are **skipped** locally and run in CI. API details most at risk: `u.Magnitude(...).physical`, `BlackBody` output units, `ApertureStats.median`, `area_overlap(method=...)`, REBOUND `exact_finish_time`.
- **L300/L400 library equivalents:** every item below has a test that skips when the package is missing. In CI they must run without skips, except healpy on Windows.
  - L300: `plan_astroplan.py` (astroplan 0.10.1, astropy 8.0.2), `calibrate_ccdproc.py` (ccdproc, astroscrappy), `platesolve_astropy.py`, `fit_emcee.py`, `cache_joblib.py`.
  - L400: `alert_avro.py` (fastavro), `pyvo_query.py` (needs network: Gaia TAP), `healpix_check.py` (healpy has no Windows wheels, so it is skipped there), `bessel_scipy.py`, `validate_external.py` (astropy votable; cffconvert only if on PATH), capstone `fetch_tess.py` (lightkurve plus network, π Men c, expect about 6.27 d).
- **Network on first use in CI:** Astropy may download IERS Earth-orientation data (lessons 2, 3); Skyfield downloads `de421.bsp` (~17 MB, lesson 5); `pyvo_query.py` (Gaia TAP) and `fetch_tess.py` (MAST) need external services and are `continue-on-error` in CI.
- **Wheels:** REBOUND wheels for macOS arm64 / Windows were not checked; astroplan 0.10.1 ships only an sdist. The L200 REBOUND step and the L300/L400 jobs therefore install with `--prefer-binary` (source if no wheel), not `--only-binary=:all:`.
- **CI workflow** (`.github/workflows/labs.yml`, 3-OS matrix, L100-L400 + capstone + cross-platform fingerprints) has not run. YAML parses and every referenced lab path exists (checked locally). GitHub only runs workflows from the repository root (`../CI.md`, `tools/sync_root_ci.py`). Action tags `@v7` and Python 3.12.15 copy the simulation topic; not re-verified.
- **Agent assist** (lessons 2, 10, 18, capstone) ran only against the deterministic fake servers (`labs/_shared/local_agent/`, `labs/L400/_agent/`). No real model was run (`--real` / `--real-model`). The number check matches numbers, not meaning.

## Mac mini / Windows
- **Nothing ran on macOS or Windows** (all `platforms` = expected). Homebrew cask and installer facts come from official pages; installs were not executed.
- **Cross-platform identical output** relies on `labs/L100/…/L400/cross_platform/golden.json` (written on Linux). Lesson 9's Poisson noise and any libm differences are the most likely source of a mismatch (HARDWARE.md). The spawn process pool (lesson 17) was tested on Linux with spawn forced only.
- Windows on ARM64 and Intel Macs are not covered by CI. healpy has no Windows wheels (lesson 19 equivalent skipped there); astrometry.net runs on Windows only via WSL2.

## Sources and checks
- **Sidereal time (lesson 3) - resolved 2026-10-29:** the secondary Swiss Ephemeris table (an astrology publisher) was removed. The lab now checks against (1) the IAU 2006 worked example in Wallace & Capitaine (2006, A&A 459, 981, appendix): ERA reproduced to 0.00001 s, apparent sidereal time to 0.023 s with USNO's approximate equation of the equinoxes; (2) USNO's full GMST formula (0.002-0.010 s); (3) the IERS Conventions (2010) eq. 5.14 Earth rotation angle at J2000.0 (0.0016 s). Still open: the IAU 2006 GMST−ERA polynomial (IERS eq. 5.32) and SOFA test-suite values were not retrieved (the SOFA cookbook, USNO Circular 179 and ERFA test-file fetches returned only tables of contents or nothing), so the lab does not compute GMST from ERA. UTC is used for UT1 (error < 0.9 s), which is why the worked-example check uses the published UT1 directly.
- **Star positions (lesson 2):** approximate J2000.0 (ICRS) values rounded to 0.0001°, as listed by SIMBAD; SIMBAD could not be fetched to re-check them. The lesson now states clearly (overview, step 3, glossary, README "Accuracy limit") that positions are **not precessed**: about 50″/yr (IAU 2006 precession, Wallace & Capitaine 2006 eq. 4) gives ~0.37° (~0.4°) by 2026. Nutation, aberration and refraction are ignored too. A rigorous precession correction was not added (the IAU 2006 angle series were not reproduced here); Astropy covers it in CI.
- **Leap-second table** is embedded and expires 2027-06-28; `test_leap_table_not_expired` is deliberately time-sensitive.
- **Unit definitions (lesson 4):** IAU 2012 B2 (au) and 2015 B2 (parsec) resolution texts were not fetched; values follow from the definitions and agree with the parsec value in the test.
- **Constants (lesson 6):** h, c, k (exact SI) and σ (CODATA) were not re-fetched; only Wien's b was. The Sun's 5772 K (IAU nominal) is not sourced here; "Betelgeuse-like" (3600 K) and "Rigel-like" (12100 K) temperatures are illustrative.
- **Orbits (lesson 5):** JPL approximate elements only (Mars ~40″); no light-time or aberration; JPL Horizons could not be fetched as a reference, so Skyfield + DE421 is the CI check (tolerance 0.05°).
- **N-body (lesson 11):** illustrative circular, coplanar initial conditions; masses 3.003e-6 and 9.546e-4 M☉ not re-sourced.
- **CCD equation (lesson 9):** standard form (Merline & Howell) not retrieved; consistency checked with a noise-free image and 3-sigma tests.
- **Gaia licence (re-verified 2026-10-29 on ESA's page):** "Gaia data are distributed under the CC BY-NC 3.0 IGO license" (cosmos.esa.int/web/gaia-users/license), **not** CC BY-SA 3.0 IGO as `kb/ASTRO-PLAN.md` assumed. Every mention in this topic (lessons 19 and 21, LEARNING-TOOLS, VERIFIED-RESOURCES) says CC BY-NC 3.0 IGO. The plan file sits outside the topic and was not edited.
- **Airmass (resolved 2026-10-29):** lesson 12 now uses Kasten & Young (1989, Applied Optics 28, 4735), read in full (archive.org copy): revised constants a = 0.50572, b = 6.07995°, c = 1.6364, and a test against nine Table II rows (< 0.5 %, the paper's stated maximum). Remaining gaps: the paper's argument is the *apparent* (refracted) elevation, but the lab passes true elevation (matters only within a few degrees of the horizon; refraction is not modelled); the fit dips to 0.9997 at the zenith and is clamped at 1. Pickering (2002) and Young (1994) were not used: Pickering's DIO paper was found but its airmass footnote lies beyond the fetchable text, and Young 1994 is paywalled.
- **TAN projection (lessons 8, 14):** Rθ = (180°/π) cot θ is **derived** (gnomonic projection of the unit vector; C&G 2002 eq. 16 with μ = 0), with the sketch in lesson 14's README and `fields.tan_project()` docstring. §5.1.3 of Calabretta & Greisen was truncated in every fetch; the code is verified by a round trip and against astropy in CI.
- **Cored-halo rotation curve (lesson 20):** **derived** by integrating the density ρ0/(1 + (r/rc)²) quoted in NFW 1996 (sketch in the lab README and `galaxy.py`), and verified numerically. The de Blok et al. 2008 ISO section was not reached.
- **Transit-duration bound (capstone):** T14 ≈ 13 h × (P / 1 yr)^(1/3) is **derived** (small-angle limit of Seager & Mallén-Ornelas 2003 with b = 0, plus Kepler's third law; sketch in the capstone README and `decisions/0002`). R☉/au = 0.00465 is the ratio of the IAU nominal values, not re-fetched. The Thompson et al. 2018 odd/even and secondary-test wording was not reached.
- ivoa.net document pages were blocked, so the IVOA wiki, IVOA DocView ("experimental … not yet officially endorsed") and a HAL copy were used instead. The VOTable 1.5 file uses the `.../VOTable/v1.3` namespace; votlint and astropy check this in CI only.
- The TESS acknowledgement in lesson 21 quotes the first two sentences from the MAST page; the page continues ("STScI is operated by …").
- Akaike 1974: search-result only.
- SPARC NGC 3198 data: the web page states no licence ("please cite"), so it is not vendored. Lesson 20 is synthetic, shaped like NGC 3198 (Begeman 1989). The real-data path is manual.

## Versions and tools
- astroplan 0.10.1 is the latest release (2024-08-13, about 26 months old, sdist only). Its compatibility with astropy 8.0.2 is unknown until CI runs.
- cffconvert 2.0.0 (2021) lists Python 3.6–3.9 classifiers. Installing it on 3.12 may fail, so it is optional in CI.
- healpy 1.20.1 publishes no Windows wheels ("Healpy does not currently support Windows"). On Windows, use WSL2 or skip.
- SAOImage DS9: the Homebrew cask `saoimageds9` has been disabled since 2026-09-01 (it fails the Gatekeeper check), so use the DMG from the download page. The licence is GPL-3.0 "licensed in part" per the repo README and GPL-3.0-only on the Zenodo record (lessons 1-11 pass); both are kept in LEARNING-TOOLS.
- Stellarium: Homebrew cask 26.3 as fetched by the lessons 12-22 pass (the lessons 1-11 pass read 26.2 earlier the same day); LEARNING-TOOLS shows 26.3 (the later read); the lessons 1-11 `learningTools` keep the first read ("cask 26.2; stellarium.org lists 26.3"). Either install command works. The GitHub repo shows "GPL-2.0" (the first pass recorded GPL-2.0-or-later); LEARNING-TOOLS footnotes both. The winget id `Stellarium.Stellarium` was checked only as an existing winget-pkgs folder; the manifest version was not read.
- astrometry.net licence is stated two ways: Homebrew lists BSD-3-Clause; the repo README says the whole work is GPL-3.0-or-later. On Windows it runs only under WSL2 ("it should work in WSL"), and it needs index files.
- AstroImageJ and TOPCAT licence files were not re-read; KStars, Aladin, JS9 and Gnuastro were not verified in either pass; Celestia dropped (old cask release). All GUI exercises are pending a manual run; Stellarium option names were not re-verified.

## Data and simplifications
- **Synthetic data** (seeded, labelled in every lab): star fields (lessons 1, 8, 9, 13, 14, 17, 18), catalogues (7, 19), light curves (10, 15, 16, capstone), rotation curve (20, NGC 3198-like), release inputs (21: real licences and credit texts, synthetic rows). No real images or catalogues are vendored.
- Lesson 12 uses J2000 coordinates without precession (about 0.37° by 2026, as in lesson 2) and low-precision Sun and Moon (USNO, about 1′; Schlyter, 1–2′). This is fine for planning but not for pointing. astropy checks it in CI.
- Lesson 13: synthetic camera; no non-linearity or fringing.
- Lesson 14: affine WCS only (no SIP).
- Lesson 15: white noise only.
- Lesson 18: a single Gaussian PSF kernel.
- Lesson 21: the licence rules are conservative defaults, not legal advice.
- Throughput and timing numbers (17, 19) come from a 1-CPU Linux sandbox and vary between runs; the READMEs give ranges. Option B (process pool) has not been measured on a multi-core Mac mini or Windows PC.
- Generated outputs: `labs/L300/16-…/work/`, `labs/L400/21-…/release/` and capstone `data/`, `scorecard.jsonl` and `prov.jsonl` are git-ignored, each with a `.gitignore` in its lab folder. `labs/L300/13-…/calib_log.jsonl` and `master_flat.fits`, and `labs/L400/17-…/pipeline_metrics.jsonl`, are committed example outputs.

## Concept share below target
Measured with the REBALANCE-SPEC script on the final JSON (2026-10-29): L100 15.1% (target 20-25%), L200 18.1% (25-30%), L300 20.2% (30-35%), L400 incl. capstone 20.4% (35-40%). Notes are already at full length (`wc -w`: L100 224-245, L200 364-393, L300 512-548, L400 647-731, capstone 518); the hands-on side is large (Mac/Windows steps, build tasks, failure labs, ADRs, agent assist). Reported, not padded (same as other topics, review F09/R3-14).

## L400 candidates (further study after the capstone)
- Real-data runs: TESS via lightkurve (capstone `fetch_tess.py`), and a Gaia TAP cross-match of the lesson 17 catalogue.
- Barycentric timing (BJD_TDB) and transit-timing variations.
- Iterative multi-planet BLS (mask and search again) and TLS.
- Gaussian-process detrending for fast rotators.
- A spatially varying difference-imaging kernel and ZOGY; moving-object linking.
- Kafka plus a schema registry for alert streams; HEALPix/MOC coverage maps and HiPS.
- SIP distortion in plate solving.
- Hierarchical rotation-curve fits and Bayesian evidence (nested sampling).
- Radial-velocity spectroscopy pipelines.

## L500 Theory & Rigour (lessons 23-27, added 2026-10-30)
- **Ran here, not on macOS/Windows.** All five L500 scripts, their unittests, `research/l500_checks.py`, `research/check_l500_qbank.py` and `research/qbank_checks.py` ran on Linux (Python 3.12.15, numpy 2.5.3). The new `python-labs-l500` job in `.github/workflows/labs.yml` has not run. The root-level copy that GitHub executes is generated by `../tools/sync_root_ci.py`; that script was not run because this pass must not edit `kb/.github`. `checkOutput` is compared with a tolerance of 2 units in the last printed digit, so libm differences should pass, but this is unverified.
- **Illustrative numbers (not measurements).**
  - The Cepheid P-L coefficients M_V = −2.43(log P − 1) − 4.05 are labelled illustrative. Benedict et al. 2007's Table 12 (their V-band slope and zero point) was beyond the fetched text; only their l Car values were read.
  - The Type Ia peak M_B = −19.3 is illustrative.
  - The "R = 1.711 R☉" star of problem 24.1 is illustrative; 9940 K comes from lesson 6.
  - The synthetic main sequence (L = M^3.5, R = M^0.8) and the synthetic distance ladder are seeded models, not catalogues.
- **Constants.** G = 6.67408e-11 is the CODATA 2014 value quoted in the IAU 2015 B3 text; the CODATA 2018 value was not fetched. The difference (about 3 × 10⁻⁵ relative) is below every printed digit that depends on it. Planck 2018's H₀ and Ω_m come from the arXiv abstract. Radiation is neglected in the age; the check's side calculation estimates its effect at about 0.04 %.
- **Proof depth.**
  - The mass-luminosity theorem is a homology *sketch*, so it is labelled as such.
  - Ergodicity of Metropolis (irreducibility and aperiodicity) is stated, not proved.
  - The ζ(4) = π⁴/90 value is quoted (Euler) and checked numerically.
  - The next-order d_L term is stated and checked numerically, not derived in full.
- **Sources not fetched in full.** The pnas.org and aanda.org landing pages returned nothing, so the PMC/NASA transcription and arXiv/HAL copies were used. Hubble 1929's licence is not stated on the pages retrieved, so the lesson summarises and does not reproduce it. Metropolis 1953, Riess 2022, Planck 2018, CS2023, Act 255, the Pollack concurrence and IAU CPS were read from search results (marked "(search)" in VERIFIED-RESOURCES). The Hawai'i Supreme Court majority opinion was fetched only through Part V.B.1; the holding quoted ("we now affirm") is from its introduction.
- **Ethics content.** The case study is a composite fictional scenario built on real documents. The Maunakea material presents positions as recorded in the 2018 opinion and Act 255. No community statements beyond these primary documents were retrieved: no Office of Hawaiian Affairs or Kahu Kū Mauna statements, and no material on other sites such as Mount Graham, Kitt Peak or the Atacama. This is a known gap for a fuller seminar.
- **Assessment pack.**
  - The pedagogy review that proposed the 14-week plan is not in `kb/`. `syllabus.md` follows L500-SPEC's weights and component list, and the week-by-week plan is this pass's design.
  - The numbers in the midterm/final model answers are recomputed by `research/l500_checks.py` (`exam_values`). Values quoted from earlier lab runs (Euler/leapfrog energy errors, completeness 0.1745 → 0.9729, TV 0.175) come from those labs' recorded outputs.
  - The ABET and QAA wording is paraphrased (copyrighted texts).
- **Validator gap.** `tools/check_qbank.py` reads only L100-L400 (not editable here), so L500 is validated by `research/check_l500_qbank.py` with the same rules plus the concept inventory. The root `qbank.yml` workflow does not run it yet.
- **Concept share.** Not re-measured for L500. These are theory lessons without steps, so the REBALANCE-SPEC concept/hands-on ratio does not apply.

## Found while writing the explanations (Nov 2026)
- **L400 #17:** the decision record says option C is fastest, but option A beat it in both re-runs here (C: 117–244 frames/s). C still meets the 50 frames/s target, so the decision stands on the target, not on being fastest. Re-measure on the Mac mini.
- **L400 #19:** large 5° cone searches were 7× faster than brute force here, against 17–31× in the README/ADR. Timing-dependent; re-measure.
