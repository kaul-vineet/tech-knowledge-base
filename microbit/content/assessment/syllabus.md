# micro:bit physical computing — course syllabus (14 weeks, L100–L500)

**Level:** undergraduate, second or third year. **Load:** about 10 hours per week (3 h contact: 1 h lecture/seminar, 2 h lab; 7 h independent).
**Hardware:** none required. All labs run on the CPython stub (`labs/sim_stub`) and the online MicroPython simulator; a BBC micro:bit V2 is optional (see `documentation/HARDWARE.md`).
**Status:** the labs are validated against the stub only (`validated-stub`); simulator and Mac/Windows CI runs are pending (see `documentation/KNOWN-GAPS.md`).

## Course learning outcomes (CLO)
By the end, a student can:
1. **Build** micro:bit programs that sense, actuate, log and communicate, and test them without hardware (L100–L200).
2. **Analyse** failures — lost frames, blocking loops, flat batteries, races — and harden designs with evidence (L300).
3. **Design and evaluate** a multi-board edge-to-cloud system with explicit trade-offs, ADRs and fitness checks (L400).
4. **Derive and verify** the theory the designs rest on: number representation, quantisation, PWM, sampling, filtering, feedback control, real-time scheduling and CRCs (L500 #23–25).
5. **Evaluate** the ethical, legal, environmental and accessibility consequences of classroom physical computing (L500 #26).
6. **Read and critique** primary literature and connect its assumptions to practice (L500 #27).
7. **Communicate and collaborate**: ADRs, peer review, an oral defence and team roles.

## Weekly plan
| Week | Topic and lessons | Lab / assessment due | Reading (before the session) |
|---|---|---|---|
| 1 | Set-up, LED display, buttons — L100 #1–3 | Labs 1–3 | Concept notes 01–03 |
| 2 | Sound, temperature and light, motion — L100 #4–6 | Labs 4–6 | Concept notes 04–06 |
| 3 | Radio between boards, data logging — L200 #7–8 | Labs 7–8 | Concept notes L200/07–08 |
| 4 | Pins and PWM, I²C sensor, state machine — L200 #9–11; pair programming | Labs 9–11 | Concept notes L200/09–11 |
| 5 | **Foundations I** — L500 #23 (two's complement, Ohm/KVL, quantisation, PWM) | Problem set 23 | Concept note L500/23 |
| 6 | Reliable radio, non-blocking scheduler — L300 #12–13; **Foundations II** — L500 #24 | Labs 12–13 | Concept notes L300/12–13, L500/24 |
| 7 | Power budget, serial gateway — L300 #14–15 | Labs 14–15, problem set 24; **midterm (end of week)** | Concept notes L300/14–15 |
| 8 | Interrupt race (Rust/Embassy sibling) — L300 #16; **Foundations III** — L500 #25 | Lab 16 | Concept notes L300/16, L500/25 |
| 9 | Edge-to-cloud, fleet configuration — L400 #17–18 | Labs 17–18, problem set 25; ADR 1 | Concept notes L400/17–18 |
| 10 | Authenticated frames, digital twin — L400 #19–20 | Labs 19–20; ADR 2 | Concept notes L400/19–20 |
| 11 | Local AI at the edge — L400 #21; **Ethics** — L500 #26 | Lab 21; case analysis (26.6) | Concept note L500/26 + its primary sources |
| 12 | **Reading seminar** — L500 #27; capstone kick-off — L400 #22 | Two critical responses (27.5, 27.6) | Shannon 1949; Liu & Layland 1973 |
| 13 | Capstone build; peer review of ADRs | ADR peer reviews (`peer-review-adr.md`) | `team-roles.md` |
| 14 | Capstone oral defence; **final exam** | Capstone + defence (`capstone-oral-defence.md`) | Revise |

## How L100–L500 map to the weeks
L100 weeks 1–2; L200 weeks 3–4; L300 weeks 6–8; L400 weeks 9–13; L500 is interleaved where its theory is used: #23 after PWM and I²C (week 5), #24 with the scheduler and logger (week 6), #25 with the interrupt race (week 8), #26 before the capstone (week 11), #27 in week 12. The concept inventory (`concept-inventory.json`, 15 items) is taken in week 1 (pre) and week 14 (post); report the normalised gain (post − pre)/(100 − pre).

## Assessment
| Component | Weight | Notes |
|---|---|---|
| Labs (L100–L400, 22 labs) | 35 % | Each lab: tests pass on the stub (40 %), README with real output (30 %), short reflection on one failure (30 %). |
| Problem sets (L500 #23–27) | 25 % | 5 sets, 5 % each; graded with each lesson's `rubric`. Numeric answers must be reproduced by code. |
| Two exams | 20 % | Midterm 8 % (`midterm.md`), final 12 % (`final.md`); closed book, one A4 formula sheet. |
| Capstone, oral defence, peer-reviewed ADRs | 20 % | Capstone system 10 %, oral defence 5 %, ADRs + peer reviews 5 %. |

## Policies
- **Late work:** 10 % of the component's marks per calendar day, up to 3 days; after that 0 unless an extension was agreed before the deadline. Exams and the oral defence cannot be late.
- **Integrity:** submitted code and text must be your own or your team's, with every external source cited. Pair programming in L200 and the team capstone follow `team-roles.md`; individual problem sets are individual.
- **AI assistants:** allowed for explanation, in the spirit of lesson 21 ("it explains, code decides"). Disclose use in a one-line note; every numeric answer must come from code you ran; never paste a model's proof as your own.
- **Data and safety:** only synthetic or your own non-personal data; no data about other students (lesson 26). If you use real boards, follow the micro:bit safety guidance and lesson 14's battery notes.

## Mapping to ACM/IEEE-CS/AAAI CS2023 knowledge areas
CS2023 lists 17 knowledge areas (https://csed.acm.org/knowledge-areas/). This course covers:
| Knowledge area | Where |
|---|---|
| SPD Specialized Platform Development | All labs (embedded MicroPython on a constrained board) |
| SF Systems Fundamentals | L300 #13–14 (scheduling, resource budgets), L500 #25 |
| AR Architecture and Organization | L500 #23 (number representation), L200 #10 (registers) |
| OS Operating Systems | L300 #13, #16, L500 #25 (scheduling, concurrency) |
| NC Networking and Communication | L200 #7, L300 #12, #15, L500 #25 (CRC) |
| PDC Parallel and Distributed Computing | L400 #17–20 (multi-board network) |
| SEC Security | L400 #19 (authenticated frames), L500 #25.8 |
| MSF Mathematical and Statistical Foundations | L500 #23–25 |
| SE Software Engineering | Tests in every lab, ADRs, fitness functions (L400) |
| HCI Human-Computer Interaction | L500 #26 (accessibility) |
| AI Artificial Intelligence | L400 #21 (local model, code decides) |
| SEP Society, Ethics, and the Profession | L500 #26–27 |
| SDF Software Development Fundamentals | L100–L200 |

## Mapping to ABET student outcomes
Wording verified on 2026-10-30 against ABET's *Criteria for Accrediting Engineering Programs, 2025–2026* (Criterion 3, outcomes 1–7). A computing programme uses ABET's *Criteria for Accrediting Computing Programs, 2025–2026* (outcomes 1–5, plus outcome 6 for computer science); the right column maps those.
| ABET EAC outcome (abridged) | Course evidence | CAC outcome |
|---|---|---|
| 1 Identify, formulate and solve complex engineering problems (engineering, science, mathematics) | L500 #23–25 proofs and problem sets; L300 failure labs | 1 (analyse a complex computing problem); CS 6 (apply CS theory) |
| 2 Apply engineering design with consideration of public health, safety, welfare, global, cultural, social, environmental, economic factors | L400 design briefs, capstone; L500 #26 battery/e-waste | 2 (design, implement, evaluate) |
| 3 Communicate effectively with a range of audiences | READMEs, ADRs, oral defence | 3 |
| 4 Recognise ethical and professional responsibilities; informed judgments | L500 #26 case analysis | 4 (professional responsibilities, legal and ethical principles) |
| 5 Function effectively on a team | Capstone roles, ADR peer review, L200 pair programming | 5 |
| 6 Develop and conduct experimentation, analyse and interpret data | Every lab's tests and outputs; L500 numerical checks | 1, 2 |
| 7 Acquire and apply new knowledge using appropriate learning strategies | L500 #27 reading seminar; learning tools | — (programme-defined) |

Sources: https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-engineering-programs-2025-2026/ and https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-computing-programs-2025-2026/ (both retrieved 2026-10-30). The mapping is the course team's proposal, not an accreditation decision.
