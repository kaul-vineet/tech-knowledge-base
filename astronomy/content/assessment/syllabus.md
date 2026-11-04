# Astronomy & Astrophysics (applied) — course syllabus, L100–L500

A 14-week undergraduate course for software engineers. Labs (L100–L400) teach the practice. L500 "Theory & Rigour" (lessons 23–27) adds the foundations, ethics and primary literature that a pedagogy review found missing. Every number quoted in lessons, problem sets and exams is recomputed by code in `research/`.

## Course learning outcomes (CLO)
By the end of the course a student can:
1. **Compute** positions, times, magnitudes, orbits and spectra from first principles and check them against library implementations (L100, L23).
2. **Build** astronomical data tools (cross-match, FITS/WCS, photometry, periodograms, N-body) with tests (L200).
3. **Harden** analyses: calibrate, plan observations, plate-solve, quantify uncertainty honestly, and make pipelines reproducible (L300).
4. **Design** survey-scale systems (pipelines, alert brokers, catalogue services) with ADRs and fitness functions, and defend the design (L400, capstone).
5. **Derive and evaluate** the physics and statistics the tools rest on: mechanics and spherical trigonometry, stellar radiation and the distance ladder, cosmology and Bayesian inference (L23–L25).
6. **Analyse** the ethical, legal and social context of astronomy (dark and quiet skies, observatory sites, open data and credit) using primary sources and professional codes (L26).
7. **Read and critique** primary literature and data-release papers, and cite and license correctly (L21, L27).

## Weekly plan
| Wk | Lessons | Topic | Weekly reading (beyond the concept notes) | Due |
|---|---|---|---|---|
| 1 | 1, 2 | Workbench; coordinates and the sky | Concept notes 01–02; L23 note §"spherical cosine rule" | Lab 1–2 |
| 2 | 3, 4 | Time systems; units and magnitudes | USNO approximate sidereal time page | Lab 3–4 |
| 3 | 5, 6, **23** | Orbits; light and spectra; **Foundations I** | L23 concept note and theorems 1–4 | Lab 5–6 |
| 4 | 7, 8 | Cross-matching; FITS and WCS | Calabretta & Greisen 2002 (WCS Paper II), §1–2 | Lab 7–8, **PS 23** |
| 5 | 9, 10, **24** | Photometry; light curves; **Foundations II** | VanderPlas 2018 (Lomb–Scargle) §1–3; Benedict et al. 2007 abstract | Lab 9–10 |
| 6 | 11 | N-body (pairs: pair-programming protocol, `team-roles.md`) | L24 concept note | Lab 11, **PS 24** |
| 7 | 12 | Observation planning; **Midterm** (L1–11, L23–24) | Kasten & Young 1989 | Lab 12, **Midterm** |
| 8 | 13, 14 | Calibration frames; plate solving | Concept notes 13–14 | Lab 13–14 |
| 9 | 15, **25** | Honest uncertainty; **Foundations III** | Metropolis et al. 1953 §I–II; Planck 2018 VI abstract | Lab 15 |
| 10 | 16, 17 | Reproducible pipelines; survey pipeline (ADR 1) | Masci et al. 2019 (ZTF), §1–3 | Lab 16–17, **PS 25** |
| 11 | 18, **26** | Alert brokers; **Ethics** | COPUOS CRP.22/Rev.1 (2026); Hawai'i Supreme Court SCOT-17-0000777 (intro); Act 255 §1 | Lab 18, **Case analysis** |
| 12 | 19, 20, **27** | Big catalogues; model comparison; **Reading seminar** | Hubble 1929; Gaia DR3 summary | Lab 19–20, **Critical response** |
| 13 | 21, 22 | Open data practice; capstone build | Wilkinson et al. 2016 (FAIR); software citation principles | Lab 21, **ADRs for peer review** |
| 14 | 22 | Capstone; **oral defence**; **Final** (L1–27) | — | Capstone, defence, **Final** |

## How the levels map onto weeks
- **L100** (lessons 1–6) is covered in weeks 1–3.
- **L200** (7–11) is covered in weeks 4–6, done in pairs (`team-roles.md`).
- **L300** (12–16) is covered in weeks 7–10.
- **L400** (17–22) is covered in weeks 10–14.
- **L500** runs alongside the labs. Each Foundations lesson follows the labs that use its results: L23 after orbits and coordinates, L24 after light and photometry, L25 after MCMC is first used. L26 sits beside the alert broker it critiques. L27 comes once students can query Gaia.

## Assessment
| Component | Weight | What | Mapped CLOs |
|---|---|---|---|
| Labs | 35 % | 22 labs; each passes its tests and fitness functions; short write-up of the failure lab | 1–4 |
| Problem sets | 25 % | PS 23, 24, 25 (derivations, proofs, calculations) and the L26 case analysis and L27 critical response, marked with each lesson's rubric | 5–7 |
| Two exams | 20 % | Midterm (week 7) 8 %; final (week 14, L1–L27) 12 % — `midterm.md`, `final.md` | 1, 3, 5, 6 |
| Capstone + oral defence + peer-reviewed ADRs | 20 % | Capstone scorecard 8 %; oral defence 7 % (`capstone-oral-defence.md`); ADRs and peer reviews 5 % (`peer-review-adr.md`) | 4, 6, 7 |

**Learning gain.** The 15-item concept inventory (`concept-inventory.json`) is taken ungraded in week 1 and again in week 14. Report the normalised gain ⟨g⟩ = (post − pre)/(100 − pre), using percentages.

## Late work and academic integrity
- **Late work.** 10 % per day for up to 3 days, then 0. Each student has one 48-hour extension, no questions asked. Lab tests are run by CI at the deadline commit.
- **Integrity.** Collaboration is encouraged on labs (pairs in L200) and is acknowledged in the README. Problem sets, exams and critical responses are individual. Copying code or text without attribution, fabricating outputs (an "Expected output" that was not run), or misrepresenting results is misconduct. This includes the honesty duty of ACM Code 1.3 that the course teaches.
- **Generative AI.** It may be used to explain, never to produce submitted derivations, answers or essays. Disclose any use. Course labs that use a local model keep "code decides, agent explains" (PLATFORM-AGENT-SPEC).

## Outcome mapping to external frameworks
**ACM/IEEE-CS/AAAI CS2023 knowledge areas** (as listed at csed.acm.org/knowledge-areas):

| CLO | CS2023 knowledge areas |
|---|---|
| 1 | MSF Mathematical and Statistical Foundations; SDF Software Development Fundamentals |
| 2 | AL Algorithmic Foundations (k-d trees, periodograms); SDF; SE Software Engineering (tests) |
| 3 | MSF (statistics, MCMC); SE; DM Data Management (provenance) |
| 4 | PDC Parallel and Distributed Computing; SF Systems Fundamentals; DM; SE |
| 5 | MSF |
| 6 | SEP Society, Ethics, and the Profession |
| 7 | SEP; DM (licences, metadata) |

**ABET Criterion 3 student outcomes (1)–(7)** (EAC 2025–2026 wording, abbreviated):
- (1) solve complex problems by applying engineering, science and mathematics: CLO 1, 3, 5.
- (2) engineering design with consideration of public health, safety and welfare and global, cultural, social, environmental and economic factors: CLO 4, 6.
- (3) communicate effectively with a range of audiences: CLO 7; oral defence.
- (4) ethical and professional responsibilities and informed judgments: CLO 6.
- (5) function effectively on a team: L200 pairs, capstone team.
- (6) develop and conduct experimentation, analyse and interpret data: CLO 2, 3.
- (7) acquire and apply new knowledge: CLO 5, 7.

**Physics and astronomy programme outcomes.** The reference is the QAA Subject Benchmark Statement for Physics, Astronomy and Astrophysics (April 2025), section 4.

| Benchmark (paraphrased) | Section | CLOs |
|---|---|---|
| Apply basic physical laws and principles | 4.4 | 1, 5 |
| Solve problems with appropriate mathematical and physical techniques | 4.4 | 1, 5 |
| Use software to analyse data and simulate physical systems | 4.4 | 2–4 |
| Analyse investigations including the level of uncertainty | 4.4 | 3, 5 |
| Communicate scientific information to varied audiences | 4.4 | 6, 7 |
| Make appropriate approximations | 4.6, typical level | 5 |
| Critical, conceptual and statistical evaluation of results against models or published data | 4.6, typical level | 3, 5, 7 |
| Use mathematical and computational techniques to model physical behaviour | 4.6, typical level | 2, 5 |
| Identify potential ethical issues; never fabricate, falsify or misrepresent data | 1.20 | 6 |

Sources: CS2023 knowledge areas https://csed.acm.org/knowledge-areas/ ; ABET EAC criteria 2025–2026 https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-engineering-programs-2025-2026/ ; QAA SBS https://www.qaa.ac.uk/docs/qaa/sbs/subject-benchmark-statement-physics-astronomy-and-astrophysics-2025.pdf (all retrieved 2026-10-30).
