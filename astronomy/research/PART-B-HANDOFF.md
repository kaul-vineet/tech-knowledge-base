# Part B hand-off: lessons 12–22 → documentation / CI owner (part A)

Part B wrote:
- `content/L300.json`, `content/L400.json` (17–21 + Capstone 22);
- `content/concepts/L300/`, `content/concepts/L400/`;
- `labs/L300/` (12–16, `cross_platform/`, `requirements.txt`);
- `labs/L400/` (17–21, `22-capstone/`, `cross_platform/`, `_agent/`, `requirements.txt`);
- `research/L300-evidence.md`, `research/L400-evidence.md`.

Nothing under `documentation/`, `labs/_shared/` or `.github/` was touched. Below is what part A needs to merge. Everything was checked on 2026-10-29.

## (c) Exact lesson titles 12–22 (as in the JSON)

| # | Level | Title | Lab folder |
|---|---|---|---|
| 12 | L300 | Observation planning: airmass, twilight, Moon distance and a scheduler under constraints | labs/L300/12-observation-planning |
| 13 | L300 | Calibration frames: bias, dark, flat and cosmic-ray rejection | labs/L300/13-ccd-calibration |
| 14 | L300 | Plate solving (astrometry-lite): match star triangles, fit a WCS, check residuals | labs/L300/14-plate-solving |
| 15 | L300 | Fitting with honest uncertainty: least squares, bootstrap and MCMC for a transit | labs/L300/15-honest-uncertainty |
| 16 | L300 | Reproducible data pipelines: provenance, caching and versioned inputs | labs/L300/16-reproducible-pipelines |
| 17 | L400 | Survey pipeline architecture: ingest, calibrate, detect, catalogue - throughput measured | labs/L400/17-survey-pipeline |
| 18 | L400 | Time-domain alerts: difference detection, alert schema and broker filters | labs/L400/18-alert-broker |
| 19 | L400 | Big catalogues: sky indexing, cone-search performance and TAP/ADQL | labs/L400/19-big-catalogues |
| 20 | L400 | Model comparison: a galaxy rotation curve with and without a dark-matter halo | labs/L400/20-model-comparison |
| 21 | L400 | Open data and science software practice: VO standards, licences, citation and validation | labs/L400/21-open-data-practice |
| 22 | Capstone | Capstone: an exoplanet transit search pipeline | labs/L400/22-capstone |

**Action for part A:**
- L200 #7–#11 `next` fields still use the plan's wording, for example "L300 #13 Calibration: bias, dark, flat, cosmic-ray rejection". Replace them with the exact titles above.
- Suggested reverse `seeAlso` links (L100/L200 → L300/L400), optional:
  - #2 → #12;
  - #3 → #16 (the JD/MJD half-day bug);
  - #7 → #19;
  - #8 → #14;
  - #9 → #13;
  - #10 → #15 and #22.
- Part B's `seeAlso` entries use part A's **current** titles for lessons 1–11, read from `content/L100.json` and `L200.json` at build time. If those titles change, tell part B, or re-run the check in `research/` (see the validation section).

## (a) Rows to append to documentation/VERIFIED-RESOURCES.md
Same columns as the existing table: Title | URL | Type | Licence | Version / date checked | Score /12 | Used in lesson(s).

| Title | URL | Type | Licence | Version / date checked | Score /12 | Used in lesson(s) |
|---|---|---|---|---|---|---|
| USNO: Computing Approximate Solar Coordinates | https://aa.usno.navy.mil/faq/sun_approx | docs | US Government work (not shown) | checked 2026-10-29 | 11 | 12 (primary) |
| USNO: Rise, Set, and Twilight Definitions | https://aa.usno.navy.mil/faq/RST_defs | docs | US Government work (not shown) | checked 2026-10-29 | 10 | 12 (primary) |
| P. Schlyter: How to compute planetary positions | https://www.stjarnhimlen.se/comp/ppcomp.html | docs | not shown | checked 2026-10-29 | 9 | 12 (primary) |
| astroplan: AirmassConstraint | https://astroplan.readthedocs.io/en/stable/api/astroplan.AirmassConstraint.html | docs | BSD-3 (package) | 0.10.1 | 10 | 12 (primary) |
| astroplan: Scheduling tutorial | https://astroplan.readthedocs.io/en/stable/tutorials/scheduling.html | docs | BSD-3 (package) | 0.10.1 | 9 | 12 (primary) |
| SIMBAD (Vega and 7 other stars; van Leeuwen 2007) | https://simbad.cds.unistra.fr/simbad/sim-id?Ident=Vega | data | not shown | checked 2026-10-29 | 10 | 12 (supporting) |
| Wikipedia: Air mass (astronomy) | https://en.wikipedia.org/wiki/Air_mass_%28astronomy%29 | docs (secondary pointer) | CC BY-SA (not shown) | checked 2026-10-29 | 6 | 12 (supporting only; Pickering 2002 formula) |
| astropy CCD Data Reduction Guide | https://github.com/astropy/ccd-reduction-and-photometry-guide | repo/course | BSD-3-Clause | 2.0.0 | 11 | 13 (primary) |
| ccdproc: Combiner | https://ccdproc.readthedocs.io/en/latest/api/ccdproc.Combiner.html | docs | BSD-3-Clause | 2.5.1 | 11 | 13 (primary) |
| van Dokkum 2001, L.A.Cosmic (PASP 113, 1420) | https://arxiv.org/abs/astro-ph/0108003 | paper | not shown | 2001 | 10 | 13 (primary) |
| Siril docs: Calibration | https://siril.readthedocs.io/en/stable/preprocessing/calibration.html | docs | not shown | 1.4.4 docs | 9 | 13 (primary) |
| Lang et al. 2010, Astrometry.net (AJ 139, 1782) | https://arxiv.org/abs/0910.2233 | paper | not shown | 2010 | 11 | 14 (primary) |
| Calabretta & Greisen 2002, WCS Paper II | https://arxiv.org/abs/astro-ph/0207413 | spec/paper | not shown | 2002 | 11 | 14 (primary) |
| astropy: fit_wcs_from_points | https://docs.astropy.org/en/stable/api/astropy.wcs.utils.fit_wcs_from_points.html | docs | BSD-3-Clause | 8.0.2 | 10 | 14 (primary) |
| Beroiz, Cabral & Sanchez 2020, astroalign | https://arxiv.org/abs/1909.02946 | paper | MIT (code) | 2020 | 10 | 14 (primary) |
| Hogg, Bovy & Lang 2010, Fitting a model to data | https://arxiv.org/abs/1008.4686 | paper | not shown | 2010 | 11 | 15 (primary) |
| Hogg & Foreman-Mackey 2018, Using MCMC | https://arxiv.org/abs/1710.06068 | paper | not shown | 2018 | 11 | 15 (primary) |
| emcee docs: Autocorrelation analysis | https://emcee.readthedocs.io/en/stable/tutorials/autocorr/ | docs | MIT | 3.1.6 | 10 | 15 (primary) |
| Seager & Mallén-Ornelas 2003 | https://arxiv.org/abs/astro-ph/0206228 | paper | not shown | 2003 | 10 | 15 (primary) |
| NIST/SEMATECH e-Handbook: Bootstrap plot | https://www.itl.nist.gov/div898/handbook/eda/section3/bootplot.htm | docs | US Government work (not shown) | checked 2026-10-29 | 9 | 15 (primary) |
| W3C PROV-DM | https://www.w3.org/TR/prov-dm/ | spec | W3C document licence | REC 2013-04-30 | 11 | 16 (primary) |
| IVOA Provenance DM 1.0 (HAL copy) | https://hal.science/hal-03433754/document | spec | not shown | REC 2020-04-11 | 9 | 16 (primary) |
| Sandve et al. 2013, Ten Simple Rules for Reproducible Computational Research | https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003285 | paper | CC BY | 2013 | 10 | 16 (primary) |
| joblib: Memory user guide | https://joblib.readthedocs.io/en/stable/user_guide/memory.html | docs | BSD-3-Clause | 1.6.0 | 10 | 16 (primary) |
| Masci et al. 2019, ZTF Science Data System | https://arxiv.org/abs/1902.01872 | paper | CC BY 3.0 | 2019 | 11 | 17 (primary) |
| Bertin & Arnouts 1996, SExtractor (ADS scan) | https://articles.adsabs.harvard.edu/pdf/1996A%26AS..117..393B | paper | not shown | 1996 | 10 | 17 (primary) |
| photutils: Background2D | https://photutils.readthedocs.io/en/stable/api/photutils.background.Background2D.html | docs | BSD-3-Clause | 3.1.1 | 10 | 17 (primary) |
| Python docs: multiprocessing | https://docs.python.org/3/library/multiprocessing.html | docs | PSF (not shown) | 3.x | 10 | 17 (primary) |
| Rubin/LSST Science Pipelines | https://pipelines.lsst.io/ | docs | code GPL-3.0, docs CC BY-SA 4.0 | v30_0_10 | 9 | 17 (primary) |
| ZTF Avro alert schemas | https://zwickytransientfacility.github.io/ztf-avro-alert/schema.html | spec | not shown | v4.01 | 10 | 18 (primary) |
| Alard & Lupton 1998 | https://arxiv.org/abs/astro-ph/9712287 | paper | not shown | 1998 | 11 | 18 (primary) |
| Zackay, Ofek & Gal-Yam 2016 (ZOGY) | https://arxiv.org/abs/1601.02655 | paper | not shown | 2016 | 10 | 18 (primary) |
| DMTN-093: Rubin alert distribution | https://dmtn-093.lsst.io/ | docs | not shown | checked 2026-10-29 | 9 | 18 (primary) |
| Apache Avro specification | https://avro.apache.org/docs/current/specification/ | spec | Apache-2.0 (project; not shown) | current | 10 | 18 (primary) |
| Lasair docs: Make a filter | https://lasair.readthedocs.io/en/main/core_functions/make_filter.html | docs | not shown | main | 8 | 18 (primary) |
| fastavro (PyPI) | https://pypi.org/project/fastavro/ | package | MIT | 1.13.1 (2026-10-07) | 9 | 18 (supporting) |
| Gray, Szalay et al. 2004, There Goes the Neighborhood | https://arxiv.org/abs/cs/0408031 | paper | not shown | MSR-TR-2004-32 | 11 | 19 (primary) |
| Górski et al. 2005, HEALPix | https://arxiv.org/abs/astro-ph/0409513 | paper | not shown | 2005 | 11 | 19 (primary) |
| IVOA ADQL page | https://wiki.ivoa.net/twiki/bin/view/IVOA/ADQL | spec | not shown | ADQL 2.1 REC 2023-12-15 | 9 | 19 (primary) |
| IVOA TAP 1.1 RFC page | https://wiki.ivoa.net/twiki/bin/view/IVOA/TAP11RFC | spec | not shown | TAP 1.1 | 8 | 19 (primary) |
| Gaia archive: Extract data | https://www.cosmos.esa.int/web/gaia-users/archive/extract-data | docs | not shown | checked 2026-10-29 | 9 | 19 (primary) |
| pyvo: Data Access | https://pyvo.readthedocs.io/en/latest/dal/index.html | docs | BSD-3-Clause | 1.9.1 | 10 | 19 (primary) |
| healpy.query_disc | https://healpy.readthedocs.io/en/latest/generated/healpy.query_disc.html | docs | GPL-2.0-only | 1.20.1 (no Windows wheels) | 9 | 19 (supporting) |
| Navarro, Frenk & White 1996 | https://arxiv.org/abs/astro-ph/9508025 | paper | not shown | 1996 | 11 | 20 (primary) |
| Freeman 1970 (ADS scan) | https://articles.adsabs.harvard.edu/pdf/1970ApJ...160..811F | paper | not shown | 1970 | 10 | 20 (primary) |
| Begeman 1989 (NGC 3198; university-hosted scan) | https://sites.ualberta.ca/~pogosyan/teaching/ASTRO_322/WINTER_2008/Begeman1989A+A...223...47B.pdf | paper | not shown | 1989 | 9 | 20 (primary) |
| Lelli, McGaugh & Schombert 2016, SPARC | https://arxiv.org/abs/1606.09251 | paper | not shown (data page: no licence) | 2016 | 10 | 20 (primary) |
| Schwarz 1978, BIC | https://projecteuclid.org/journals/annals-of-statistics/volume-6/issue-2/Estimating-the-Dimension-of-a-Model/10.1214/aos/1176344136.full | paper | © IMS | 1978 | 9 | 20 (primary) |
| NIST/SEMATECH e-Handbook: Runs test | https://www.itl.nist.gov/div898/handbook/eda/section3/eda35d.htm | docs | US Government work (not shown) | checked 2026-10-29 | 10 | 20 (primary) |
| ESA Gaia: data licence | https://www.cosmos.esa.int/web/gaia-users/license | policy | CC BY-NC 3.0 IGO (the data) | checked 2026-10-29 | 11 | 19, 21 (primary) |
| Gaia DR3 credit and citation instructions | https://gea.esac.esa.int/archive/documentation/GDR3/Miscellaneous/sec_credit_and_citation_instructions/ | policy | not shown | DR3 | 11 | 21 (primary) |
| MAST: Data Use | https://archive.stsci.edu/publishing/data-use | policy | public domain (most data); HLSPs CC BY 4.0 | checked 2026-10-29 | 10 | 21 (primary) |
| MAST: mission acknowledgements | https://archive.stsci.edu/publishing/mission-acknowledgements | policy | not shown | checked 2026-10-29 | 10 | 21 (supporting) |
| IVOA VOTable (DocView) | https://ivoa.github.io/IvoaDocViewSite/idoc/VOTable/VOTable.html | spec | not shown | VOTable 1.5 REC 2025-01-16 | 9 | 21 (primary) |
| Citation File Format schema guide | https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md | spec | not shown | CFF 1.2.0 | 10 | 21 (primary) |
| SPDX License List | https://spdx.org/licenses/ | spec | not shown | 3.29.0 (2026-09-16) | 10 | 21 (supporting) |
| Wilkinson et al. 2016, FAIR Guiding Principles | https://pmc.ncbi.nlm.nih.gov/articles/PMC4792175/ | paper | CC BY 4.0 | 2016 | 10 | 21 (primary) |
| Smith, Katz & Niemeyer 2016, Software citation principles (FORCE11 copy) | https://force11.org/info/software-citation-principles-published-2016/ | paper | not shown | 2016 | 9 | 21 (primary) |
| CC BY-SA 3.0 IGO deed | https://creativecommons.org/licenses/by-sa/3.0/igo/ | licence | CC | checked 2026-10-29 | 9 | 21 (supporting: ShareAlike rule) |
| Kovács, Zucker & Mazeh 2002, BLS | https://arxiv.org/abs/astro-ph/0206099 | paper | not shown | 2002 | 11 | 22 (primary) |
| astropy: Box Least Squares | https://docs.astropy.org/en/stable/timeseries/bls.html | docs | BSD-3-Clause | 8.0.2 | 10 | 22 (primary) |
| lightkurve (repo) | https://github.com/lightkurve/lightkurve | repo | MIT | 2.6.0 | 10 | 22 (primary) |
| Thompson et al. 2018, Kepler DR25 Robovetter | https://arxiv.org/abs/1710.06758 | paper | not shown | 2018 | 9 | 22 (primary) |
| Huang et al. 2018, π Men c | https://arxiv.org/abs/1809.05967 | paper | not shown | 2018 | 10 | 22 (primary) |
| TESS FAQ (HEASARC) | https://heasarc.gsfc.nasa.gov/docs/tess/faq.html | docs | US Government work (not shown) | checked 2026-10-29 | 9 | 22 (primary) |
| NASA Exoplanet Archive: π Men | https://exoplanetarchive.ipac.caltech.edu/overview/pi%20Men | data | not shown | checked 2026-10-29 | 9 | 22 (supporting) |
| PyPI pins: astroplan 0.10.1 / ccdproc 2.5.1 / astroscrappy 1.3.0 / emcee 3.1.6 / joblib 1.6.0 / pyvo 1.9.1 / healpy 1.20.1 / lightkurve 2.6.0 | https://pypi.org/project/astroplan/ (and /ccdproc/, /astroscrappy/, /emcee/, /joblib/, /pyvo/, /healpy/, /lightkurve/) | package | BSD-3 / BSD-3 / BSD-3 / MIT / BSD-3 / BSD-3 / GPL-2.0-only / MIT | released 2024-08-13 / 2025-07-05 / 2025-10-31 / 2024-04-19 / 2026-08-31 / 2026-06-11 / 2026-10-03 / 2026-04-16 | 9 | 12–22 (supporting) |
| Homebrew cask stellarium | https://formulae.brew.sh/cask/stellarium | package | GPL-2.0 (GitHub repo licence) | 26.3 | 9 | 12, 14, 22 (tool) |
| Stellarium repo | https://github.com/Stellarium/stellarium | repo | GPL-2.0 | 26.3 | 9 | 12, 14, 22 (tool) |
| winget-pkgs: Stellarium.Stellarium folder | https://github.com/microsoft/winget-pkgs/tree/master/manifests/s/Stellarium/Stellarium | package | n/a | folder exists (manifest version not read) | 8 | 12, 14, 22 (tool) |
| SAOImageDS9 download page | https://sites.google.com/cfa.harvard.edu/saoimageds9/download | download | GPL-3.0, "licensed in part" (repo README) | 8.8 (2026-10-01) | 9 | 13 (tool) |
| Siril downloads | https://siril.org/download/ | download | GPL-3.0 (gitlab.com/free-astro/siril) | 1.4.5 (2026-10-28) | 9 | 13 (tool) |
| TOPCAT home page | https://www.star.bris.ac.uk/mbt/topcat/ | download/docs | GPL (some LGPL) | 4.10-8 (2026-08-21) | 10 | 19, 21, 22 (tool) |
| astrometry.net: Use it | https://astrometry.net/use.html | docs | BSD-3 own code; whole work GPL-3.0+ (README) | checked 2026-10-29 | 9 | 14 (tool) |
| Homebrew formula astrometry-net | https://formulae.brew.sh/formula/astrometry-net | package | BSD-3-Clause (as listed) | 0.97 | 9 | 14 (tool) |

## (b) Items for documentation/KNOWN-GAPS.md

**Not run locally (pending-ci).** Every item below has a test that skips when the package is missing. In CI they must run without skips, except healpy on Windows.
- L300: `plan_astroplan.py` (astroplan 0.10.1, astropy 8.0.2), `calibrate_ccdproc.py` (ccdproc, astroscrappy), `platesolve_astropy.py`, `fit_emcee.py`, `cache_joblib.py`.
- L400: `alert_avro.py` (fastavro), `pyvo_query.py` (needs network: Gaia TAP), `healpix_check.py` (healpy has no Windows wheels, so it is skipped there), `bessel_scipy.py`, `validate_external.py` (astropy votable; cffconvert only if on PATH), capstone `fetch_tess.py` (lightkurve plus network, π Men c, expect about 6.27 d).
- Agent assists (18, capstone) ran against the deterministic fake server only (`labs/L400/_agent/`). `--real` / `--real-model` against Ollama was not run.
- No lab has run on macOS or Windows; every `platforms` value is "expected". The spawn process pool (lesson 17) was tested on Linux with spawn forced.

**Versions and tools.**
- astroplan 0.10.1 is the latest release (2024-08-13, about 26 months old, sdist only). Its compatibility with astropy 8.0.2 is unknown until CI runs.
- cffconvert 2.0.0 (2021) lists Python 3.6–3.9 classifiers. Installing it on 3.12 may fail, so it is optional in CI.
- healpy 1.20.1 publishes no Windows wheels ("Healpy does not currently support Windows"). On Windows, use WSL2 or skip.
- SAOImage DS9: the Homebrew cask `saoimageds9` has been disabled since 2026-09-01 (it fails the Gatekeeper check), so use the DMG from the download page. The licence is GPL-3.0 "in part" per the repo README; part A's table says GPL-3.0-only from the Zenodo record.
- Stellarium: Homebrew cask 26.3, as fetched (part A lists "cask 26.2"). The GitHub repo shows "GPL-2.0" (part A: GPL-2.0-or-later). The winget id `Stellarium.Stellarium` was checked only as an existing winget-pkgs folder; the manifest version was not read.
- astrometry.net licence is stated two ways: Homebrew lists BSD-3-Clause; the repo README says the whole work is GPL-3.0-or-later. On Windows it runs only under WSL2 ("it should work in WSL"), and it needs index files.

**Sources.**
- **Gaia licence correction:** the Gaia data licence is **CC BY-NC 3.0 IGO** (cosmos.esa.int/web/gaia-users/license), not CC BY-SA 3.0 IGO as ASTRO-PLAN assumed. Lessons 19 and 21 use the correct terms. Check any part A text that repeats the plan.
- Pickering (2002) airmass formula: no primary (DIO) URL was found, so the formula text comes from Wikipedia (secondary). Kasten & Young 1989 is paywalled; only the abstract was read.
- TAN projection: Rθ = (180°/π) cot θ is derived from Calabretta & Greisen eq. 16 with μ = 0. §5.1.3 was truncated in every fetch; the code is verified by a round trip and astropy in CI.
- Cored-halo rotation curve: derived by integrating the density ρ0/(1 + (r/rc)²) quoted in NFW 1996, and verified numerically. The de Blok et al. 2008 ISO section was not reached.
- Duration bound for vetting: T14 ≈ 13 h × (P / 1 yr)^(1/3) is derived from Kepler's third law (R☉/a = 0.00465), not quoted. The Thompson et al. 2018 odd/even and secondary-test wording was not reached.
- ivoa.net document pages were blocked, so the IVOA wiki, IVOA DocView ("experimental … not yet officially endorsed") and a HAL copy were used instead. The VOTable 1.5 file uses the `.../VOTable/v1.3` namespace; votlint and astropy check this in CI only.
- The TESS acknowledgement in lesson 21 quotes the first two sentences from the MAST page; the page continues ("STScI is operated by …").
- Akaike 1974: search-result only.
- SPARC NGC 3198 data: the web page states no licence ("please cite"), so it is not vendored. Lesson 20 is synthetic, shaped like NGC 3198 (Begeman 1989). The real-data path is manual.

**Simplifications.**
- Lesson 12 uses J2000 coordinates without precession (about 0.36° by 2026) and low-precision Sun and Moon (USNO, about 1′; Schlyter, 1–2′). This is fine for planning but not for pointing. astropy checks it in CI.
- Lesson 13: synthetic camera; no non-linearity or fringing.
- Lesson 14: affine WCS only (no SIP).
- Lesson 15: white noise only.
- Lesson 18: a single Gaussian PSF kernel.
- Lesson 21: the licence rules are conservative defaults, not legal advice.
- Throughput and timing numbers (17, 19) come from a 1-CPU Linux sandbox and vary between runs; the READMEs give ranges. Option B (process pool) has not been measured on a multi-core Mac mini or Windows PC.
- Generated outputs: `labs/L300/16-…/work/`, `labs/L400/21-…/release/` and capstone `data/`, `scorecard.jsonl` and `prov.jsonl` are git-ignored, each with a `.gitignore` in its lab folder. `labs/L300/13-…/calib_log.jsonl` and `master_flat.fits`, and `labs/L400/17-…/pipeline_metrics.jsonl`, are committed example outputs.

**Concept share below target** (REBALANCE script on part B's JSON): L300 20.2 % against a 30–35 % target; L400 20.4 % against 35–40 %. Notes are at full length: L300 512–549 words, L400 647–734, capstone 518–525 (`wc -w`, C and UTF-8 locales). Reported, not padded.

**L400 candidates (further study after the capstone).**
- Real-data runs: TESS via lightkurve (capstone `fetch_tess.py`), and a Gaia TAP cross-match of the lesson 17 catalogue.
- Barycentric timing (BJD_TDB) and transit-timing variations.
- Iterative multi-planet BLS (mask and search again) and TLS.
- Gaussian-process detrending for fast rotators.
- A spatially varying difference-imaging kernel and ZOGY; moving-object linking.
- Kafka plus a schema registry for alert streams; HEALPix/MOC coverage maps and HiPS.
- SIP distortion in plate solving.
- Hierarchical rotation-curve fits and Bayesian evidence (nested sampling).
- Radial-velocity spectroscopy pipelines.

## (d) Learning tools used in lessons 12–22 (verified by part B, 2026-10-29)

| Tool | Role | Licence (OSI) | Mac mini install | Windows install | URL | Lessons |
|---|---|---|---|---|---|---|
| Stellarium 26.3 | SEE | GPL-2.0 (yes) | `brew install --cask stellarium` | `winget install -e --id Stellarium.Stellarium` (folder exists in winget-pkgs) or the installer from stellarium.org | https://stellarium.org/ | 12, 14, 22 |
| SAOImage DS9 8.8 | INSPECT | GPL-3.0, "licensed in part" (yes) | Aqua DMG from the download page (Homebrew cask disabled 2026-09-01) | Installer from the download page (C:\SAOImageDS9) | https://sites.google.com/cfa.harvard.edu/saoimageds9/download | 13 |
| Siril 1.4.5 | CHECK | GPL-3.0 (yes) | DMG from siril.org/download (macOS 13+) | Installer from siril.org/download | https://siril.org/download/ | 13 |
| TOPCAT (+ STILTS) 4.10-8 | CHECK | GPL, some LGPL (yes) | `brew install --cask topcat` (also installs `stilts`) | `java -jar topcat-full.jar` (Java 8+) | https://www.star.bris.ac.uk/mbt/topcat/ | 19, 21, 22 |
| astrometry.net (solve-field) 0.97 | CHECK | own code BSD-3; whole work GPL-3.0-or-later (yes) | `brew install astrometry-net` (+ index files) | WSL2: `sudo apt install astrometry.net` (no native build) | https://astrometry.net/use.html | 14 |
| JupyterLab (+ JupyterLab Desktop) 4.6.4 | CHECK | BSD-3-Clause (yes) | `pip install jupyterlab` (catalog) | `pip install jupyterlab` / `winget install jupyterlab` (catalog) | https://pypi.org/project/jupyterlab/ | 15, 17, 18, 20, 22 |

Not used in lessons 12–22: Aladin, KStars, AstroImageJ, JS9, Gnuastro (not verified by part B), and Celestia.

## (e) CI fragment for .github/workflows/labs.yml (same style as kb/simulation)
Paste these jobs under `jobs:`, and add the two cross-platform steps to the existing `cross-platform` job, if part A has one. Otherwise use the job below. Requirements chain: `labs/L400/requirements.txt` → L300 → L200 → L100.

```yaml
  python-labs-l300:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        lab:
          - 12-observation-planning
          - 13-ccd-calibration
          - 14-plate-solving
          - 15-honest-uncertainty
          - 16-reproducible-pipelines
        include:
          - { lab: 12-observation-planning,   demo: "plan.py --check",  equivalent: "plan_astroplan.py",     solution: "solution/plan.py",        stretch: "solution/urgent.py" }
          - { lab: 13-ccd-calibration,        demo: "calibrate.py",     equivalent: "calibrate_ccdproc.py",  solution: "solution/calibrate.py",   stretch: "solution/gain.py" }
          - { lab: 14-plate-solving,          demo: "platesolve.py",    equivalent: "platesolve_astropy.py", solution: "solution/platesolve.py",  stretch: "solution/search.py" }
          - { lab: 15-honest-uncertainty,     demo: "transit_fit.py",   equivalent: "fit_emcee.py",          solution: "solution/transit_fit.py", stretch: "solution/report.py" }
          - { lab: 16-reproducible-pipelines, demo: "pipeline.py",      equivalent: "cache_joblib.py",       solution: "solution/pipeline.py",    stretch: "solution/lineage.py" }
    defaults:
      run:
        shell: bash  # Git Bash on Windows: the same commands run on all three runners
        working-directory: labs/L300/${{ matrix.lab }}
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: "3.12.15"
      - name: Install pinned dependencies (L200 pins + astroplan, ccdproc, astroscrappy, emcee, joblib; wheels only)
        run: "python -m pip install --only-binary=:all: -r ../requirements.txt"
      - name: Run demo (shipped, unfixed)
        run: python ${{ matrix.demo }}
      - name: Run tryIt
        run: python try_it.py
      - name: Run buildTask reference solution (the fix) and the stretch solution
        run: |
          python ${{ matrix.solution }}
          python ${{ matrix.stretch }}
      - name: buildTask test must FAIL on the shipped (unfixed) lab file
        run: "! BUILD_TARGET=mine python -m unittest test_build_task"
      - name: Run library equivalent (astroplan / ccdproc / astropy / emcee / joblib)
        run: python ${{ matrix.equivalent }}
      - name: Run tests incl. fault reproductions, test_build_task and test_stretch (no skips expected in CI)
        run: python -m unittest -v

  python-labs-l400:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        lab:
          - 17-survey-pipeline
          - 18-alert-broker
          - 19-big-catalogues
          - 20-model-comparison
          - 21-open-data-practice
        include:
          - { lab: 17-survey-pipeline,     demo: "survey.py",   extra: "",            solution: "solution/survey.py",  equivalent: "",                     agent: "" }
          - { lab: 18-alert-broker,        demo: "alerts.py",   extra: "",            solution: "solution/alerts.py",  equivalent: "alert_avro.py",        agent: "agent_assist.py" }
          - { lab: 19-big-catalogues,      demo: "catalog.py",  extra: "",            solution: "solution/catalog.py", equivalent: "healpix_check.py",     agent: "" }
          - { lab: 20-model-comparison,    demo: "compare.py",  extra: "",            solution: "solution/compare.py", equivalent: "bessel_scipy.py",      agent: "" }
          - { lab: 21-open-data-practice,  demo: "release.py",  extra: "defects.py",  solution: "solution/release.py", equivalent: "validate_external.py", agent: "" }
    defaults:
      run:
        shell: bash
        working-directory: labs/L400/${{ matrix.lab }}
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: "3.12.15"
      - name: Install pinned dependencies (L300 pins + fastavro, pyvo, healpy (not on Windows), lightkurve; wheels only)
        run: "python -m pip install --only-binary=:all: -r ../requirements.txt"
      - name: Optional cffconvert 2.0.0 (lesson 21; old package, may not install on 3.12)
        if: matrix.lab == '21-open-data-practice'
        run: python -m pip install cffconvert==2.0.0 || echo "cffconvert not installable - validate_external.py skips it"
      - name: Run demo (shipped design)
        run: python ${{ matrix.demo }}
      - name: Run extra evidence script
        if: matrix.extra != ''
        run: python ${{ matrix.extra }}
      - name: Run buildTask reference solution (the fix)
        run: python ${{ matrix.solution }}
      - name: Run tryIt
        run: python try_it.py
      - name: buildTask + fitness tests must FAIL on the shipped (unfixed) lab file
        run: "! BUILD_TARGET=mine python -m unittest test_build_task test_fitness"
      - name: Run library equivalent (healpy has no Windows wheels)
        if: matrix.equivalent != '' && !(matrix.lab == '19-big-catalogues' && runner.os == 'Windows')
        run: python ${{ matrix.equivalent }}
      - name: TAP query against the Gaia archive (lesson 19; external service)
        if: matrix.lab == '19-big-catalogues'
        continue-on-error: true
        run: python pyvo_query.py
      - name: Run agent assist with the fake model
        if: matrix.agent != ''
        run: python ${{ matrix.agent }}
      - name: Fitness function 3x (wall-clock bounds are generous)
        run: for i in 1 2 3; do python -m unittest test_fitness || exit 1; done
      - name: Run tests incl. fault reproductions, test_build_task and test_fitness (healpy/pyvo may skip on Windows / offline)
        run: python -m unittest -v

  python-capstone-l400:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    defaults:
      run:
        shell: bash
        working-directory: labs/L400/22-capstone
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: "3.12.15"
      - name: Install pinned dependencies (wheels only)
        run: "python -m pip install --only-binary=:all: -r ../requirements.txt"
      - name: Run the capstone (fake model) - scorecard must be PASS
        run: |
          python run_capstone.py
          python -c "import json; l = [json.loads(x) for x in open('scorecard.jsonl', encoding='utf-8')]; assert l[-1]['scorecard'] == 'PASS', l[-1]"
      - name: Run tryIt
        run: python try_it.py
      - name: Milestone tests and fitness functions
        run: python -m unittest -v
      - name: Real TESS data for pi Men (lightkurve; external service; expect ~6.27 d)
        continue-on-error: true
        run: python fetch_tess.py

  cross-platform-l300-l400:
    # same seeds -> same printed results on every OS (golden.json written on Linux x86_64)
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    defaults:
      run:
        shell: bash
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: "3.12.15"
      - name: Install pinned dependencies
        run: "python -m pip install --only-binary=:all: -r labs/L400/requirements.txt"
      - name: L300 seeded fingerprints match golden.json
        working-directory: labs/L300/cross_platform
        run: python -m unittest -v
      - name: L400 + capstone seeded fingerprints match golden.json
        working-directory: labs/L400/cross_platform
        run: python -m unittest -v
      - name: L400 local-agent helper (astronomy copy, fake server only)
        working-directory: labs/L400/_agent
        run: python -m unittest -v
```

Header comment to add: "L300 adds astroplan, ccdproc, astroscrappy, emcee, joblib (labs/L300/requirements.txt, which includes the L200 pins). L400 adds fastavro, pyvo, healpy (not Windows) and lightkurve (labs/L400/requirements.txt, which includes the L300 pins). pyvo_query.py and fetch_tess.py call external services, so they are continue-on-error."

## (f) Concept share (REBALANCE measurement script on part B's JSON)

| Level | Concept words | Hands-on words | Share | Target | Note words (`wc -w`) |
|---|---|---|---|---|---|
| L300 (12–16) | 2701 | 10687 | **20.2 %** | 30–35 % | 512–549 (C locale), 529–549 (UTF-8) |
| L400 (17–21 + 22) | 3970 | 15476 | **20.4 %** | 35–40 % | 647–731 (C), 649–734 (UTF-8); capstone 518 / 525 |

Suggested README line: "Concept share (measured): L100 15.9 %, L200 18.4 %, L300 20.2 %, L400 20.4 % (notes at full length; reported, not padded)."

## Validation summary (part B)
- Every test file in `labs/L300/*`, `labs/L400/*`, `labs/L400/_agent`, `labs/L300/cross_platform` and `labs/L400/cross_platform` was run here with `python -m unittest` from its folder. Results are in each lab README (rendered from real runs).
- The time-sensitive suites (17, 19, the capstone) and lessons 18 and 20 were run 3× in a row.
- Fail-before / pass-after: `BUILD_TARGET=mine` on each shipped file fails, and the solution passes, in all 10 lessons:

| Lesson | Shipped failures |
|---|---|
| 12 | 15 |
| 13 | 12 |
| 14 | 3 |
| 15 | 2 |
| 16 | 2 |
| 17 | 3 |
| 18 | 2 |
| 19 | 8 |
| 20 | 12 |
| 21 | 3 |
