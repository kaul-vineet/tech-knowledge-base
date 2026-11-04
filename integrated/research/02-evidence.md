# L600 #02 evidence — Quantum-safe migration: from Shor in a simulator to a crypto inventory

Checked 2026-10-30 with web_search / web_fetch (primary sources only) and by running the lab locally
(Python 3.12, numpy, cryptography 50.0.2; Qiskit not installed). Every number in the lesson and question bank is
recomputed by `integrated/research/checks_02.py`.

## Research questions
1. What do the primary sources say it takes to factor RSA-2048, under which assumptions? (never extrapolate from N = 15/21)
2. What is NIST's current transition timeline for quantum-vulnerable public-key algorithms, and how does it describe
   Mosca's inequality, harvest-now-decrypt-later and hybrids? (final IR 8547 was published 2026-10-27 - re-read it)
3. What are the exact X25519MLKEM768 wire sizes and share order? What are the ML-DSA key/signature sizes?
4. Why do small Shor demos mislead?

## Sources kept (score /12: implementable, current, authoritative, open, transferable, right depth)
| Source | URL | Used for | Score |
|---|---|---|---|
| NIST IR 8547 (final, October 2026), *Transition to Post-Quantum Cryptography Standards* | https://nvlpubs.nist.gov/nistpubs/ir/2026/NIST.IR.8547.pdf (landing: https://csrc.nist.gov/pubs/ir/8547/final) | timeline, Mosca, HNDL, hybrids, signatures not HNDL-exposed | 12 |
| Gidney & Ekerå, *How to factor 2048 bit RSA integers in 8 hours using 20 million noisy qubits*, Quantum 5, 433 (2021) | https://arxiv.org/abs/1905.09749 | 20 M qubits / 8 h; assumptions; abstract-circuit formulas | 11 |
| Gidney, *How to factor 2048 bit RSA integers with less than a million noisy qubits* (2025) | https://arxiv.org/abs/2505.15917 | < 1 M qubits / < 1 week; same assumptions as 2019 | 11 |
| RFC 10024, *PQ/T Hybrid Key Agreement Mechanisms for TLS 1.3* (August 2026) | https://www.rfc-editor.org/rfc/rfc10024.html | X25519MLKEM768 name, 1216-byte client share, reversed share order | 12 |
| FIPS 204, *Module-Lattice-Based Digital Signature Standard* | https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf | ML-DSA parameter sets (sizes also measured locally) | 11 |
| Mosca, *Cybersecurity in an era with quantum computers: will we be ready?*, ePrint 2015/1075 | https://eprint.iacr.org/2015/1075 | origin of the x + y > z argument | 9 |
| Smolin, Smith & Vargo, *Pretending to factor large numbers on a quantum computer* (Nature 499, 2013) | https://arxiv.org/abs/1301.7007 | compiled-oracle caveat | 10 |

Considered and dropped: vendor/blog size tables and a news summary of IR 8547 (secondary; used only to locate the
primary PDF, never quoted).

## What was verified, and how
- **NIST IR 8547 final (Oct 2026).** Read the PDF: Tables 2 and 4 list ECDSA, EdDSA, RSA signatures and finite-field DH/MQV,
  EC DH/MQV, RSA key establishment as "Deprecated after 2030, Disallowed after 2035" (all at >= 112 bits; EdDSA >= 128).
  This differs from the November 2024 draft, which split 112-bit (deprecated 2030) from 128-bit (disallowed 2035) - the
  lesson uses the final wording. Sec. 3 states Mosca's X + Y vs Z, names HNDL, and says signatures are not vulnerable to
  HNDL; sec. 3.2.1 allows the SP 800-56C composite Z' = Z || T (and T || Z). The federal 2030/2031 deadlines for high-value
  systems (EO 14412, OMB M-26-15) are mentioned only as context, not used in the plan.
- **RSA-2048 estimates.** arXiv abstracts fetched: GE2019 "20 million noisy qubits", "8 hours", gate error 1e-3, 1 us
  cycle, 10 us reaction time, formulas 3n + 0.002 n lg n qubits and 0.3 n^3 + 0.0005 n^3 lg n Toffolis; Gidney 2025
  "less than a million noisy qubits", "less than a week", "same assumptions as in 2019". The lab stores these strings
  verbatim and evaluates only the published formula at n = 2048 (6190 logical qubits, 2.62e9 Toffolis) via quantum
  lesson 19's code. No other RSA-2048 number appears.
- **X25519MLKEM768.** RFC 10024 sec. 4.1: client share 1216 bytes (1184 ML-KEM + 32 X25519); the name does not follow
  the RFC 9954 order (shares reversed: ML-KEM first); sec. 4.2 server share 1120 bytes (1088 + 32); sec. 4.3 shared
  secret = ML-KEM secret || X25519 secret (64 B); sec. 7.1 codepoint 4588 (0x11EC). Sizes also measured locally via
  cryptography L400 #18's `pq_hybrid` (cryptography 50.0.2 ML-KEM-768). Sec. 6 warns that the security analysis relies
  on the TLS 1.3 transcript and does not carry over to other protocols - hence the lesson's caution that the lab's
  TLS-shaped wire format is a teaching model, not a protocol to deploy.
- **ML-DSA sizes.** Measured locally: ML-DSA-65 public key 1952 B, signature 3309 B; ML-DSA-87 2592 / 4627 B
  (`seams.measured_sizes()`), consistent with FIPS 204.
- **Shor in a simulator.** Ran `shor_sim.py`: N = 15 (a = 7, 12 qubits) P = 0.5, N = 21 (a = 2, 15 qubits) P = 0.3222;
  both equal quantum L500 #25's closed-form distribution (max error < 1e-9). The gate-level N = 15 oracle equals the
  permutation statevector (a first version multiplied by 13 = 7^-1 and still gave P = 0.5 - now a test and a question).
- **Smolin et al.** arXiv abstract: a compiled Shor can "factor" with two qubits; "the correct measure of difficulty ...
  is not the size of number factored, but the length of the period found" - basis for the compiled-oracle caution.

## Not verified / gaps
- Qiskit cross-check (`shor_qiskit.py`) written against the documented Qiskit 2.x API (QFTGate, UnitaryGate.control,
  Statevector.probabilities) but not run here - pending CI.
- The 1,400 B / 6,144 B handshake budget is a stated team constraint, not a standard; real TLS adds certificates.
- z = 10 years is a labelled planning assumption, not a forecast; no source gives a date for a CRQC.
