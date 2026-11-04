# Simulation for software engineers - 14-week syllabus (L100-L500)

Audience: second- or third-year undergraduates in computing or engineering who can program in Python. The course is applied and example-led. Every week has a lab that runs locally (Python 3.12 + numpy, on macOS or Windows; see lesson 1). The L500 lessons supply the theory, ethics and primary literature behind the labs.

Prerequisites:
- programming in Python (functions, lists, dictionaries, unittest)
- calculus: derivatives, integrals, Taylor series
- introductory probability: expectation, variance, independence
- linear algebra: matrices and solving linear systems

Each L500 lesson lists the mathematics it assumes in `prerequisites`.

## Weekly plan

"Reading" means a concept note in `content/concepts/` plus the named primary source. Lesson numbers refer to `content/L100.json` … `content/L500.json`.

| Wk | Labs (hands-on) | Theory / ethics / reading (L500) | Weekly reading | Due |
|---|---|---|---|---|
| 1 | L100 #1 Setup, #2 Monte Carlo | #23 part 1: LLN (Chebyshev proof), CLT | Grinstead & Snell ch. 8-9 (sections on LLN, CLT) | Concept inventory **pre-test**; lab 2 |
| 2 | L100 #3 Discrete-event queue | #23 part 2: Poisson process, Markov chains, M/M/1 from cut balance | Gallager 6.262 ch. 2 (Poisson); MIT 2.854 M/M/1 notes | Lab 3; problem set 23 (Q1-Q5) |
| 3 | L100 #4 Time-stepped physics | #24 part 1: Euler O(h), RK4 O(h^4) | Verschelde MCS 471 RK notes | Lab 4; problem set 23 (Q6-Q9) |
| 4 | L100 #5 Agent-based, #6 V&V | #27 reading 2: Sargent (2010) | Sargent WSC 2010 (sections on definitions, process, techniques) | Labs 5-6; reading questions (Sargent) |
| 5 | L200 #7 Input modelling, #8 Erlang C | #23 revisited: cut balance for M/M/c | NIST e-Handbook KS and chi-square pages | Labs 7-8 (build tasks, **pairs**) |
| 6 | L200 #9 Adaptive ODEs | #24 part 2: stability regions, stiffness, floating point | Princeton COS 323 lect. 19; Goldberg (1991) sections on rounding error | Lab 9; problem set 24 |
| 7 | L200 #10 Warm-up and replications, #11 CRN inventory | Revision | Course notes | Labs 10-11; **Midterm** (weeks 1-7) |
| 8 | L300 #12 Variance reduction | #25 part 1: MC variance, importance sampling, antithetics | Owen ch. 8-9 (via the author's site) | Lab 12 (failure lab) |
| 9 | L300 #13 Calibration, #14 Global sensitivity | #27 reading 1: Metropolis & Ulam (1949) | Metropolis & Ulam (JSTOR) | Labs 13-14; critical response 1 |
| 10 | L300 #15 Co-simulation, #16 Performance and scale | #25 part 2: LCGs, RANDU, PCG64/Philox, generator tests | Hull & Dobell (1962) §1-2; Salmon et al. (2011) §1-3 | Labs 15-16; problem set 25 |
| 11 | L400 #17 Digital twin, #18 Simulation optimisation | ADR writing and **peer review round 1** (`peer-review-adr.md`) | NASA-STD-7009B front matter | Labs 17-18; ADR 1 + reviews |
| 12 | L400 #19 Surrogates, #20 Parallel scale, #21 Governance | #26 ethics seminar: case analysis | Ofqual interim report (executive summary); OSR (2021) summary; ACM Code | Labs 19-21; case analysis (26-P5) |
| 13 | L400 #22 Capstone (team build) | ADR **peer review round 2** | AQuA Book (2025) roles and proportionality sections | Capstone milestones M1-M4; critical response 2 |
| 14 | Capstone M5-M6, oral defences | Revision | - | Capstone + **oral defence**; **Final exam** (L100-L500); concept inventory **post-test** |

## Assessment

| Component | Weight | What | Where |
|---|---|---|---|
| Labs | 35% | 20 graded labs (L100 #2 - L400 #21). Each lab is pass/merit/distinction: tests pass; tryIt predictions recorded; build or failure task fixed with a test; ADR where required | each lesson's `checkpoint`, `buildTask`, `failureLab`, `fitnessFunction` |
| Problem sets | 25% | L500 #23, #24 and #25 problem sets (proofs, derivations and calculations; numbers reproduced in code) plus #26 case analysis and #27 critical responses | `problemSet` + `rubric` in content/L500.json |
| Two exams | 20% | Midterm 8% (weeks 1-7), final 12% (L100-L500) | `midterm.md`, `final.md` |
| Capstone + oral defence + peer-reviewed ADRs | 20% | Team capstone (L400 #22) 10%, individual oral defence 6%, two peer-reviewed ADRs 4% | `capstone-oral-defence.md`, `peer-review-adr.md`, `team-roles.md` |

The concept inventory (`concept-inventory.json`, 15 items) is **not graded**. It runs as a pre-test in week 1 and as a post-test in week 14. Report the class-average normalised gain g = (post − pre)/(100 − pre). Items target the misconceptions listed in the concept notes.

## Policies

- **Late work.** Up to 72 hours late: 10% deducted per 24 hours. After that the mark is 0, unless an extension was agreed beforehand. Two "grace days" may be used on labs only (not exams, not the capstone). Problem-set solutions are released one week after the deadline, so no work is accepted after release.
- **Academic integrity.** Work in pairs only where the syllabus says so (L200 build tasks, using the protocol in `team-roles.md`). Write proofs and essays individually. Cite every source. Do not reproduce copyrighted papers (the two readings are summarised, never copied).
- **AI tools.** Code assistants and local models (lesson 1's optional Ollama) may be used for labs if declared in the README. The course rule holds everywhere: *deterministic code decides; a model may propose or explain; every model output is checked by code.* Proofs, case analyses and critical responses must be your own writing. The oral defence checks that you understand what you submitted.
- **Reproducibility.** Every reported number must come from seeded code that the marker can re-run. Numbers that cannot be reproduced score zero for that item.
- **Accessibility.** All labs run on a laptop without a GPU. Ask for exam adjustments through the usual channel.

## Course learning outcomes and mappings

CS2023 knowledge areas are taken from the ACM/IEEE-CS/AAAI *Computer Science Curricula 2023* knowledge-area list (csed.acm.org/knowledge-areas, retrieved 2026-10-30). ABET outcomes are paraphrased from *Criteria for Accrediting Engineering Programs 2025-2026* (EAC, outcomes 1-7) and *Criteria for Accrediting Computing Programs 2026-2027* (CAC, outcomes 1-5, plus CS outcome 6). Both pages were retrieved 2026-10-30. The EAC 2026-27 wording was not opened, so check it before an accreditation submission.

| # | Learning outcome (students will be able to…) | Evidence | CS2023 KAs | ABET EAC (1-7) | ABET CAC/CS (1-6) |
|---|---|---|---|---|---|
| LO1 | Build and run Monte Carlo, discrete-event, time-stepped and agent-based models, and report results with honest uncertainty | Labs L100-L200; midterm | SDF Software Development Fundamentals; MSF Mathematical and Statistical Foundations | 1, 6 | 1, 2, 6 |
| LO2 | Derive and prove the probability and numerical results the models rely on (LLN, CLT, Poisson, birth-death balance, truncation error order, stability, floating point) | L500 #23-24 problem sets; exams | MSF; AL Algorithmic Foundations | 1, 7 | 1, 6 |
| LO3 | Design efficient, reproducible stochastic experiments: generators and streams, variance reduction, replications, parallel runs | L300 #12/#16, L400 #20, L500 #25 | MSF; PDC Parallel and Distributed Computing; SF Systems Fundamentals | 1, 6 | 1, 2, 6 |
| LO4 | Verify, validate, calibrate and govern models against an accuracy requirement for an intended use, and record decisions in ADRs | L100 #6, L300 #13-14, L400 #21, capstone, ADR peer review | SE Software Engineering; MSF | 2, 6 | 2, 4 |
| LO5 | Evaluate the ethical, social and professional implications of model-informed decisions about people, citing codes and standards | L500 #26 case analysis; final Q7 | SEP Society, Ethics, and the Profession | 2, 4 | 4 |
| LO6 | Work in a team on an integrated model, explain and defend it orally, and review peers' design decisions | Capstone, oral defence, peer-reviewed ADRs | SE; SEP | 3, 5 | 3, 5 |
| LO7 | Read primary literature critically and relate it to current practice | L500 #27 critical responses | SEP; MSF | 7 | 4 |

Paraphrased ABET EAC outcomes (2025-26):
1. Identify, formulate and solve complex engineering problems.
2. Apply engineering design with consideration of public health, safety and welfare, and global, cultural, social, environmental and economic factors.
3. Communicate effectively with a range of audiences.
4. Recognise ethical and professional responsibilities and make informed judgments.
5. Function effectively on a team.
6. Develop and conduct appropriate experimentation, analyse and interpret data, and use engineering judgment.
7. Acquire and apply new knowledge using appropriate learning strategies.

Paraphrased ABET CAC outcomes (2026-27):
1. Analyse complex computing problems.
2. Design, implement and evaluate solutions.
3. Communicate in professional contexts.
4. Recognise professional responsibilities and make judgments based on legal and ethical principles.
5. Function on a team.
6. (CS) Apply computer-science theory and software development fundamentals.

## How the levels map to the weeks
- **L100 "Run it"**: weeks 1-4.
- **L200 "Build it"**: weeks 5-7. Pairs, with the protocol in `team-roles.md`.
- **L300 "Harden it"**: weeks 8-10.
- **L400 "Design it" + capstone**: weeks 11-14.
- **L500 "Theory & rigour"**: runs alongside, so the theory arrives just before or with the lab that uses it.
  - #23 Probability: weeks 1-2, revisited in week 5.
  - #24 Numerical methods: weeks 3 and 6.
  - #25 Random numbers and Monte Carlo: weeks 8 and 10.
  - #26 Ethics: week 12.
  - #27 Readings: weeks 4 and 9.
