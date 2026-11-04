# Applied Cryptography - 14-week undergraduate syllabus (L100-L500)

**Audience:** undergraduates in computer science, software engineering or cybersecurity engineering who can program in Python.
**Prerequisites:** discrete mathematics (proof, modular arithmetic), introductory probability, Python.
**Format:** each week has two 75-minute sessions (theory and lab) plus about 6 hours of independent work.
**Materials:** this knowledge base (content/L100-L500.json, labs/, concept notes) and the readings listed below.
**Toolchain:** Python 3.12, cryptography==50.0.2, on an Apple-silicon Mac or a Windows 11 PC (documentation/HARDWARE.md).

## How the levels map to the course
| Level | Lessons | Role in the course |
|---|---|---|
| L100 "Run it" | 1-6 | Safe primitives: hashing, randomness, AEAD, passwords |
| L200 "Build it" | 7-11 | Signatures, key exchange, PKI, TLS, tokens |
| L300 "Harden it" | 12-16 | Rotation, certificate lifecycle, supply chain, misuse tests, secrets |
| L400 "Design it" | 17-22 | Agility, post-quantum, hardware keys, group E2EE, threat models, capstone |
| L500 "Theory & Rigour" | 23-27 | Number theory, probability, security definitions, ethics, primary literature |

The L500 theory is **interleaved**: each theory lesson comes in the week where the practice that needs it is taught.

## Weekly plan
| Week | Theory session | Lab session | Reading (before the week) | Due |
|---|---|---|---|---|
| 1 | Course map; threat vocabulary | L100 #1 Set up your crypto workbench; #2 Hashing and integrity | Concept notes 01-02 | - |
| 2 | **L500 #24** Probability I: birthday bound, entropy | L100 #3 Secure randomness; #4 Authenticated encryption | Note 24; NIST SP 800-38D §8 | Lab 1-2 |
| 3 | **L500 #24** Probability II: nonce budgets, negligible functions | L100 #5 Password storage; #6 Encoding vs hashing vs encryption | Boneh-Shoup App. B | Problem set 24 |
| 4 | **L500 #23** Number theory I: Euclid, Euler, CRT | L200 #7 Digital signatures with Ed25519 | Note 23; Boneh-Shoup App. A | Lab 3-6 |
| 5 | **L500 #23** Number theory II: RSA correctness, textbook RSA/DH | L200 #8 Key exchange and hybrid encryption | RFC 8017 §§3, 5, 7.1 (skim) | Problem set 23 |
| 6 | **L500 #25** Security definitions I: OTP, IND-CPA, IND-CCA | L200 #9 A local certificate authority; #10 TLS on localhost | Note 25; Bellare-Namprempre abstract | Lab 7-8 |
| 7 | **Midterm exam** (content/assessment/midterm.md) | L200 #11 Tokens done right | - | - |
| 8 | **L500 #25** Security definitions II: EUF-CMA, reductions, DL and LWE | L300 #12 Envelope encryption and key rotation | Regev (2009) §1 (intuition only) | Problem set 25; Lab 9-11 |
| 9 | **L500 #27** Reading seminar: Shannon 1949 | L300 #13 Certificate lifecycle | Shannon 1949, Parts I-II | Reading notes |
| 10 | **L500 #27** Reading seminar: Diffie & Hellman 1976 | L300 #14 Signing the software supply chain; #15 Misuse you can test | Diffie & Hellman 1976 | Critical response 1 |
| 11 | **L500 #26** Ethics: lawful access, disclosure, export | L300 #16 Secrets handling in applications | Note 26; ACM Code 2018; ISO/IEC 29147 abstract; CERT Guide intro | Case analysis (26-P3) |
| 12 | Design review practice: ADRs and fitness functions | L400 #17 Crypto agility; #18 Post-quantum in practice | FIPS 203 abstract; RFC 7696 | Lab 12-16; peer-reviewed ADR 1 |
| 13 | Threat modelling and group E2EE | L400 #19 Keys in hardware-style storage; #20 Group E2EE; #21 Threat modelling | Notes 19-21 | Peer-reviewed ADR 2 |
| 14 | **Capstone oral defence** and **final exam** | L400 #22 Capstone: an encrypted document service | - | Capstone + defence |

## Assessment
| Component | Weight | What | Where |
|---|---|---|---|
| Labs | 35 % | L100-L400 labs; each checkpoint is PASS/FAIL with a short write-up graded on correctness and evidence (observed output) | labs/ |
| Problem sets | 25 % | L500 problem sets 23-27 (calculations are auto-checked against research/l500_checks.py; proofs and essays use the lesson rubrics) | content/L500.json `problemSet`, `rubric` |
| Two exams | 20 % (10 % + 10 %) | Midterm (week 7) and final (week 14), each mixing derivation, short explanation, prediction and design critique | midterm.md, final.md |
| Capstone + oral defence + peer-reviewed ADRs | 20 % | Capstone service 10 %, oral defence 5 %, two peer-reviewed ADRs 5 % | capstone-oral-defence.md, peer-review-adr.md, team-roles.md |

The **concept inventory** (concept-inventory.json, 15 items) is given ungraded in week 1 and again in week 14. Report the normalised gain g = (post − pre) / (100 − pre) per cohort.

## Policies
- **Late work.** 10 % off per calendar day, up to 3 days, after which the work is not accepted. One no-questions 48-hour extension per student per term. Extensions for documented illness or emergencies are granted by the instructor.
- **Academic integrity.** Labs may be done in pairs using the pair-programming protocol (team-roles.md), and both names go on the submission. Problem sets, exams and critical responses are individual. You may discuss ideas, but you must write your own solutions. Cite every source.
- **Generative AI and local agents.** These may explain concepts and review code, as in the "agent assist" labs. You must state what you used them for. Every number and claim you submit must be verified by your own code or a cited source, and you remain responsible for it. Submitting unverified model output as your own analysis is an integrity violation.
- **Ethics of practice.** Attack demonstrations run only on your own machine or on systems you are authorised to test (ACM Code 2.8). Lab keys are demo keys, and no real secrets go into submissions or models.
- **Reading primary sources.** Summarise; short quotations need page or section references. Do not redistribute copyrighted PDFs.

## Course learning outcomes
On completion students can:
1. **Use** vetted primitives correctly: AEAD, hashing, password hashing, signatures, key exchange, PKI and TLS (L100-L200).
2. **Harden and test** cryptographic code against misuse: nonce reuse, timing, rotation and secrets (L300).
3. **Design and justify** cryptographic architectures with ADRs, fitness functions and threat models, including post-quantum migration (L400).
4. **Prove and quantify** the foundations: number-theoretic correctness, birthday and nonce budgets, security games and reductions, hardness assumptions (L500 #23-25).
5. **Evaluate** ethical, legal and societal implications, and practise coordinated disclosure (L500 #26).
6. **Read and critique** primary literature (L500 #27).
7. **Communicate and collaborate**: ADR peer review, oral defence, team capstone.

### Mapping to ACM/IEEE-CS/AAAI CS2023 knowledge areas
CS2023 knowledge areas (verified at https://csed.acm.org/knowledge-areas/ on 2026-10-30) include Security (SEC); Mathematical and Statistical Foundations (MSF); Society, Ethics, and the Profession (SEP); Algorithmic Foundations (AL); Software Engineering (SE); Networking and Communication (NC); and Software Development Fundamentals (SDF).

| Outcome | SEC | MSF | SEP | AL | SE | NC | SDF |
|---|---|---|---|---|---|---|---|
| 1 Use primitives | ● |  |  |  |  | ● | ● |
| 2 Harden/test | ● |  |  |  | ● |  | ● |
| 3 Design/justify | ● |  |  |  | ● | ● |  |
| 4 Prove/quantify | ● | ● |  | ● |  |  |  |
| 5 Ethics/law | ● |  | ● |  |  |  |  |
| 6 Primary literature | ● | ● | ● |  |  |  |  |
| 7 Communicate/collaborate |  |  | ● |  | ● |  |  |

### Mapping to ABET student outcomes (1)-(7)
The wording was verified against the ABET *Criteria for Accrediting Engineering Programs, 2025-2026*, Criterion 3 (retrieved 2026-10-30). The summaries below are paraphrased. Those engineering criteria also include Cybersecurity Engineering program criteria. They require probability, statistics and cryptographic topics, plus specialised mathematics such as number theory and finite fields, which L500 #23-25 address. *Note:* computing programmes accredited by ABET's Computing Accreditation Commission use a different, shorter outcome list. Map to that list if your programme is CAC-accredited.

| ABET outcome (paraphrased) | Course outcomes | Evidence |
|---|---|---|
| (1) Identify, formulate and solve complex engineering problems using engineering, science and mathematics | 2, 4 | Problem sets 23-25; misuse labs |
| (2) Apply engineering design with consideration of public health, safety, welfare and global, cultural, social, environmental and economic factors | 3, 5 | L400 ADRs; capstone |
| (3) Communicate effectively with a range of audiences | 6, 7 | Critical responses; oral defence |
| (4) Recognise ethical and professional responsibilities and make informed judgments considering impact in global, economic, environmental and societal contexts | 5 | Case analysis 26-P3; disclosure plan 26-P4 |
| (5) Function effectively on a team | 7 | Team capstone; pair labs; ADR peer review |
| (6) Develop and conduct experimentation, analyse and interpret data, use engineering judgment | 1, 2, 4 | Theorem checks; measured lab evidence |
| (7) Acquire and apply new knowledge using appropriate learning strategies | 4, 6 | Reading seminar; post-quantum lessons |

## Weekly reading list (all links verified; see documentation/VERIFIED-RESOURCES.md)
- Boneh & Shoup, *A Graduate Course in Applied Cryptography* v0.6 - https://toc.cryptobook.us/ (Appendices A-B; chapters 2, 5, 6, 9, 10, 17)
- Shannon (1949) - https://www.cs.virginia.edu/~evans/greatworks/shannon1949.pdf
- Diffie & Hellman (1976) - https://www-ee.stanford.edu/~hellman/publications/24.pdf
- Bellare & Namprempre - https://eprint.iacr.org/2000/025
- NIST SP 800-38D, FIPS 203, RFC 8017 (as listed in lessons 23-25)
- ACM Code of Ethics (2018) - https://www.acm.org/code-of-ethics; ISO/IEC 29147:2018 abstract; CERT Guide to CVD - https://certcc.github.io/CERT-Guide-to-CVD/
