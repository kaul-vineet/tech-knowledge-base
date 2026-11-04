# L500 evidence - research questions, sources considered, key facts (2026-10-30)

Method as in SPEC.md: 2-3 questions per lesson; search official, standard and primary sources; score kept sources 0-2 on six criteria (keep ≥ 8/12); cross-check claims against ≥ 2 sources, one of them primary. All URLs below were retrieved on 2026-10-30 unless marked otherwise. Theory results are standard textbook material. Proofs were written for this course and cross-checked against Boneh-Shoup v0.6 and the primary papers, and every numeric claim is computed by code (research/l500_checks.py, labs/L500/*/theorem_checks.py).

## Lesson 23 - number theory
**Questions.**
1. What exactly must d satisfy, and how do libraries store CRT parameters?
2. Is finite-field DH still supported in pyca 50.0.2?
3. What is the original DH construction and its cost estimate?

**Kept.**
| Source | URL | Score | Facts used |
|---|---|---|---|
| RFC 8017 PKCS #1 v2.2 | https://www.rfc-editor.org/rfc/rfc8017.html | 12 | §3.2: d satisfies e·d ≡ 1 (mod λ(n)); CRT representation (p, q, dP, dQ, qInv) with qInv = q⁻¹ mod p; §5.1.2 RSADP CRT steps; §7.1: RSAES-OAEP is REQUIRED for new applications; PKCS1-v1_5 encryption of arbitrary messages NOT RECOMMENDED |
| pyca/cryptography RSA docs | https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/ | 12 | RSAPrivateNumbers dmp1 = d mod (p−1), dmq1 = d mod (q−1), iqmp = q⁻¹ mod p; rsa_recover_private_exponent uses the Carmichael totient; OAEP/PSS recommended |
| Boneh & Shoup v0.6 | https://toc.cryptobook.us/ | 11 | Appendix A number theory; v0.6 posted Jan 14 2023 |
| Diffie & Hellman 1976 | https://www-ee.stanford.edu/~hellman/publications/24.pdf | 11 | Y = α^X mod q; K = α^(XiXj); 2·log₂q multiplications; ~q^(1/2) for logs; b = 200 → 400 multiplications vs 2^100 |

**Observed locally (cryptography 50.0.2).**
- `dh.DHParameterNumbers(23, 4, 11).parameters()` raised "p (modulus) must be at least 512-bit".
- `dh.generate_parameters(2, 512)` works and emits CryptographyDeprecationWarning ("Diffie-Hellman over finite fields (FFDH) is deprecated ...").
- pyca's d satisfies e·d ≡ 1 mod lcm(p−1, q−1).

**Dropped.** Wikipedia and blog explanations of RSA (not primary, and redundant with RFC 8017 and Boneh-Shoup).

## Lesson 24 - probability
**Questions.**
1. Where is the GCM random-IV limit stated?
2. Which standard uses min-entropy for entropy sources?
3. Exact vs approximate birthday numbers?

**Kept.**
| Source | URL | Score | Facts used |
|---|---|---|---|
| NIST SP 800-38D (also L100) | https://csrc.nist.gov/pubs/sp/800/38/d/final | 11 | GCM/GMAC spec, Nov 2007. NIST announced a revision (planning note 2024-03-06). The 2^32-invocation limit for random IVs (§8.3) was already used and cited in L100 #4 |
| NIST SP 800-90B | https://csrc.nist.gov/pubs/sp/800/90/b/final | 10 | Jan 2018, entropy sources; keywords include min-entropy |
| Boneh & Shoup v0.6 | https://toc.cryptobook.us/ | 11 | Appendix B probability; negligible functions |
| RFC 8439 (also L100) | https://www.rfc-editor.org/rfc/rfc8439.html | 11 | Nonce uniqueness for ChaCha20-Poly1305 |

All numbers (23 / 0.5073, 77164, 2^−33.00, 2^32.50, 2^48.24, 0.39, 12.43 / 3.32 bits, n ≥ 83) were computed in labs/L500/24-probability.

## Lesson 25 - security definitions
**Questions.**
1. Which generic compositions are secure?
2. What is known about generic discrete-log lower bounds?
3. What does FIPS 203 say ML-KEM's security rests on?
4. Where does LWE come from?

**Kept.**
| Source | URL | Score | Facts used |
|---|---|---|---|
| Bellare & Namprempre, ePrint 2000/025 (CC BY) | https://eprint.iacr.org/2000/025 | 11 | IND-CPA + INT-CTXT notions; Encrypt-and-MAC, MAC-then-encrypt, Encrypt-then-MAC analysed under IND-CPA encryption + EUF-CMA MAC; proofs and counterexamples |
| Shoup 1997 (author copy) | https://www.shoup.net/papers/dlbounds1.pdf | 10 | Generic algorithms need Ω(p^(1/2)) group operations; index calculus is outside the generic model; for elliptic curves only generic algorithms are known |
| Regev (author copy, 2009 version) | https://cims.nyu.edu/~regev/papers/qcrypto.pdf | 10 | LWE definition; quantum reduction from worst-case lattice problems; public-key cryptosystem |
| NIST FIPS 203 | https://csrc.nist.gov/pubs/fips/203/final | 12 | Aug 13 2024; ML-KEM security related to Module-LWE; ML-KEM-512/768/1024; errata planning note 2025-11-17 |
| Shannon 1949 | https://www.cs.virginia.edu/~evans/greatworks/shannon1949.pdf | 11 | Perfect-secrecy definition and key-count condition |

**Observed locally.** pyca ML-KEM-768 encapsulation key 1184 B, ciphertext 1088 B, shared secret 32 B (same values as L400 #18).

**Note.** q = 3329 for ML-KEM is from FIPS 203. The fetched abstract does not state it; it is the standard parameter, and KNOWN-GAPS 75 records that only the abstract page was fetched this pass.

## Lesson 26 - ethics
**Questions.**
1. What exactly did each side claim in Apple-FBI 2016, and what did the later official review find?
2. What do ISO/IEC 29147 and the CERT Guide cover?
3. What is the current export framework, at policy level?
4. What is the exact wording and numbering of the ACM and IEEE codes?

**Kept.**
| Source | URL | Score | Facts used |
|---|---|---|---|
| ACM Code of Ethics 2018 | https://www.acm.org/code-of-ethics | 12 | Principle numbers and titles 1.1-4.2; 2.3 challenge rules through existing channels; 2.8 "publicly accessible is not sufficient grounds"; 2.9 secure systems incl. vulnerability reporting; adopted 22 June 2018 |
| IEEE Code of Ethics (Policies 7.8) | https://www.ieee.org/about/corporate/governance/p7-8.html | 11 | Item 1 (privacy, disclose dangers), item 5 (honest criticism, realistic claims); revisions through June 2020 |
| Apple customer letter | https://www.apple.com/customer-letter/ | 9 (party to the dispute: advocacy) | 16 Feb 2016; new iOS version circumventing security features; All Writs Act of 1789; electronic passcode entry |
| DOJ OIG Report 18-03 (landing page + press release) | https://oig.justice.gov/reports/special-inquiry-regarding-accuracy-fbi-statements-concerning-its-capabilities-exploit ; https://www.oig.justice.gov/archives/press/2018/2018-03-27.pdf | 11 | Posted 27 Mar 2018; no evidence of capability at time of testimony; coordination failures delayed the outside-party solution; government withdrew the filing |
| Keys Under Doormats (MIT-CSAIL-TR-2015-026) | https://dspace.mit.edu/bitstream/handle/1721.1/97690/MIT-CSAIL-TR-2015-026.pdf?sequence=1 | 11 | Abstract: exceptional access would reverse forward secrecy, introduce hard-to-detect flaws, raise governance and human-rights problems; recommend concrete technical requirements first; CC BY-NC-ND 4.0 (DSpace record) |
| ISO/IEC 29147:2018 | https://www.iso.org/standard/72311.html | 10 (paywalled text; abstract only) | Ed. 2 2018-10, confirmed 2024, stage 90.92 (to be revised); scope: receiving reports and disclosing remediation; ISO/IEC 30111 for handling |
| CERT Guide to CVD (CMU/SEI-2017-SR-022) | https://certcc.github.io/CERT-Guide-to-CVD/ ; https://www.sei.cmu.edu/library/the-cert-guide-to-coordinated-vulnerability-disclosure-2/ | 11 | Definition of CVD; phases (discovery, reporting, validation and triage, remediation, public awareness, promote deployment); coordinator roles |
| 15 CFR 740.17 (eCFR, up to date as of 2026-10-27) | https://www.ecfr.gov/current/title-15/subtitle-B/chapter-VII/subchapter-C/part-740/section-740.17 | 11 | License Exception ENC scope; Country Groups E:1/E:2 excluded; mass-market note → 5A992/5D992 after classification; self-classification reports |
| Wassenaar dual-use list 2025 Corr. | https://www.wassenaar.org/app/uploads/2026/01/List-of-Dual-Use-Goods-and-Technologies-and-ML-2025-Corr.pdf | 10 | Category 5 Part 2 "Information Security"; General Software Note does not release Cat. 5 Part 2 software |

**Dropped.**
- The direct PDF of OIG report o1803.pdf: the fetch returned no content. The landing page and press release were used instead (KNOWN-GAPS 76).
- A commercial "encryption export controls guide" found in search: secondary and vendor-run.
- News articles on the case: secondary; the primary documents suffice.

## Lesson 27 - readings
**Questions.**
1. Are accessible, legitimately hosted copies available?
2. Exact bibliographic data?
3. Which passages support the guided questions?

**Kept.**
| Source | URL | Score | Facts used |
|---|---|---|---|
| Diffie & Hellman 1976, Hellman's Stanford page | https://www-ee.stanford.edu/~hellman/publications/24.pdf | 11 | IEEE Trans. IT-22(6), Nov 1976; (n² − n)/2 pairs; PK cryptosystem vs PK distribution; no proof of converse; attack classification; public file protection; one-way authentication; trap doors (§V) |
| Shannon 1949, UVA course copy | https://www.cs.virginia.edu/~evans/greatworks/shannon1949.pdf | 10 | Three types of secrecy systems; enemy knows the system; perfect secrecy needs as many keys as messages; equivocation; unicity distance H(K)/D, "about 30 letters" for simple substitution with H(K) given as "about 20" |
| Shannon 1949, Internet Archive BSTJ 28:4 scan | https://archive.org/details/bstj28-4-656 | 9 | Bibliographic confirmation (BSTJ 28:4, October 1949, p. 656) |

**Licence.** Both papers are copyrighted (IEEE; Bell System Technical Journal). The lesson only links to copies hosted by an author or a university page and summarises them. No text is reproduced beyond short phrases.

## Course-level assessment
| Source | URL | Facts used |
|---|---|---|
| ABET Criteria for Accrediting Engineering Programs 2025-2026 | https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-engineering-programs-2025-2026/ | Criterion 3 outcomes (1)-(7) (paraphrased in the syllabus); Cybersecurity Engineering program criteria include probability, statistics, cryptographic topics, number theory and finite fields |
| CS2023 knowledge areas | https://csed.acm.org/knowledge-areas/ | KA names and abbreviations (SEC, MSF, SEP, AL, SE, NC, SDF, ...); CS2023 endorsed by ACM, IEEE-CS and AAAI in Jan-Feb 2024 (https://csed.acm.org/) |
