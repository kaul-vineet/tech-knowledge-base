# Application Architecture – 14-week undergraduate course syllabus (L100–L500)

**Format.** One 90-minute lecture/seminar and one 2-hour lab per week; about 8–10 hours of total study per week.
**Running example.** Library Loans, grown from a layered service (L100) to a production-ready, multi-tenant system (L400)
and analysed with theory (L500). **Tools.** Python 3.12 standard library on an Apple-silicon Mac mini or a Windows 11 PC;
optional open-source tools per lesson (`documentation/LEARNING-TOOLS.md`).
**Prerequisites.** One programming course (Python or similar), discrete mathematics (sets, graphs, proof by induction),
introductory probability (independence, expectation).

## How the levels map to the course
| Level | Lessons | Role in the course |
|---|---|---|
| L100 "run it" | 1–6 | Weeks 1–3: structure, boundaries, APIs, configuration, documentation |
| L200 "build it" | 7–11 | Weeks 4–6: ports and adapters, aggregates, events, authentication, testing |
| L300 "harden it" | 12–16 | Weeks 8–10: read models, resilience, contracts, SLOs, fitness functions |
| L400 "design it" | 17–22 | Weeks 11–14: decomposition, tenancy, policy, evolution, capacity, capstone |
| L500 "theory & rigour" | 23–27 | Threaded through weeks 3–12: the theory each practical block rests on, ethics, primary literature |

## Weekly plan
| Week | Lessons (lab) | Theory / seminar | Reading (before class) | Due |
|---|---|---|---|---|
| 1 | 1 Set up; 2 Layered structure | What is architecture; quality vs function | L100 concept notes 1–2 | Lab 1 |
| 2 | 3 Modular monolith; 4 API-first OpenAPI | Information hiding (intro) | Parnas 1972, first half (lesson 27 reading 1) | Lab 2 |
| 3 | 5 Configuration; 6 Documenting (C4, ADR) | **L500 #23 Foundations I** (graphs, layering ⇔ acyclic, Martin metrics) | Concept note 23 | Labs 3–4 |
| 4 | 7 Hexagonal architecture | Dependency inversion; metrics on the lab code | Martin 1994 | Labs 5–6; PS23 (problem set 23) |
| 5 | 8 Aggregates and invariants; 9 Event-driven integration | Contracts and invariants (first half of #25) | Concept note 25 §Definitions | Lab 7 |
| 6 | 10 OIDC; 11 Testing pyramid | Pair-programming retrospective | L200 concept notes 10–11 | Labs 8–9 |
| 7 | **Midterm exam** (L100–L200 + #23) | **L500 #24 Foundations II** (quality attributes, availability maths) | Concept note 24; ISO/IEC 25010:2023 foreword | Labs 10–11 |
| 8 | 12 CQRS read models; 13 Resilience | Series/parallel availability on Library Loans | Treynor et al. 2017 | PS24 |
| 9 | 14 Consumer-driven contracts; 15 SLOs and error budgets | Nines → downtime; MTTF/MTTR | SRE chapter linked in lesson 15 | Labs 12–13 |
| 10 | 16 Fitness functions in CI | **L500 #25 Foundations III** (Liskov, model checking, evidence) | Liskov & Wing 1994 §1–2; concept note 25 | Labs 14–15 |
| 11 | 17 Strangler fig; 18 Multi-tenancy | **L500 #26 Ethics** seminar (case analysis) | ACM Code 2018; WCAG 2.2 "What's new"; GDPR Art. 25 | Lab 16; PS25 |
| 12 | 19 Policy as code; 20 Evolutionary migrations | **L500 #27 Reading seminar** (Parnas; SEI ATAM) | Both readings in full | Labs 17–18; case analysis (#26) |
| 13 | 21 Capacity planning; capstone build | Mini-ATAM of the capstone; ADR writing | ATAM report §5–7 | Labs 19–21; critical response (#27); ADRs for peer review |
| 14 | 22 Capstone | **Oral defence**; course review | Own ADRs and peer reviews | Capstone; peer reviews; **final exam** (exam week) |

## Assessment
| Component | Weight | What | Where |
|---|---|---|---|
| Labs | 35 % | 21 labs (lessons 2–22), each passes its `unittest` suite and the build task (`CHECK_MINE=1`); short lab reflection | `labs/` |
| Problem sets | 25 % | Five L500 problem sets (lessons 23–27): proofs, derivations, calculations checked by code, essays; the #26 case analysis and #27 critical response count here | `content/L500.json` |
| Two exams | 20 % | Midterm 10 % (week 7, L100–L200 + #23), final 10 % (L100–L500) | `midterm.md`, `final.md` |
| Capstone + oral defence + peer-reviewed ADRs | 20 % | Capstone scorecard GO and fault drills 10 %; oral defence 6 %; ADRs written and peer-reviewed 4 % | `capstone-oral-defence.md`, `peer-review-adr.md`, `team-roles.md` |

The concept inventory (`concept-inventory.json`, 15 items) is taken in week 1 and again in week 14. It is **not graded**;
the normalised gain ⟨g⟩ = (post − pre)/(100 − pre) is used to evaluate the course, not the student.

## Course learning outcomes (CLO)
| CLO | By the end, students can … | Lessons | CS2023 knowledge areas | ABET CAC (computing) | ABET EAC (engineering) |
|---|---|---|---|---|---|
| 1 | Decompose a service into modules, layers and ports, and prove/enforce boundary properties with fitness functions | 2, 3, 7, 16, 23 | SE, SDF, MSF | 1, 2, 6 (CS) | 1, 2 |
| 2 | Design integration with explicit contracts and idempotent event handling | 4, 9, 12, 14 | SE, PDC | 2, 6 (CS) | 2 |
| 3 | Specify quality attributes as measurable scenarios and evaluate trade-offs | 15, 16, 21, 24 | SE, SF | 1, 2 | 1, 2, 6 |
| 4 | Quantify reliability and performance (availability, SLOs, capacity) with stated assumptions | 13, 15, 21, 24 | SE, PDC, MSF | 1, 6 (CS) | 1, 6 |
| 5 | Reason formally about correctness (contracts, invariants, substitution, model checking) and judge empirical claims | 8, 25 | SE, FPL, MSF | 1, 6 (CS) | 1, 6, 7 |
| 6 | Secure and govern multi-tenant systems (authentication, policy, isolation) | 10, 18, 19 | SEC, SE | 2 | 2, 4 |
| 7 | Communicate and defend architecture (C4, ADRs, oral defence, peer review) as a team | 6, 22, capstone | SE, SEP | 3, 5 | 3, 5 |
| 8 | Act on professional responsibilities: accessibility, privacy by design, honest reporting | 26, 27 | SEP, HCI, SEC | 4 | 4, 7 |

**CS2023** knowledge-area abbreviations (ACM/IEEE-CS/AAAI, https://csed.acm.org/knowledge-areas/): SE Software
Engineering, SDF Software Development Fundamentals, MSF Mathematical and Statistical Foundations, PDC Parallel and
Distributed Computing, SF Systems Fundamentals, FPL Foundations of Programming Languages, SEC Security, SEP Society,
Ethics, and the Profession, HCI Human-Computer Interaction.

**ABET** (verified 2026-10-30 against the 2026–2027 criteria; paraphrased because ABET does not permit reproduction):
- *Computing Accreditation Commission* (CS and similar programmes): general outcomes 1–5 – (1) analyse a complex
  computing problem and apply computing principles to identify solutions; (2) design, implement and evaluate a computing
  solution against requirements; (3) communicate effectively in professional contexts; (4) recognise professional
  responsibilities and make informed judgements based on legal and ethical principles; (5) function effectively as a
  member or leader of a team – plus the computer-science programme outcome (6): apply computer-science theory and
  software-development fundamentals to produce solutions. The CAC general criteria have five outcomes, not seven.
- *Engineering Accreditation Commission* (software-engineering programmes accredited as engineering): outcomes 1–7 –
  (1) solve complex engineering problems with engineering, science and mathematics; (2) apply engineering design with
  consideration of public health, safety, welfare and wider factors; (3) communicate with a range of audiences;
  (4) recognise ethical and professional responsibilities and judge impacts in global, economic, environmental and
  societal contexts; (5) function on a team that leads, collaborates, sets goals and meets objectives; (6) develop and
  conduct experimentation, analyse data and use judgement; (7) acquire and apply new knowledge with appropriate
  learning strategies.
Sources: https://www.abet.org/wp-content/uploads/2025/12/2026-2027_CAC_Criteria.pdf and
https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-engineering-programs-2026-2027/.
Programmes must use the binding wording from those documents in their own self-study.

## Policies
**Late work.** Labs and problem sets: 10 % deducted per started day late, up to 3 days; after that 0 unless an extension
was agreed before the deadline. Exams and the oral defence are rescheduled only for documented reasons.
Each student has one 48-hour "no questions asked" extension for one problem set.

**Academic integrity.** Labs may be done in pairs (see `team-roles.md`); problem sets, the case analysis, the critical
response and exams are individual. You may discuss ideas; you may not share written solutions or code for individual
work. Quote sources with quotation marks and a citation; paraphrase with a citation (ACM Code 1.5). Do not reproduce
copyrighted readings.

**Generative AI and local models.** The course's rule applies to you too: *the model proposes, code and you decide*.
You may use a local model (lessons 6, 9, 15, 21, 22) to draft or explain, but you must (1) say where you used it,
(2) verify every number and claim it produces – calculations must be reproduced by code you can run, and (3) be able to
explain every line in the oral defence. Undisclosed use in individual assessments is an integrity breach.

**Accessibility.** Course materials are plain text, Markdown, JSON and code. Request adjustments (extra time, alternative
formats, alternative to the oral defence format) through the disability office; the oral defence can be held in writing
or with extra time without penalty.
