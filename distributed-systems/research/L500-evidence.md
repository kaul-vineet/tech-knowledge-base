# L500 research evidence (2026-10-30)

Method as SPEC.md: questions per lesson, candidate sources, kept/dropped with reason, key facts with URL. Every number in the lessons comes from a fetched source or from a seeded check script whose output is stored verbatim (`research/l500_checks.py` re-runs them).

## Lesson 23 - Foundations I
**Questions.** What exactly are Lamport's IR1/IR2 and the clock condition? What do vector clocks characterise and with which update rule? How are synchronous / asynchronous / partially synchronous models defined? What is the formal safety/liveness definition?
**Kept.** Lamport 1978 (author PDF, 12/12): definition of -> as the smallest relation of three rules; C1, C2, IR1, IR2; total order with process tie-break; "we cannot expect the converse"; anomalous behaviour; PC1/PC2 and the epsilon ≈ d(2κτ + ξ) theorem. Kleppmann notes (11/12, CC BY-SA): crash-stop / crash-recovery / Byzantine; synchronous / asynchronous / partially synchronous after Dwork et al.; fair-loss links. Dwork, Lynch & Stockmeyer 1988 (abstract: Δ, Φ; unknown bounds or bounds after unknown T). Alpern & Schneider 1985 (definitions of safety and liveness; every property = safety ∩ liveness). Gilbert & Lynch 2012 (consistency = safety, availability = liveness).
**Dropped.** Wikipedia "Vector clock" (secondary); Fidge 1988 / Mattern 1989 originals not retrieved - the vector-clock proof is standard and written from the definitions (stated as such in the lesson).
**Key facts.** https://lamport.azurewebsites.net/pubs/time-clocks.pdf (IR2(b): "sets C_j greater than or equal to its present value and greater than T_m"); https://www.cl.cam.ac.uk/teaching/2526/ConcDisSys/dist-sys-notes.pdf §2.3.

## Lesson 24 - Foundations II
**Questions.** FLP's exact model and lemma structure? Gilbert & Lynch's precise Theorem 1 and Corollary 1.1? Paxos invariants P1-P2c and the phase rules? Raft's safety argument and how it compares?
**Kept.** FLP 1985 (12/12): Theorem 1 "No consensus protocol is totally correct in spite of one fault"; Lemmas 1-3; admissible run; atomic broadcast and reliable delivery assumed. Gilbert & Lynch 2002 (12/12): Theorem 1, Corollary 1.1, Theorem 2 (partially synchronous), §3.2 any two achievable, Delayed-t consistency. Lamport 2001 (12/12): P1, P2, P2a-c, P1a, phases, §2.4 progress + FLP remark, stable storage. Raft extended version (12/12): Figure 3 properties, §5.4.1 election restriction, §5.4.2 / Figure 8, §5.4.3 proof, §5.6 timing. Kleppmann notes: two generals (Gray 1978), Byzantine 3f + 1 (Dwork et al. Theorem 4.4). Gilbert & Lynch 2012: failure detectors (Chandra, Toueg; weakest = Omega), eventual synchrony, n/2 bound.
**Dropped.** Brewer's 2000 keynote slides (not a proof); blog explanations of CAP (secondary).
**Key facts.** https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf; https://www.comp.nus.edu.sg/~gilbert/pubs/BrewersConjecture-SigAct.pdf; https://lamport.azurewebsites.net/pubs/paxos-simple.pdf; https://raft.github.io/raft.pdf.

## Lesson 25 - Foundations III
**Questions.** Assumptions of Little's law? Dean & Barroso's fan-out numbers? USL formula and peak? Amdahl's original framing?
**Kept.** Little & Graves 2008 (L = λW, stationarity only, no distribution / servers / order assumptions; area picture). Dean & Barroso 2013 (12/12): 10 ms / 1 s / 100 servers -> 63%; 1 in 10,000 and 2,000 servers -> almost one in five; hedged requests (1,800 ms -> 74 ms p99.9 with 2% more requests); tied requests; micro-partitions; canary requests. Gunther 2008 (10/12): Amdahl eq. (2), USL eq. (5), p* eq. (6), USL = synchronous repairman bound. Amdahl 1967 (8/12; words, no equations - noted in T25.4).
**Derived here (no source needed).** M/M/1 balance equations; the checks' simulations.
**Dropped.** ResearchGate copy of Little & Graves (OCR errors); vendor performance blogs.

## Lesson 26 - Ethics
**Questions.** Which code principles apply to reliability? What did a real outage report say about causes, communication and harms? What do blameless post-mortems require? What does GDPR say about availability and transfers? What do energy authorities project?
**Kept.** ACM Code 2018 (12/12: 1.1, 1.2, 1.3, 1.6, 2.1, 2.3, 2.5, 2.9, 3.7; adopted 22 June 2018). IEEE Code (items 1, 5). AWS US-EAST-1 summary 10 Dec 2021 (timeline 7:30 -> 2:22 PM PST, retries, latent back-off issue, SHD failover, support cases 7:33-2:25, Connect failures). Google SRE ch. 15 (definition, triggers, blameless). GDPR Art. 32 (legislation.gov.uk copy), CJEU press release 91/20. IEA Energy and AI (945 TWh by 2030, just under 3%).
**Dropped / limited.** Third-party GDPR article sites; EED Art. 12 secondary briefs (used only to locate the provision; see KNOWN-GAPS). Meta October 2021 and CrowdStrike July 2024 reports were considered as cases but not fetched; one well-documented primary report was preferred.

## Lesson 27 - Readings
Lamport 1978 (author PDF; ACM fair-use statement for teaching) and Ongaro & Ousterhout 2014 (USENIX open access page, ATC 14 pp. 305-319, Best Paper; extended version 20 May 2014). DeCandia et al. 2007 (Dynamo) was the alternative named in the brief; it is already a primary source of L400 #17 and #19, so Raft was chosen to pair a consensus paper with Lamport's ordering paper. Both papers read in full on 2026-10-30; the course summarises and links, never reproduces.

## Assessment pack
ABET CAC 2026-27 PDF (Criterion 3 outcomes 1-5, CS outcome 6) and EAC 2025-26 page (outcomes 1-7); CS2023 knowledge-area list (csed.acm.org). Exam model answers are recomputed by `research/l500_checks.py` (EXAMS).
