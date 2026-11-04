# L500 research evidence — quantum computing ("Theory & Rigour", lessons 23–27 + assessment pack)

Method: kb/SPEC.md research method with the rubric of `L100-evidence.md` (I implementable, C current, A authoritative, O open, T transferable, D right depth; 0–2 each; keep ≥ 8/12). For L500 "implementable" means "states a result precisely enough to prove or check in code", and primary papers, standards, statutes and regulators take priority over tutorials. Every URL below was retrieved with web_fetch or web_search on 2026-10-30 unless marked "reused". Paper texts are summarised and never reproduced (licences noted).

Design decision for the whole level: every theorem is followed by a numpy check that runs here (`labs/L500/<lab>/theorems.py`, on the shared `labs/_shared/qsim`). `research/l500_checks.py` re-runs each check, compares it with the `checkOutput` stored in `content/L500.json` and with the lab README, and recomputes every problem-set and exam number. No quantum SDK is needed, so all five lessons are `validated-local`.

## Lesson 23 — Foundations I: linear algebra for qubits
**Questions:** 1. Which conventions (bra conjugation, tensor order) must a derivation state to match the labs? 2. Which open, citable source presents the Born rule, tensor products and Bell states at undergraduate level? 3. How do we check "unitaries preserve norm" beyond one example?

| source | I C A O T D | score | decision |
|---|---|---|---|
| IBM Quantum Learning, Basics of quantum information: Single systems / Multiple systems (Watrous) — reused | 2 2 2 2 2 2 | 12 | kept: Dirac notation, tensor products, Bell states; licence CC BY-SA 4.0 (Qiskit/documentation repo) |
| IBM Quantum Learning, Limitations on quantum information | 2 2 2 2 2 2 | 12 | kept: irrelevance of global phases (|ψ> and α|ψ> with |α| = 1 indistinguishable under any U and measurement), relative phase |+>/|-> distinguishable with H |
| Bit-ordering in the Qiskit SDK — reused | 2 2 2 2 2 2 | 12 | kept: qubit 0 least significant (T23.2 ordering remark) |

**Key facts / own derivations:** polarisation identity for the converse of T23.1, Kronecker-index proof of the mixed-product rule, and the rotated-basis Bell derivation are standard linear algebra and are proved in the lesson, not quoted. Checks: 1000 Haar-random unitaries (QR with phase fix), 200 Kronecker cases, 300 random bases, five angle pairs plus 20,000 seeded shots each.

## Lesson 24 — Foundations II: quantum information basics
**Questions:** 1. What is the cleanest proof of no-cloning for this audience? 2. How are teleportation and superdense coding presented in an open course, and what is the e-bit framing? 3. What is the honest classical comparison for Deutsch-Jozsa? 4. Which source motivates density matrices and partial trace?

| source | I C A O T D | score | decision |
|---|---|---|---|
| IBM Quantum Learning, Limitations on quantum information (no-cloning section) | 2 2 2 2 2 2 | 12 | kept: theorem statement and linearity proof (U(|ψ>⊗|φ>) = |ψ>⊗|ψ> for all ψ impossible; basis states clonable with CNOT; approximate cloning possible) — the lesson adds the inner-product proof |
| IBM Quantum Learning, Entanglement in action (introduction) | 1 2 2 2 2 2 | 11 | kept: teleportation, superdense coding and CHSH as "stones in the foundation"; e-bit as a resource unit |
| IBM Quantum Learning, The Deutsch-Jozsa algorithm — reused | 2 2 2 2 2 2 | 12 | kept (L200 source) |
| IBM Quantum Learning, General formulation: Density matrices (introduction) | 1 2 2 2 2 2 | 11 | kept: density matrices describe noise, random choices of states, and parts of entangled systems; diagonal = classical |
| Cleve, Ekert, Macchiavello, Mosca (1998), arXiv:quant-ph/9708016 | 1 1 2 2 2 2 | 10 | kept: unified view of Deutsch-Jozsa, phase estimation and Shor as interference/phase estimation (abstract fetched; arXiv licence) |

**Key facts:** randomised classical bound for Deutsch-Jozsa (error ≤ 2^(1-k) with k queries) is derived in the lesson. Holevo's bound is mentioned once and explicitly "stated without proof" (KNOWN-GAPS). Checks: CNOT-copier fidelities (joint (c^3+s^3)^2, single c^4+s^4), 200 random teleportations × 4 outcomes, all 70 balanced 3-bit functions, 200 random no-signalling trials.

## Lesson 25 — Foundations III: algorithms and complexity
**Questions:** 1. Where are Grover's success formula and optimality proved? 2. What does Shor's paper claim, and where is the success probability of the reduction? 3. Which source supports "exponential speed-ups are rare" without hype in either direction?

| source | I C A O T D | score | decision |
|---|---|---|---|
| Grover (1996), arXiv:quant-ph/9605043 (STOC '96) | 1 1 2 1 2 2 | 9 | kept: N/2 classical vs O(√N) quantum; "within a small constant factor of the fastest possible"; v3 uses "inversion about average". Licence: arXiv distribution licence (abstract page "view license"); summarised only |
| Boyer, Brassard, Høyer, Tapp (1998), arXiv:quant-ph/9605034 | 2 1 2 1 2 2 | 10 | kept: closed-form success probability, multiple solutions, unknown M, quantum counting, near-optimality |
| Bennett, Bernstein, Brassard, Vazirani (1997), arXiv:quant-ph/9701001 | 1 1 2 1 2 2 | 9 | kept: relative to a random oracle NP not in time o(2^{n/2}); tight with Grover |
| Shor (1997), arXiv:quant-ph/9508027 (SIAM J. Comput. 26, 1484) | 1 1 2 1 2 2 | 9 | kept: polynomial-time randomized algorithms for factoring and discrete log; the ≥ 1/2 success probability of the reduction is cited to the paper's factoring section, and checked exactly for N = 15, 21, 33, 35, 91 |
| IBM Quantum Learning, Grover's algorithm (introduction) | 1 2 2 2 2 2 | 11 | kept: quadratic advantage "unlikely to lead to a practical advantage ... any time soon" |
| IBM Quantum Learning, Phase estimation and factoring (introduction) | 1 2 2 2 2 1 | 10 | kept: QFT → phase estimation → Shor structure; Shor 1994 conference / 1997 journal |
| Preskill (2018), Quantum 2, 79 (full text fetched via arXiv PDF) | 1 2 2 2 2 2 | 11 | kept: speed-up defined against best classical hardware and algorithm; NP-hard problems "likely to be quantumly hard"; QRAM input/output bottleneck; note on Tang (2018) dequantizing recommendation systems; ~1000-gate naive NISQ limit at > 0.1% two-qubit error |

**Own derivations:** reflection/rotation proof of Grover, P_k ≥ 1 - M/N for k = floor(π/(4θ)), geometric-series unitarity of the QFT, the |a_m| ≥ 2/π phase-estimation bound, BQP ⊆ PSPACE path-sum sketch, majority-vote amplification (15 runs → 0.0882). Checks: dense Grover up to N = 4096, QFT vs DFT for n ≤ 5 (circuit) and N ≤ 256 (matrix), QPE for t = 3–6, exact order-finding distributions for N = 15 and 21.

**Dropped:** Nature article page for the Sycamore paper (fetch returned only a one-line snippet; the Google blog and the arXiv supplementary-information abstract were used instead).

## Lesson 26 — Ethics, society and professional responsibility
**Questions:** 1. Which professional-code clauses govern capability claims? 2. What are the current, official PQC transition dates? 3. What do quantum export controls cover, at policy level, in the US and EU, and what is excluded? 4. Which primary source frames access/equity internationally? 5. What exactly happened to the 2019 supremacy comparison?

| source | I C A O T D | score | decision |
|---|---|---|---|
| ACM Code of Ethics and Professional Conduct (adopted 22 June 2018) | 2 2 2 1 2 2 | 11 | kept: 1.2, 1.3 (full disclosure of capabilities and limitations; misleading claims are violations), 1.4, 1.5, 2.3, 2.4, 2.5, 2.7, 3.1, 3.7 (fair access for infrastructure). © ACM, may be republished unchanged |
| IEEE Code of Ethics, IEEE Policies 7.8 (revisions through June 2020) | 2 2 2 1 2 2 | 11 | kept: item 2 (understanding of capabilities and implications of emerging technologies), item 5 ("honest and realistic in stating claims or estimates based on available data") |
| NIST IR 8547 final (CSRC page; Oct 2026) — PDF reused from L400 | 2 2 2 2 2 2 | 12 | kept: deprecate after 2030 / disallow after 2035; HNDL; Mosca X + Y > Z (from the L400 evidence); page now cites EO 14412 and OMB M-26-15 (not used further) |
| NIST FIPS 203 (CSRC page) | 1 2 2 2 2 2 | 11 | kept: ML-KEM-512/768/1024, published 13 Aug 2024 |
| UK NCSC, Timelines for migration to PQC (20 Mar 2025) | 2 2 2 1 2 2 | 11 | kept: 2028 discovery/plan, 2031 priority migration, 2035 complete; hybrid key agreement in browsers |
| US BIS interim final rule, 89 FR 72926 (6 Sep 2024), FederalRegister.gov | 1 2 2 2 1 2 | 10 | kept: new ECCNs incl. 3A901, 3A904 (≥ 600 µW at ≤ 0.1 K for > 48 h), 4A906, 4D906, 4E906; worldwide NS/RS licence requirement; License Exception IEC; General Order No. 6 (f)(3) General License for quantum deemed exports with annual reporting; BIS text on foreign talent ("more than half of QIST-related degrees ... temporary U.S. residents") |
| Commission Delegated Regulation (EU) 2025/2003 (EUR-Lex) | 1 2 2 2 1 1 | 9 | kept: replaces Annex I of Reg. 2021/821; in force the day after publication (OJ 14.11.2025); General Technology Note exclusions ("in the public domain", "basic scientific research") |
| UN GA resolution A/RES/78/287 (UN Digital Library) | 1 2 2 2 1 1 | 9 | kept: 2025 International Year of Quantum Science and Technology; adopted 7 June 2024 without vote; emphasis on developing countries |
| Google Research blog (23 Oct 2019) | 1 1 1 2 1 2 | 8 | kept (vendor, facts of the claim only): 200 s vs 10,000 years, 54-qubit Sycamore |
| Pednault et al. (2019), arXiv:1910.09534 | 1 1 2 1 2 2 | 9 | kept: simulation "in a matter of days" on Summit with secondary storage (the "2.5 days" figure is from IBM's blog, not fetched, so not used) |
| Pan, Chen, Zhang (2022), arXiv:2111.03011 (PRL 129, 090502) | 1 2 2 1 2 2 | 10 | kept: 1 M samples, 53 qubits / 20 cycles, F ≈ 0.0037, ~15 hours on 512 GPUs |
| Quantum journal, Terms and Conditions / Code of Conduct | 1 2 2 2 2 1 | 10 | kept: misconduct includes "misrepresentation and overstatement of results and the omission of crucial conditions and assumptions" |

**Dropped:** Eversheds Sutherland client note on the 2025 EU list (secondary, law-firm marketing; it is the only source we found for the EU quantum entry numbers 4A506, 3A501.b.13, 3A504, 3B504, so those numbers are not used in lesson text — KNOWN-GAPS); EC "regdel" and transparency-register copies of the delegated act (duplicates of EUR-Lex); Wikimedia copy of A/RES/78/287 (UN Digital Library used).

## Lesson 27 — Reading seminar
**Questions:** 1. Can both papers be retrieved openly, and under what licence? 2. What exactly do the abstracts and key sections claim?

| source | I C A O T D | score | decision |
|---|---|---|---|
| Grover (1996) abstract page arXiv:quant-ph/9605043 | as above | 9 | kept: reading 1; arXiv distribution licence → link + short attributed quotes only |
| Preskill (2018) Quantum page + arXiv:1801.00862v3 PDF | as above | 11 | kept: reading 2; NISQ = 50 to a few hundred qubits (§4.1), ~1000 gates naive limit (§4.2), speed-up definition and moving target (§6), optimizers/annealing/QML/HHL/recommendation/SDP/simulation sections, Tang note |
| Quantum: Terms and Conditions announcement (CC BY 4.0 for published works) | 1 2 2 2 1 1 | 9 | kept: licence evidence for reading 2 |
| arXiv non-exclusive licence to distribute | 1 2 2 2 1 1 | 9 | kept: licence evidence for reading 1 (grants arXiv, not readers, distribution rights) |

## Assessment pack
| source | I C A O T D | score | decision |
|---|---|---|---|
| ABET Criteria for Accrediting Computing Programs 2025–2026 | 2 2 2 1 2 2 | 11 | kept: CAC Student Outcomes 1–5 (verbatim in syllabus) + CS program criterion outcome 6 |
| ABET Criteria for Accrediting Engineering Programs 2025–2026 | 2 2 2 1 2 2 | 11 | kept: EAC Student Outcomes 1–7 (verbatim in syllabus) |
| CS2023 Knowledge Areas (csed.acm.org) | 2 2 2 2 2 1 | 11 | kept: 17 KA names and abbreviations |
| German, Pias, Xiang (ITiCSE 2023), Q-AR knowledge-unit proposal (ACM DL search result) | 1 1 1 1 1 2 | 7 | dropped as a source of truth (abstract only): mentioned in the syllabus as a *proposal*; final CS2023 wording not verified |

## Numbers in the concept notes and exams
Every number in `content/concepts/L500/*.md` is printed by `labs/L500/*/theorems.py` (pasted in the lab READMEs) or recomputed in `research/l500_checks.py`; the exam model answers' numbers are recomputed in its "exams" section (including the L400 #19 RSA row: 6190 logical qubits, 9,025,020 physical qubits, 16.1 hours, taken from that lab's code). Published figures (10,000 years / 200 s; 15 hours / 512 GPUs; 2030/2035; 2028/2031/2035) are quoted from the sources above.
