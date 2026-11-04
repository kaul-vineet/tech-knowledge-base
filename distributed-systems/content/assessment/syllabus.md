# Distributed Systems (applied, with theory) - 14-week syllabus

**Level:** undergraduate, third year · **Credits:** one 15-week semester module (14 teaching weeks + exam week) · **Prerequisites:** programming in Python, discrete mathematics (relations, induction), introductory probability, basic networking.

The course is lab-first: L100 "Run it", L200 "Build it", L300 "Harden it", L400 "Design it" + capstone. L500 adds the theory, ethics and primary literature: every week pairs a lab with the result that explains it.

## Course learning outcomes (CLOs)
By the end of the course a student can:
1. **Build** request/response services with timeouts, retries, idempotency and logical clocks, and explain their failure modes (L100).
2. **Implement** leader election with fencing, at-least-once messaging, consistent hashing, caching and rate limiting, verified by tests (L200).
3. **Diagnose and harden** replicated systems under injected faults (Raft, partitions, sagas, tracing, backpressure) (L300).
4. **Design** with evidence: choose consistency, replication and failover per use case, record ADRs, keep them true with fitness functions (L400).
5. **Prove and derive** the theory these mechanisms rest on - clock condition, vector clocks, two generals, FLP (sketch), CAP, quorum intersection, Paxos safety, M/M/1, Little's law, tail amplification, Amdahl/USL - and check each numerically (L500 #23-25).
6. **Evaluate** reliability decisions ethically and legally at policy level, using the ACM and IEEE codes, blameless post-mortems, data-protection and energy considerations (L500 #26).
7. **Read and critique** primary papers (Lamport 1978, Ongaro & Ousterhout 2014) and communicate designs in writing and orally (L500 #27, ADRs, oral defence).

## Weekly plan
| Week | Labs (hands-on) | Theory / ethics / reading (L500) | Weekly reading | Due |
|---|---|---|---|---|
| 1 | #1 Setup, #2 Two services talking over HTTP | #23 system models: synchronous / asynchronous / partially synchronous; crash vs Byzantine | Kleppmann notes §1-2.3 | concept inventory (pre) |
| 2 | #3 Timeouts, #4 Retries with backoff and jitter | #23 T23.4 failure detection and timing | Kleppmann §2.4; Google SRE "Handling Overload" | Lab 2-3 |
| 3 | #5 Idempotency keys, #6 Lamport clocks | #23 T23.1-T23.3 clock condition, vector clocks, safety vs liveness | Lamport 1978 (first pass) | Lab 4-5; PS23 |
| 4 | #7 Leader election with leases and fencing tokens, #8 At-least-once messaging | #24 T24.1 two generals | Kleppmann §2.1; Gray's two generals as told there | Lab 6-7 |
| 5 | #9 Consistent hashing, #10 Caching and invalidation | #25 T25.2 Little's law (cache and pool sizing) | Little & Graves ch. 5 | Lab 8-9 |
| 6 | #11 Rate limiting | #25 T25.1 M/M/1 | - | Lab 10-11; ADR peer review 1 (lab 11 design note) |
| 7 | **Midterm** (L100, L200, L500 #23 and #24 T24.1) | review | - | midterm |
| 8 | #12 Raft replicated log | #24 T24.2 FLP; T24.4 quorums and Paxos safety | Paxos Made Simple §2; Raft §5 | Lab 12; PS24 |
| 9 | #13 Partitions and fault injection | #24 T24.3 CAP precisely | Gilbert & Lynch 2002 | Lab 13 |
| 10 | #14 Sagas, #15 Distributed tracing | #25 T25.3 tail amplification | Dean & Barroso 2013 | Lab 14-15 |
| 11 | #16 Backpressure and load shedding, #17 Consistency and quorums | #25 T25.4 Amdahl and USL | Gunther 2008 §1-2 | Lab 16-17; PS25 |
| 12 | #18 CRDTs, #19 Multi-region design | #26 ethics: outages, post-mortems, data residency, energy | AWS Dec 2021 summary; ACM Code 2018; Google SRE ch. 15 | Lab 18-19; ADR peer review 2; case analysis 26 |
| 13 | #20 Chaos engineering, #21 Verifying correctness | #27 reading seminar: Lamport 1978, Raft 2014 | both papers (full) | Lab 20-21; critical response 27 |
| 14 | #22 Capstone integration and oral defences | revision | - | capstone + oral defence; concept inventory (post) |
| Exam week | **Final exam** (L100-L500) | | | final |

## Assessment
| Component | Weight | What | Mapped CLOs |
|---|---|---|---|
| Labs | 35% | 20 graded labs (#2-#21; #1 setup is pass/fail) graded by their tests, build tasks, fitness functions and a short README of observations | 1-4 |
| Problem sets | 25% | PS23, PS24, PS25 (8 problems each), case analysis #26 and critical response #27, graded with each lesson's rubric | 5-7 |
| Two exams | 20% | midterm 8% (week 7), final 12% (exam week); see midterm.md and final.md | 1-6 |
| Capstone + oral defence + peer-reviewed ADRs | 20% | capstone scorecard and code 10%, oral defence 5% (capstone-oral-defence.md), ADRs and peer reviews 5% (peer-review-adr.md); team roles in team-roles.md | 2-4, 6-7 |

The concept inventory (concept-inventory.json, 15 items) is taken in week 1 and week 14 and is **not graded**; it measures learning gain: normalised gain g = (post% - pre%) / (100 - pre%).

## Policies
- **Late work:** 10% of the component's marks per calendar day, up to 3 days; after that 0 unless an extension was agreed before the deadline. Lab tests that pass on CI at the deadline commit count as on time.
- **Academic integrity:** labs and problem sets are individual unless marked as pair work (pair programming protocol in team-roles.md); cite every source; copying solutions, tests or another team's ADR is misconduct. Primary papers may be quoted briefly with attribution only - summarise, never reproduce (licences in VERIFIED-RESOURCES.md).
- **AI and local models:** allowed as in the labs' agent-assist rule: the model may propose or explain; you verify with code and you are responsible for every claim. Disclose use in a short note. Never paste credentials, personal data or exam questions into a model.
- **Reproducibility:** graded runs use the seeded labs; if your machine shows different numbers for a seeded lab, report it (it is a bug).
- **Accessibility:** all labs run on one laptop (Mac mini or Windows PC, see HARDWARE.md); ask early for adjustments.

## Mapping to ACM/IEEE-CS/AAAI CS2023 knowledge areas
Knowledge-area names as listed at csed.acm.org/knowledge-areas (CS2023, verified 2026-10-30).

| CS2023 knowledge area | Where |
|---|---|
| Parallel and Distributed Computing (PDC) | whole course; theory in #23-#25 |
| Systems Fundamentals (SF) | #3, #4, #16, #19, #25 (performance, reliability) |
| Networking and Communication (NC) | #2, #3, #13 |
| Data Management (DM) | #10, #17, #18 |
| Security (SEC) | #7 (fencing), #26 (security of processing) |
| Software Engineering (SE) | ADRs, fitness functions, tests, CI (#17-#22) |
| Mathematical and Statistical Foundations (MSF) | #23-#25 proofs, probability, queueing |
| Society, Ethics, and the Profession (SEP) | #26, capstone oral defence, blameless post-mortems |

## Mapping to ABET student outcomes
Wording verified on abet.org on 2026-10-30. **Computing Accreditation Commission** (CAC, 2026-27 criteria, outcomes 1-5 general + 6 for computer science) and **Engineering Accreditation Commission** (EAC, 2025-26 criteria, outcomes 1-7) for programmes accredited by EAC.

| ABET outcome | Evidence in this course |
|---|---|
| CAC 1 - Analyze a complex computing problem and apply principles of computing and other relevant disciplines to identify solutions | problem sets #23-#25; L300 diagnosis labs |
| CAC 2 - Design, implement, and evaluate a computing-based solution to meet a given set of computing requirements | L200 build tasks; L400 design labs; capstone |
| CAC 3 - Communicate effectively in a variety of professional contexts | ADRs, critical response #27, oral defence |
| CAC 4 - Recognize professional responsibilities and make informed judgments in computing practice based on legal and ethical principles | #26 case analysis; post-mortem in the capstone |
| CAC 5 - Function effectively as a member or leader of a team | capstone teams, pair programming, ADR peer review |
| CAC 6 (CS) - Apply computer science theory and software development fundamentals to produce computing-based solutions | #23-#25 theorems applied in labs 6, 12, 16, 17 |
| EAC 1 - identify, formulate, and solve complex engineering problems by applying principles of engineering, science, and mathematics | #23-#25, L300 |
| EAC 2 - apply engineering design ... with consideration of public health, safety, and welfare, as well as global, cultural, social, environmental, and economic factors | L400 + #26 (availability, privacy, energy) |
| EAC 3 - communicate effectively with a range of audiences | ADRs, oral defence |
| EAC 4 - recognize ethical and professional responsibilities ... and make informed judgments | #26 |
| EAC 5 - function effectively on a team ... | capstone, team-roles.md |
| EAC 6 - develop and conduct appropriate experimentation, analyze and interpret data, and use engineering judgment | seeded experiments, chaos campaigns (#20), simulations in #25 |
| EAC 7 - acquire and apply new knowledge as needed, using appropriate learning strategies | reading seminar #27, learning tools |
