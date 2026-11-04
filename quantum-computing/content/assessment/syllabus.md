# Syllabus — Quantum computing: applied practice and theory (L100-L500)

**Level:** upper-level undergraduate, 14 weeks, ~10 hours/week (3 contact + 7 independent).
**Prerequisites:** programming in Python; linear algebra (complex vectors, matrix products, eigenvalues); discrete probability; introductory algorithms (big-O). No physics background is assumed.
**Platform:** every lab runs on a laptop (Apple-silicon Mac or Windows 11) with open-source simulators; no cloud account or quantum hardware is needed (`documentation/HARDWARE.md`).

> The 14-week plan below is this topic's proposal. The pedagogy review that asked for it is not in the knowledge base, so week boundaries should be confirmed with the course lead (see KNOWN-GAPS).

## Course learning outcomes

By the end of the course a student can:

| # | Outcome (Bloom level) | Lessons | ACM/IEEE CS2023 knowledge areas | ABET CAC | ABET EAC |
|---|---|---|---|---|---|
| LO1 | **Explain** and **derive** the linear algebra of qubits (states, unitaries, tensor products, Born rule) and verify results numerically | L100 #2-#4, L500 #23 | MSF, AL | 1, 6 (CS) | 1 |
| LO2 | **Prove** core information-theoretic results (no-cloning, teleportation, Deutsch-Jozsa) and **explain** their engineering consequences | L500 #24, L200 #7 | MSF, AL, SEC | 1, 6 (CS) | 1 |
| LO3 | **Derive** and **evaluate** Grover, QFT, phase estimation and Shor's reduction, and **critique** speed-up claims with complexity arguments | L200 #8-#9, L500 #25 | AL, MSF | 1, 6 (CS) | 1, 7 |
| LO4 | **Build** and **test** portable circuits and hybrid loops, with statistical rather than exact assertions | L100 #1-#6, L200, L300 #14-#16 | SDF, SE, FPL | 2, 6 (CS) | 2, 6 |
| LO5 | **Analyze** noise, mitigation, compilation and resource estimates, and **justify** feasibility decisions with numbers | L300 #12-#13, L400 #19-#20 | AR, SF, PDC | 1, 2 | 1, 6 |
| LO6 | **Design** a hybrid service with ADRs and fitness functions and **defend** it orally | L400 #17-#18, #22 | SE, SF, PDC | 2, 3, 5 | 2, 3, 5 |
| LO7 | **Evaluate** professional responsibilities: honest claims, post-quantum migration, export controls, access | L400 #21, L500 #26 | SEP, SEC | 4 | 4 |
| LO8 | **Critique** primary literature and communicate the critique in writing | L500 #27 | SEP | 3 | 3, 7 |

**CS2023 knowledge areas** (ACM/IEEE-CS/AAAI, verified on csed.acm.org): AL Algorithmic Foundations; AR Architecture and Organization; FPL Foundations of Programming Languages; MSF Mathematical and Statistical Foundations; PDC Parallel and Distributed Computing; SDF Software Development Fundamentals; SE Software Engineering; SEC Security; SEP Society, Ethics, and the Profession; SF Systems Fundamentals. A Quantum Architectures knowledge unit was proposed for AR (German, Pias and Xiang, ITiCSE 2023). Its final CS2023 wording was not verified (KNOWN-GAPS).

**ABET Computing Accreditation Commission (CAC), Criterion 3, 2025-2026.** Graduates will have an ability to:
1. Analyze a complex computing problem and apply principles of computing and other relevant disciplines to identify solutions.
2. Design, implement, and evaluate a computing-based solution to meet a given set of computing requirements in the context of the program's discipline.
3. Communicate effectively in a variety of professional contexts.
4. Recognize professional responsibilities and make informed judgments in computing practice based on legal and ethical principles.
5. Function effectively as a member or leader of a team engaged in activities appropriate to the program's discipline.

Computer science programs add a sixth outcome, marked "6 (CS)" above: apply computer science theory and software development fundamentals to produce computing-based solutions.

**ABET Engineering Accreditation Commission (EAC), outcomes 1-7, 2025-2026**, for programs accredited as engineering. Graduates will have:
1. an ability to identify, formulate, and solve complex engineering problems by applying principles of engineering, science, and mathematics;
2. an ability to apply engineering design to produce solutions that meet specified needs with consideration of public health, safety, and welfare, as well as global, cultural, social, environmental, and economic factors;
3. an ability to communicate effectively with a range of audiences;
4. an ability to recognize ethical and professional responsibilities in engineering situations and make informed judgments, which must consider the impact of engineering solutions in global, economic, environmental, and societal contexts;
5. an ability to function effectively on a team whose members together provide leadership, create a collaborative environment, establish goals, plan tasks, and meet objectives;
6. an ability to develop and conduct appropriate experimentation, analyze and interpret data, and use engineering judgment to draw conclusions;
7. an ability to acquire and apply new knowledge as needed, using appropriate learning strategies.

## 14-week plan

| Week | Practice (labs) | Theory (L500) | Reading | Due |
|---|---|---|---|---|
| 1 | L100 #1 Set up your quantum environment; #2 Qubits and gates in code | #23 states, inner products, unitaries (T23.1) | Watrous, *Single systems* (IBM Quantum Learning) | concept inventory (pre-test) |
| 2 | L100 #3 Shots, counts and probability; #4 Entanglement with a Bell pair | #23 Born rule, Bell statistics (T23.3-T23.4) | Watrous, *Multiple systems* | lab 1-2 |
| 3 | L100 #5 Portable circuits with OpenQASM; #6 Same circuit, two frameworks | #23 tensor-product ordering (T23.2) | Qiskit bit-ordering guide | PS23 |
| 4 | L200 #7 Bernstein–Vazirani; #8 Small Grover search (pairs, `team-roles.md`) | #24 phase kickback, Deutsch-Jozsa (T24.3) | Cleve, Ekert, Macchiavello and Mosca (1998), introduction | labs 3-6 |
| 5 | L200 #9 The QFT as a building block; #10 Parameterized circuits | #24 no-cloning, teleportation, superdense coding (T24.1-T24.2) | Watrous, *Limitations on quantum information*; *Entanglement in action* | — |
| 6 | L200 #11 Transpiling to a device layout | #24 density matrices, partial trace (T24.4) | Watrous, *Density matrices* | PS24; labs 7-9 |
| 7 | L300 #12 Noise models | review | — | **midterm** (`midterm.md`) |
| 8 | L300 #13 Error mitigation; #14 QAOA on MaxCut | #25 Grover derivation, optimality (T25.1) | Grover (1996); Boyer et al. (1998), introduction | labs 10-11 |
| 9 | L300 #15 VQE; #16 quantum classifier | #25 QFT, phase estimation, Shor, BQP (T25.2-T25.4) | Shor (1997), introduction and the factoring section | PS25; labs 12-14 |
| 10 | L400 #17 Hybrid architecture; #18 Benchmarking honestly | why speed-ups are rare (#25 P9) | Preskill (2018), sections 1-4 | ADR peer review 1 (`peer-review-adr.md`); labs 15-16 |
| 11 | L400 #19 Resource estimation; #20 Error-aware compilation | #26 claims and the supremacy timeline | ACM Code of Ethics (2018); IEEE Code 7.8 | labs 17-18 |
| 12 | L400 #21 Quantum and post-quantum; capstone kickoff | #26 HNDL, export controls, access; case study | NIST IR 8547; NCSC timelines; BIS 89 FR 72926 (summary sections) | PS26 + case analysis; labs 19-20 |
| 13 | L400 #22 Capstone build | #27 reading seminar | Grover (1996) and Preskill (2018) in full | ADR peer review 2; PS27 + critical response; lab 21 |
| 14 | Capstone demonstration | review | — | capstone, **oral defence**, **final exam** (`final.md`), concept inventory (post-test) |

## Assessment

| Component | Weight | Details |
|---|---|---|
| Labs | 35% | 21 labs (L100-L400), each graded on passing tests, an observed-output README and one tryIt answered in the student's own words. Lowest two lab scores dropped. |
| Problem sets | 25% | PS23, PS24, PS25 (6% each), PS26 and PS27 (3.5% each), graded with each lesson's rubric. Calculations must be backed by code output. |
| Two exams | 20% | Midterm 8%, cumulative final 12%. |
| Capstone + oral defence + peer-reviewed ADRs | 20% | Capstone service 10% (team, `team-roles.md`); oral defence 5% (individual, `capstone-oral-defence.md`); ADR peer reviews 5% (two rounds; your review is graded, not the reviewed ADR). |

The concept inventory (`concept-inventory.json`, 15 items) is given ungraded in week 1 and week 14. Report the normalised gain g = (post - pre) / (100% - pre) per student and per class to measure learning, not to grade it.

## Policies

**Late work.** Labs and problem sets lose 10% per day, for up to 3 days; after that they score 0 but must still be submitted to pass the course. Each student has 3 "grace days" per term, to be used in whole days on labs or problem sets (not exams, the capstone or the defence). Extensions for illness or caring duties go through the usual university process.

**Academic integrity.** Labs may be done in pairs, both names on the submission. Problem sets, case analyses and critical responses are individual. You may discuss ideas, but write your own solution and name whoever you discussed it with. Copying solutions, including from earlier years, is misconduct. Code from the course repository may be reused with attribution. The integrity rules of *Quantum* (no overstatement, no omitted assumptions) apply to your reports too.

**AI and local agents.** The course's rule is the same as its labs' rule: the model proposes, the code decides. You may use a local or hosted assistant to explain concepts or draft code. You must (1) disclose the use in a short note on the submission, (2) verify every number with code you ran, and (3) never submit model-written proofs or essays as your own. Undisclosed use is treated like undisclosed collaboration. Do not paste exam questions, credentials or other students' work into any model.

**Accessibility.** All materials are text and code; the simulators run offline. Contact the instructor in week 1 for adjustments. The capstone oral defence can be held as a written Q&A if needed.
