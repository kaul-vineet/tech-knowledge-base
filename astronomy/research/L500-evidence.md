# L500 research evidence — Astronomy & Astrophysics, lessons 23–27 (Theory & Rigour)

Method as in SPEC.md and L100–L400-evidence.md. Sources were retrieved on 2026-10-30 with web_fetch, or read from a web_search result where marked "(search)". Each is scored 0–2 on six criteria (implementable, current, authoritative, open, transferable, right depth) and kept at ≥ 8/12. Every theorem has an independent numerical check whose real output is stored in `content/L500.json` (`checkOutput`). `research/l500_checks.py` re-runs each check and recomputes 93 numbers from the problem sets and exams. Full source rows are in `documentation/VERIFIED-RESOURCES.md`.

---

## Lesson 23 — Foundations I: mechanics, gravitation, spherical trigonometry
**Questions:** Which constants should the derivations use so that the numbers match the rest of the course? How can each formula be checked without using the formula itself? Does lesson 2's alt-az code match an independent construction?

| Source | URL | Decision | Score | Key facts used |
|---|---|---|---|---|
| IAU 2015 Resolution B3 text | https://www.pas.rochester.edu/~emamajek/IAU/IAUres_B3.pdf | kept | 11 | (GM)☉ = 1.3271244e20, (GM)⊕ = 3.986004e14 m³ s⁻²; R⊕ = 6.3781e6 m; CODATA 2014 G = 6.67408e-11 quoted |
| Mamajek et al. 2015 (arXiv:1510.07674) | https://arxiv.org/abs/1510.07674 | kept (search) | 11 | B3 adopted by the XXIXth GA; nominal values are exact conversion constants, not best estimates |
| USNO approximate sidereal time | https://aa.usno.navy.mil/faq/GAST | kept (reused from L100) | 11 | GMST rate 24.065709824279 h per day, giving a sidereal day of 86164.0905 s |
| JPL approximate planetary elements | https://ssd.jpl.nasa.gov/planets/approx_pos.html | kept (reused) | 12 | a(Mars) = 1.524 au, a(Jupiter) = 5.2026 au (lesson 11 values) |

Derivations are standard textbook results, written out in full in the lesson. The independent checks are:
- leapfrog integration of the orbit (period; measured semi-major axis for vis-viva; time-averaged virial);
- random spherical triangles compared with dot products;
- a rotation-matrix alt-az compared with `labs/L100/02-coordinates/sky.py`, imported unchanged.

**Measured:** T = 365.2569 d; leapfrog vs formula 1.3e-7; vis-viva 3.0e-8; virial 1.000000 over whole orbits, 1.249 over a quarter orbit; alt-az agreement 7e-15 deg (Deneb 56.27°); cosine-rule cancellation 0.00972″ at 0.01″.

## Lesson 24 — Foundations II: stars, radiation and the distance ladder
**Questions:** Do σ from exact constants and the nominal solar values satisfy L = 4πR²σT⁴? Which real rung-1 numbers can anchor the ladder? What happens to H₀ when the calibration is weak?

| Source | URL | Decision | Score | Key facts used |
|---|---|---|---|---|
| IAU 2015 B3 (as above) and Prša et al. 2016 | https://arxiv.org/abs/1605.09788 | kept (search) | 10 | L☉ = 3.828e26 W, R☉ = 6.957e8 m, T☉ = 5772 K (nominal) |
| Benedict et al. 2007, HST FGS Cepheid parallaxes | https://arxiv.org/abs/astro-ph/0612465 | kept (PDF text fetched) | 11 | l Car: π = 2.01 ± 0.20 mas, ⟨V⟩ = 3.724, ⟨A_V⟩ = 0.52, LKH −0.08, M_V = −5.35 ± 0.22; P-L form M = a + b(log P − 1). Table 12 coefficients were **not reached** |
| Riess et al. 2022 (SH0ES) | https://arxiv.org/abs/2112.04510 | kept (search) | 10 | 42 SN Ia hosts with Cepheids; 72.53 ± 0.99 (with TRGB) and 73.30 ± 1.04 (with high-z SNe); 5σ from Planck |
| NIST CODATA Wien constant (reused) | https://physics.nist.gov/cgi-bin/cuu/Value?bwien | kept | 12 | b = 2.897771955e-3 m K |

**Measured:** π∫B = σT⁴ to 5 digits; σ from h, k, c = 5.670374419e-8; nominal L☉ reproduced to 2.4e-6; synthetic main-sequence slope 3.481; t☉ = 10.36 Gyr; synthetic ladder H₀ = 68.68 with 8 hosts and 67.24 with one (truth 70); Monte Carlo σ_d/d = 0.0461 for σ_μ = 0.1.

## Lesson 25 — Foundations III: cosmology and Bayesian analysis
**Questions:** What H₀ and Ω_m should the lesson use, and from which primary source? Can the age be checked by two routes that do not share code? How can the course show the Hastings factor matters?

| Source | URL | Decision | Score | Key facts used |
|---|---|---|---|---|
| Planck 2018 results VI | https://arxiv.org/abs/1807.06209 | kept (search) | 11 | H₀ = 67.4 ± 0.5 km/s/Mpc, Ω_m = 0.315 ± 0.007, base flat ΛCDM |
| Metropolis et al. 1953 | https://doi.org/10.1063/1.1699114 | kept (search) | 9 | The original method: Monte Carlo over configuration space with weighting exp(−E/kT); J. Chem. Phys. 21, 1087 |
| Hubble 1929 (PMC; NASA transcription) | https://pmc.ncbi.nlm.nih.gov/articles/PMC522427/ | kept | 11 | K = +500 km/s/Mpc |

**Measured:**
- v/r = 67.4000000000 from two different observers;
- d_L small-z slope 0.762 (theory 0.764);
- 1/H₀ = 14.51 Gyr;
- ρ_c = 8.5331e-27 kg/m³ = 1.2608e11 M☉/Mpc³;
- age 13.7962 Gyr by integral, closed form and RK4 in u = a^(3/2);
- detailed balance exact on a 5-state target; total-variation distance 0.175 without Hastings vs 2.7e-14 with;
- conjugate posterior 71.696 ± 2.116 equals the grid; Metropolis gives 71.688 ± 2.098.

## Lesson 26 — Ethics: dark and quiet skies, observatory sites, open data
**Questions:** What do the UN and IAU documents actually say, and which parts are law versus recommendation? How does the primary legal record describe the Maunakea positions? What are the Gaia licence terms?

| Source | URL | Decision | Score | Key facts used |
|---|---|---|---|---|
| COPUOS A/AC.105/C.1/2026/CRP.22/Rev.1 | https://www.unoosa.org/res/oosadoc/data/documents/2026/aac_105c_12026crp/aac_105c_12026crp_22rev_1_0_html/AC105_C1_2026_CRP22Rev01E.pdf | kept (fetched) | 12 | Five-year STSC agenda item from Feb 2025; mag-7 limit from Rubin; TLEs accurate to a few arcminutes; 350 km vs 550 km (up to 40 % fewer streaks, worse at twilight); FSOA mag ≥ 7; Italian Space Law 13 June 2025; proposed EU Space Act; FCC/NSF conditions; no country had binding brightness law in 2023 (CPS report) |
| IAU CPS home and About | https://cps.iau.org/ | kept (search) | 10 | Mission: dark and radio-quiet sky for science, cultural heritage and nocturnal wildlife; launched 1 April 2022; SATCON / Dark & Quiet Skies history |
| Hawai'i Supreme Court SCOT-17-0000777 (amended opinion, 30 Nov 2018) | https://www.courts.state.hi.us/wp-content/uploads/2018/12/SCOT-17-0000777am.pdf | kept (fetched) | 12 | Appellants' and appellees' positions; cumulative adverse impacts of earlier development; "we now affirm the BLNR's decision"; Wilson, J. dissenting |
| Pollack, J. concurrence (amended) | https://www.courts.state.hi.us/wp-content/uploads/2018/12/SCOT-17-0000777conam.pdf | kept (search) | 10 | Public trust under art. XI s.1; majority holds summit conservation lands are public trust resources |
| Act 255 (2022), HB2024 | https://data.capitol.hawaii.gov/sessions/sessionlaws/Years/SLH2022/SLH2022_Act255.pdf | kept (search) | 11 | Findings ("rigid dichotomy between culture and science"); authority membership including Native Hawaiian practitioners and lineal descendants |
| Gaia licence page | https://www.cosmos.esa.int/web/gaia-users/license | kept (fetched) | 12 | "Gaia data are distributed under the CC BY-NC 3.0 IGO license"; commercial use under separate ESA terms |
| ACM Code of Ethics 2018 | https://www.acm.org/code-of-ethics | kept (fetched) | 12 | Principles 1.1–1.7, 2.1–2.9, 3.1–3.7 (headings and guidance used verbatim only for short phrases) |
| ABET EAC 2025–2026 | https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-engineering-programs-2025-2026/ | kept (fetched) | 12 | Criterion 3 outcomes (1)–(7) |

Dropped:
- COPUOS CRP.22 2025 revisions: superseded by the 2026 paper.
- LinkedIn-tracking variants of the CPS URL: duplicates.
- Secondary news coverage of Maunakea: the primary documents were preferred, for neutrality.

## Lesson 27 — Reading seminar
**Questions:** Where can both papers be read legally and free of charge? What are their licences? Which of their own numbers can a student check?

| Source | URL | Decision | Score | Key facts used |
|---|---|---|---|---|
| Hubble 1929, PMC | https://pmc.ncbi.nlm.nih.gov/articles/PMC522427/ | kept (fetched) | 11 | PNAS 15(3):168–173, doi:10.1073/pnas.15.3.168; free full text; no open licence shown |
| Hubble 1929, NASA transcription | https://science.nasa.gov/apod/a-relation-between-distance-and-radial-velocity-among-extra-galactic-nebulae/ | kept (fetched) | 11 | 24 distances; equation of condition; K = +500; NGC 7619 +3910 → 7.8e6 pc, M = −17.65; 745 km/s at 1.4e6 pc, "K of 530"; "first approximation representing a restricted range" |
| Gaia DR3 summary (arXiv) | https://arxiv.org/abs/2208.00211 | kept (fetched) | 12 | 34 months; same astrometry/photometry as EDR3; > 33 million RVs (G_RVS < 14); about 1 million RVS and about 220 million BP/RP spectra; about 10 million variables; 470 million / 1500 million APs and class probabilities; about 800,000 binaries; > 150,000 SSOs |
| Gaia DR3 summary (HAL, A&A version) | https://hal.science/hal-03857259/document | kept (search) | 11 | "Open Access article … Creative Commons Attribution License (CC BY 4.0)" |
| pnas.org DOI page; aanda.org full HTML | — | dropped | — | Fetch returned no document |
| JSTOR copy of Hubble 1929 | https://www.jstor.org/stable/85225 | dropped | 6 | Access-restricted |

## Assessment pack sources
- CS2023 knowledge areas: https://csed.acm.org/knowledge-areas/ (search). 17 knowledge areas, including MSF and SEP.
- QAA Subject Benchmark Statement, Physics, Astronomy and Astrophysics (April 2025): fetched. Paragraph 1.20 covers professional skills and ethics; paragraphs 4.4–4.6 cover the threshold and typical levels. Paraphrased in `content/assessment/syllabus.md`.
