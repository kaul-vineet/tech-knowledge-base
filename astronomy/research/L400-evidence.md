# L400 research evidence — Astronomy & Astrophysics (applied), lessons 17–21 + capstone 22

Method as in L300-evidence.md: sources retrieved 2026-10-29, scored 0–2 on six criteria and kept at ≥ 8/12; anything read only from a search result is marked. Every number in the L400 concept notes, ADRs and option tables comes from a lab run (the READMEs are rendered from real runs). Wall-clock numbers (frames/s, ms/query) vary between runs, and the text gives ranges. Fail-before / pass-after evidence: `BUILD_TARGET=mine python -m unittest test_build_task test_fitness` on the shipped file against the solution (listed per lesson). Time-sensitive fitness tests (17, 19) and the capstone were run 3× in a row.

Additional PyPI pins (2026-10-29):
- fastavro 1.13.1 (2026-10-07, MIT, macOS universal2 + Windows x64 wheels, "maintenance mode");
- pyvo 1.9.1 (2026-06-11, BSD-3, pure Python);
- healpy 1.20.1 (2026-10-03, GPL-2.0-only, **no Windows wheels**: "Healpy does not currently support Windows");
- scipy 1.18.1 (2026-08-21, BSD; the wheel list was not in the fetched text);
- lightkurve 2.6.0 (2026-04-16, MIT, pure Python).

---

## Lesson 17 — Survey pipeline architecture
**Questions:** How do production surveys structure ingest → calibrate → detect → catalogue, and what latency do they target? How is a spatially varying sky background estimated? How does the multiprocessing start method affect a pool on macOS and Windows?

| Source | URL | Decision | Score | Key facts |
|---|---|---|---|---|
| Masci et al. 2019, ZTF Science Data System, PASP 131, 018003 | https://arxiv.org/abs/1902.01872 | kept | 11 | "nine pipelines"; 64 CCD-quadrants per exposure; alerts within 13 min (95th percentile) against a 20 min requirement; ZOGY differencing |
| Bertin & Arnouts 1996, SExtractor (ADS scan) | https://articles.adsabs.harvard.edu/pdf/1996A%26AS..117..393B | kept | 10 | Mesh background, ±3σ clipping, mesh "32 to 128 pixels", bilinear interpolation between meshes |
| SExtractor docs, Background | https://sextractor.readthedocs.io/en/latest/Background.html | kept | 10 | Mode = 2.5 × median − 1.5 × mean; BACK_SIZE / BACK_FILTERSIZE |
| photutils Background2D (3.1.1) | https://photutils.readthedocs.io/en/stable/api/photutils.background.Background2D.html | kept | 10 | box_size, filter_size, SigmaClip(3.0); SExtractorBackground default |
| Rubin/LSST Science Pipelines docs | https://pipelines.lsst.io/ | kept | 9 | ip_isr, ip_diffim, ap_association, daf_butler packages; code GPLv3 |
| Python multiprocessing docs | https://docs.python.org/3/library/multiprocessing.html | kept | 10 | spawn is the default on Windows and macOS; forkserver on POSIX since 3.14 → main guard and picklable workers (`pool_worker.py`) |

Measured: shipped completeness 0.1745 (172 detections); fixed 0.9729 / purity 0.984 (1808), identical catalogue hash `b51fb7f42583` for A/B/C. Throughput best of 3: A 166–241, B 10–19, C ~259 frames/s on 1 CPU. Fail/pass: shipped 3 failures; solution OK; fitness OK ×3.

## Lesson 18 — Time-domain alerts
**Questions:** What does a real alert packet contain? How do image-differencing methods match PSF and flux? How do brokers filter?

| Source | URL | Decision | Score | Key facts |
|---|---|---|---|---|
| ZTF Avro schemas v4.01 | https://zwickytransientfacility.github.io/ztf-avro-alert/schema.html | kept | 10 | candid, objectId, candidate {jd, ra, dec, magpsf, sigmapsf, isdiffpos, rb, fwhm}, prv_candidates (30 days), cutouts |
| lsst/alert_packet (v10.0 schema) | https://github.com/lsst/alert_packet | kept | 9 | diaSource / diaObject / prvDiaSources; MAJOR.MINOR versions; GPL-3.0 |
| DMTN-093 Rubin alert distribution | https://dmtn-093.lsst.io/ | kept | 9 | Avro; FORWARD_TRANSITIVE compatibility; Confluent wire format |
| Alard & Lupton 1998, ApJ 503, 325 | https://arxiv.org/abs/astro-ph/9712287 | kept | 11 | Kernel by linear least squares on all pixels; Gaussian basis × polynomial (our single-Gaussian simplification) |
| Zackay, Ofek & Gal-Yam 2016 (ZOGY) | https://arxiv.org/abs/1601.02655 | kept | 10 | Optimal closed-form difference statistic (named in the scaling limits) |
| Apache Avro specification | https://avro.apache.org/docs/current/specification/ | kept | 10 | JSON schemas; container file "Obj" + 1; null/deflate codecs |
| Lasair docs, Make a filter | https://lasair.readthedocs.io/en/main/core_functions/make_filter.html | kept | 8 | SQL-like filters over object attributes; Kafka delivery |
| fastavro on PyPI | https://pypi.org/project/fastavro/ | kept | 9 | 1.13.1, MIT, wheels; maintenance mode |

Measured: shipped option C 58.2 alerts/night at 4.5 % real; fixed A 9.8 (46.2 %), B 4.2 (88.2 %), C 3.5 (85.7 %). Agent gate with the fake model: 3/3 explanations blocked (V1 class mismatch; invented "2.5"). Fail/pass: shipped 2 failures (test_constant_stars_vanish, test_alert_volume_and_purity); solution OK ×3.

## Lesson 19 — Big catalogues
**Questions:** How do zone-based and HEALPix indexes answer cone searches? What are the current TAP/ADQL standards and syntax?

| Source | URL | Decision | Score | Key facts |
|---|---|---|---|---|
| Gray, Szalay et al. 2004, "There Goes the Neighborhood" (MSR-TR-2004-32) | https://arxiv.org/abs/cs/0408031 | kept | 11 | zoneNumber = floor((dec + 90)/zoneHeight); RA window widened with declination; B-tree friendly |
| Górski et al. 2005, HEALPix | https://arxiv.org/abs/astro-ph/0409513 | kept | 11 | Npix = 12 Nside², equal area π/(3 Nside²); ring and nested schemes |
| IVOA ADQL page (ADQL 2.1 REC 2023-12-15) | https://wiki.ivoa.net/twiki/bin/view/IVOA/ADQL | kept | 9 | Current REC; the coordinate-system argument optional from 2.1 (Erratum 3 page) |
| IVOA TAP 1.1 RFC page | https://wiki.ivoa.net/twiki/bin/view/IVOA/TAP11RFC | kept | 8 | "Removed REQUEST and VERSION parameters" (so no REQUEST=doQuery in the lab) |
| Gaia archive, Writing queries / Extract data | https://www.cosmos.esa.int/web/gaia-users/archive/extract-data | kept | 9 | `1 = CONTAINS(POINT('ICRS', …), CIRCLE('ICRS', …))` form; ADQL 2.1 |
| pyvo DAL docs | https://pyvo.readthedocs.io/en/latest/dal/index.html | kept | 10 | TAPService(...).search / run_sync / run_async |
| healpy.query_disc docs + healpy repo | https://healpy.readthedocs.io/en/latest/generated/healpy.query_disc.html | kept | 9 | query_disc(nside, vec, radius[rad], inclusive=…); GPL-2.0 |

The exact RA half-width α = atan(sin r / √|cos(δ−r) cos(δ+r)|) is **derived** (spherical trigonometry) and verified by code: 0 wrong cones against brute force over 600 cones. Measured: shipped 374/600 wrong; fixed A 6–11 ms, B 0.2–0.5 ms, C 0.05–0.14 ms per query. Fail/pass: shipped 8 failures; solution OK ×3.

## Lesson 20 — Model comparison (rotation curve)
| Source | URL | Decision | Score | Key facts |
|---|---|---|---|---|
| Navarro, Frenk & White 1996, ApJ 462, 563 | https://arxiv.org/abs/astro-ph/9508025 | kept | 11 | eq. 3–5 (NFW density, δc, Vc(r)/V200); quotes the cored form ρ0/(1 + (r/rc)²) |
| Freeman 1970, ApJ 160, 811 (ADS scan) | https://articles.adsabs.harvard.edu/pdf/1970ApJ...160..811F | kept | 10 | eq. 10: V²/R = πGμ0αR(I0K0 − I1K1) at ½αR. Our V² = 2GMd/Rd · y²[…] is algebra from it (with Md = 2πμ0/α², eq. 11) |
| Begeman 1989, A&A 223, 47 (university-hosted scan) | https://sites.ualberta.ca/~pogosyan/teaching/ASTRO_322/WINTER_2008/Begeman1989A+A...223...47B.pdf | kept | 9 | NGC 3198 flat within 5 km/s to 11 scale lengths; scale length 2.63 kpc |
| Lelli, McGaugh & Schombert 2016, SPARC | https://arxiv.org/abs/1606.09251 | kept | 10 | 175 galaxies; the data page states **no licence** ("please cite") → not vendored |
| Schwarz 1978, Estimating the dimension of a model | https://projecteuclid.org/journals/annals-of-statistics/volume-6/issue-2/Estimating-the-Dimension-of-a-Model/10.1214/aos/1176344136.full | kept | 9 | BIC |
| Akaike 1974 | search-result only | background | 6 | AIC (title confirmed only from search results) |
| NIST e-Handbook, Runs test | https://www.itl.nist.gov/div898/handbook/eda/section3/eda35d.htm | kept | 10 | Z = (R − R̄)/sR with R̄ and sR² formulas (`runs_z`) |

The cored-halo velocity V² = 4πGρ0rc²[1 − (rc/R) arctan(R/rc)] is **derived** by integrating the quoted density. `test_cored_halo_matches_numerical_mass_integral` verifies it; the de Blok et al. 2008 ISO section was not reached. Bessel I0, I1, K0 and K1 (series and integral) agree with tabulated values at x = 1 to 10⁻⁷; the SciPy cross-check runs in CI. V200 = 10 H r200 is derived from M200 = 200 ρcrit (4/3)π r200³ and ρcrit = 3H²/8πG (NFW). Measured: χ² picks wiggles 50/50, BIC picks the cored halo 50/50, hold-out 43/5/2. Fail/pass: shipped 12 failures; solution OK ×3.

## Lesson 21 — Open data and science software practice
| Source | URL | Decision | Score | Key facts |
|---|---|---|---|---|
| ESA Gaia data licence | https://www.cosmos.esa.int/web/gaia-users/license | kept | 11 | "Gaia data are distributed under the CC BY-NC 3.0 IGO license." (**not** CC BY-SA, as ASTRO-PLAN assumed) |
| Gaia DR3 credit and citation instructions | https://gea.esac.esa.int/archive/documentation/GDR3/Miscellaneous/sec_credit_and_citation_instructions/ | kept | 11 | Exact acknowledgement text (vendored verbatim in `inputs.py`) |
| MAST Data Use + mission acknowledgements | https://archive.stsci.edu/publishing/data-use ; https://archive.stsci.edu/publishing/mission-acknowledgements | kept | 10 | Most MAST data are public domain; the TESS acknowledgement text (first two sentences vendored) |
| IVOA DocView (VOTable 1.5 REC 2025-01-16) | https://ivoa.github.io/IvoaDocViewSite/idoc/VOTable/VOTable.html | kept | 9 | Current VOTable version. ivoa.net was blocked; DocView is "experimental … not yet officially endorsed" |
| Citation File Format 1.2.0 schema guide | https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md | kept | 10 | Required keys: authors, cff-version, message, title; file name CITATION.cff |
| SPDX License List 3.29.0 | https://spdx.org/licenses/ | kept | 10 | IDs used: CC0-1.0, CC-BY-4.0, CC-BY-SA-4.0, CC-BY-NC-4.0, CC-BY-NC-SA-4.0, MIT, BSD-3-Clause |
| Wilkinson et al. 2016, FAIR | https://pmc.ncbi.nlm.nih.gov/articles/PMC4792175/ | kept | 10 | F1, A1, I1, R1.1 ("clear and accessible data usage license") |
| Smith, Katz & Niemeyer 2016, Software citation principles (FORCE11 copy) | https://force11.org/info/software-citation-principles-published-2016/ | kept | 9 | Six principles incl. Unique Identification, Specificity |
| CC BY-SA 3.0 IGO deed | https://creativecommons.org/licenses/by-sa/3.0/igo/ | kept | 9 | ShareAlike: "distribute your contributions under the same license" (basis of the NC + SA conflict rule) |
| ASCL About | http://www.ascl.net/home/getwp/2 | kept | 8 | Citable ascl numbers for codes |
| Astropy acknowledging page | https://www.astropy.org/acknowledging.html | kept | 9 | Software acknowledgement pattern |

The licence rules are conservative defaults, not legal advice (stated in the lab, the ADR and the lesson's caution). Measured: a "files present" review catches 0/6 seeded defects and `check()` catches 6/6. Fail/pass: shipped 3 failures; solution OK.

## Capstone 22 — Transit search
| Source | URL | Decision | Score | Key facts |
|---|---|---|---|---|
| Kovács, Zucker & Mazeh 2002, BLS | https://arxiv.org/abs/astro-ph/0206099 | kept | 11 | Two-level box model; SDE > 6 for a significant detection (our threshold is 7) |
| astropy BoxLeastSquares guide + API | https://docs.astropy.org/en/stable/timeseries/bls.html | kept | 10 | Four parameters (period, duration, depth, reference time); compute_stats odd/even depths |
| lightkurve repo / search_lightcurve / flatten / BLS tutorial | https://github.com/lightkurve/lightkurve | kept | 10 | MIT; `search_lightcurve(...).download()`; `flatten` = Savitzky–Golay; `to_periodogram(method='bls')` |
| Thompson et al. 2018, Kepler DR25 Robovetter | https://arxiv.org/abs/1710.06758 | kept | 9 | Automated vetting into false-positive categories (odd/even and secondary-test wording not reached) |
| TESS FAQ (HEASARC) | https://heasarc.gsfc.nasa.gov/docs/tess/faq.html | kept | 9 | "all TESS data becomes immediately public" |
| Huang et al. 2018; Gandolfi et al. 2018 (π Men c) | https://arxiv.org/abs/1809.05967 ; https://arxiv.org/abs/1809.07573 | kept | 10 | P = 6.27 d (`fetch_tess.py` check) |
| NASA Exoplanet Archive, π Men | https://exoplanetarchive.ipac.caltech.edu/overview/pi%20Men | kept | 9 | 6.26790 ± 0.00046 d and 6.26834 ± 0.00024 d |

The duration bound T14 ≈ 13 h × (P / 1 yr)^(1/3) for a Sun-like star is **derived** (T ≈ (P/π)(R☉/a), with R☉/a = 0.00465 at 1 au), not quoted. Measured scorecard: PASS 6/6. Periods within 0.05 %, EBs rejected with reasons, depths +2.22 / −0.95 / +0.90σ, 6/6 agent explanations blocked. Capstone tests: OK ×3 (13 tests).
