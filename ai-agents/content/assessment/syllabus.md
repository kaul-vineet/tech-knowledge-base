# AI Agents – applied engineering with foundations: 14-week syllabus

**Level:** upper-undergraduate (year 3) or conversion master's. **Workload:** about 10 hours/week (2 h lecture, 2 h lab, 6 h independent work). **Prerequisites:** programming in Python; introductory probability and statistics; linear algebra (matrix multiplication); discrete mathematics. **Platforms:** an Apple-silicon Mac mini or a Windows 11 PC; every lab runs offline against the deterministic fake model server, optionally against a local model (Ollama / llama.cpp) – see `documentation/HARDWARE.md`.

The course alternates *practice* (L100 run it → L200 build it → L300 harden it → L400 design it) with *theory* (L500): each L500 foundations lesson comes right after the labs whose behaviour it explains, so students prove what they have already observed.

## Weekly plan

| Week | Lessons | Theme | Reading (before class) | Assessed work due |
|---|---|---|---|---|
| 1 | L100 #1–3 | Setup; calling a model; prompt structure | `documentation/CONCEPTS-PRIMER.md`; concept notes 01–03 | Lab 1 (setup check) |
| 2 | L100 #4–6 | Structured output; tool calls; the agent loop | Concept notes 04–06; Yao et al. 2023 abstract + Sec. 1–2 | Labs 2–3 |
| 3 | **L500 #23** | Foundations I: how language models work | Concept note L500/23; Vaswani et al. 2017 Sec. 3.2; Jurafsky & Martin ch. 3 §3.1–3.4 | Lab 4–6; team formation (`team-roles.md`) |
| 4 | L200 #7–8 | Retrieval; several tools with schemas | Concept notes L200/07–08 | Problem set 23 |
| 5 | L200 #9–11 | Memory; MCP; guardrails | Concept notes L200/09–11 | L200 labs (pair-programmed, `team-roles.md` §3) |
| 6 | L300 #12, **L500 #24** | Golden sets; statistics for evaluation | Concept notes L300/12, L500/24; NIST e-Handbook 7.2.4.1 | L300 lab 12 |
| 7 | L300 #13; **midterm** | Tracing; midterm (L100–L300 #14, L500 #23–24) | Concept note L300/13 | Problem set 24; midterm (`midterm.md`) |
| 8 | L300 #14–15 | Reliability budgets; safe tool execution | Concept notes L300/14–15 | Labs 13–14 |
| 9 | **L500 #25**, L300 #16 | Decision theory and planning; red-teaming | Concept note L500/25; Sutton & Barto ch. 3; Hart et al. 1968 (abstract) | Lab 15 |
| 10 | L400 #17–18 | Multi-agent patterns; durable workflows | Concept notes L400/17–18 | Problem set 25; Lab 16; ADR 1 draft |
| 11 | L400 #19–20 | Cost and model choice; deterministic core | Concept notes L400/19–20 | Labs 17–18; ADR 1 peer review (`peer-review-adr.md`) |
| 12 | **L500 #26**, L400 #21 | Ethics and professional responsibility; governance | Concept note L500/26; ACM Code 2018; AI Act Art. 14 and 50; Moffatt v. Air Canada | Case analysis (lesson 26); Labs 19–20 |
| 13 | **L500 #27**, L400 #22 | Reading seminar; capstone build | Both papers in full (three-pass method) | Critical response (lesson 27); ADR 2–3 peer review; Lab 21 |
| 14 | L400 #22 | Capstone demonstration, oral defence; final exam | – | Capstone + oral defence (`capstone-oral-defence.md`); final exam (`final.md`) |

## How the levels map to weeks
- **L100 (weeks 1–2):** run it – every student gets a working loop against the fake server, then a local model.
- **L200 (weeks 4–5):** build it – one feature per lab with a test; pair programming.
- **L300 (weeks 6–9):** harden it – seeded failure labs, each with a failing proof test that the fix turns green.
- **L400 (weeks 10–14):** design it – ADRs, fitness functions, the capstone.
- **L500 (weeks 3, 6, 9, 12, 13):** theory, ethics and primary literature, each placed after the practice it explains.

## Assessment

| Component | Weight | What | Notes |
|---|---|---|---|
| Labs | 35 % | 22 lab submissions (L100–L400): code + test output + short reflection | Graded pass / merit / distinction on the lab's checkpoint, tests and trade-off answers; lowest two dropped |
| Problem sets | 25 % | L500 #23, #24, #25 problem sets (7 % each) and the lesson 26 case analysis + lesson 27 critical response (2 % each) | Graded with each lesson's `rubric`; calculation answers must be reproducible with code |
| Two exams | 20 % | Midterm (week 7, 8 %), final (week 14, 12 %) | Closed book with a notes sheet; model answers in `midterm.md`, `final.md` |
| Capstone, oral defence and peer-reviewed ADRs | 20 % | Capstone system and scorecard (10 %), 20-minute oral defence (6 %), three ADRs with peer review given and received (4 %) | `capstone-oral-defence.md`, `peer-review-adr.md`; team roles in `team-roles.md` |

A **concept inventory** (`concept-inventory.json`, 15 items) is taken in week 1 (pre) and week 14 (post) and is not graded; normalised gain ⟨g⟩ = (post − pre)/(100 − pre) is reported to the class and used to revise the course.

## Learning outcomes
On completion students can:

| # | Outcome | CS2023 knowledge areas | ABET CAC student outcomes (computing, 2025–26) | ABET EAC student outcomes (engineering, 2025–26) |
|---|---|---|---|---|
| LO1 | Build a tool-using agent loop with structured output, budgets and tests against a local model | AI, SDF, SE | 2, 6 (CS) | 1, 2 |
| LO2 | Derive and explain the probability and linear algebra behind next-token generation and decoding | AI, MSF | 1, 6 (CS) | 1 |
| LO3 | Evaluate agents with golden sets and correct statistics (intervals, power, paired tests, multiple comparisons) | AI, MSF, SE | 1, 2 | 6 |
| LO4 | Harden agents against faults and prompt injection; enforce capability boundaries | SEC, SE, PDC | 2 | 1, 2 |
| LO5 | Make and record design decisions (ADRs, fitness functions) using expected utility, MDP and search arguments | SE, AI, AL | 1, 2, 3 | 2, 3, 6 |
| LO6 | Analyse accountability, oversight, fairness, privacy and transparency obligations using primary law and professional codes | SEP, HCI | 4 | 4 |
| LO7 | Read, summarise and critique primary research papers | AI, SEP | 1, 3 | 3, 7 |
| LO8 | Work in a team with defined roles, peer review and pair programming | SE, SEP | 5 | 5 |

**CS2023** knowledge-area abbreviations are those of the ACM/IEEE-CS/AAAI CS2023 report (https://csed.acm.org/knowledge-areas/, checked 2026-10-30): AL Algorithmic Foundations, AI Artificial Intelligence, HCI Human-Computer Interaction, MSF Mathematical and Statistical Foundations, PDC Parallel and Distributed Computing, SDF Software Development Fundamentals, SE Software Engineering, SEC Security, SEP Society, Ethics, and the Profession.

**ABET.** Wording checked on 2026-10-30 against *Criteria for Accrediting Computing Programs, 2025–2026* and *Criteria for Accrediting Engineering Programs, 2025–2026*. Computing (CAC) programmes have outcomes 1–5 for all programmes plus a programme-specific outcome; for computer science this is outcome 6. CAC: (1) analyze a complex computing problem and apply principles of computing and other relevant disciplines to identify solutions; (2) design, implement, and evaluate a computing-based solution to meet a given set of computing requirements; (3) communicate effectively in a variety of professional contexts; (4) recognize professional responsibilities and make informed judgments in computing practice based on legal and ethical principles; (5) function effectively as a member or leader of a team; (6, CS) apply computer science theory and software development fundamentals to produce computing-based solutions. Engineering (EAC) programmes use outcomes 1–7: (1) solve complex engineering problems; (2) engineering design with consideration of public health, safety, welfare and wider factors; (3) communicate with a range of audiences; (4) ethical and professional responsibilities; (5) function effectively on a team; (6) develop and conduct experimentation, analyze and interpret data; (7) acquire and apply new knowledge. Use the CAC column for a computing degree and the EAC column for an engineering degree (e.g. software engineering accredited by EAC). The mapping is the course team's proposal, not an ABET determination.

## Policies

**Late work.** Labs and problem sets: −10 % of the mark per calendar day late, up to 3 days; after that, 0 unless an extension was agreed before the deadline. The capstone demonstration and exams cannot be late; documented illness or emergencies are handled by the institution's mitigating-circumstances process.

**Academic integrity.**
- Work you submit must be your own (or your team's, for team items). Cite every source; quote sparingly with quotation marks; never paste text from papers, standards or statutes as your own. Reading responses must summarise in your own words.
- **AI assistants.** You may use a local or hosted model as a tutor or to draft code, as the course itself does – under the same boundary the course teaches: *you* decide, *code* checks. Disclose any assistant use in a short "assistance" note per submission (tool, what for). You must be able to explain every line in the oral defence; undisclosed generated work, or work you cannot explain, is treated as misconduct.
- Calculation answers must be reproducible: include the code or the exact command you ran. Fabricated outputs are misconduct.
- Never put secrets, personal data of real people, or confidential employer data into prompts or submissions.

**Accessibility.** All labs run on either platform and offline; talk to the course team about adjustments (extra time, alternative formats) early.

## Primary sources used across the course
Vaswani et al. 2017 (arXiv:1706.03762) · Yao et al. 2023 (arXiv:2210.03629) · Jurafsky & Martin, *Speech and Language Processing* ch. 3 · NIST/SEMATECH e-Handbook §7.2.4.1 · McNemar 1947 · Sutton & Barto 2018 · Hart, Nilsson & Raphael 1968 · Rice 1953 · ACM Code of Ethics 2018 · NIST AI RMF 1.0 · Regulation (EU) 2024/1689 as amended by (EU) 2026/1744 · GDPR Art. 22 · Moffatt v. Air Canada 2024 BCCRT 149 · Parasuraman & Riley 1997. Full list with URLs: `documentation/VERIFIED-RESOURCES.md`.
