# Evidence - L600 project 01: Post-quantum secure messaging over a replicated log

Checked 2026-10-30. Primary sources only. Every number in the lesson, the concept note, the ADRs and the 32 questions is
recomputed by `research/checks_01.py` (prints OK, exit 0) from code that ran here: Linux, Python 3.12, cryptography 50.0.2.

## Research questions
1. What exactly must be unique for AES-GCM, and which nonce constructions are allowed? What happens on reuse?
2. Do the hybrid key-share sizes and the strict-length rule we reuse from cryptography L400 #18 match the published spec?
3. Which Raft guarantees make a term-derived nonce unique, and where does the Raft paper put retry deduplication?
4. What does the Idempotency-Key draft say about fingerprints, 400 / 409 / 422?
5. What does a misuse-resistant AEAD leak on nonce reuse (tryIt 1)?

## Sources kept
| Source | URL | Type | Score /12 | What was verified, how |
|---|---|---|---|---|
| NIST SP 800-38D (GCM/GMAC) | https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf | spec | 12 | Fetched. Section 8: the probability that the same IV and key are used on two distinct inputs "shall be no greater than 2^-32", and one repeated IV may allow forgery (Appendix A). Section 8.2: exactly one IV construction per key. Section 8.2.1 deterministic construction = fixed field (device/context) + invocation field. We map this to term (fixed) + counter (invocation). The text of section 8.3 (2^32 total invocations with RBG-based IVs) was beyond the fetched excerpt. It is taken from the cryptography topic's L100/L500 evidence, which cites it, and is consistent with our own birthday computation (risk 2^-32 at 6.07e9 = 2^32.5 messages). |
| RFC 10024 (was draft-ietf-tls-ecdhe-mlkem) | https://datatracker.ietf.org/doc/draft-ietf-tls-ecdhe-mlkem/ | RFC | 12 | Fetched. X25519MLKEM768 client share 1,216 B (1,184 + 32), server share 1,120 B (1,088 + 32), ML-KEM secret first, 64-byte combined secret, IANA 4588 (0x11EC). The client MUST check the ciphertext length and abort with illegal_parameter (our welcome uses lesson 18's strict client). Security considerations: the analysis "relies crucially on the TLS 1.3 message transcript", so a similar hybrid in other protocols is not automatically secure. Quoted in caution and ADR-01-3. |
| NIST FIPS 203 (ML-KEM) | https://csrc.nist.gov/pubs/fips/203/final | standard | 12 | Not re-fetched; already verified for cryptography L400 #18 and cited by RFC 10024 as the normative ML-KEM reference. Sizes were measured here with cryptography 50.0.2 (1,184 B encapsulation key, 1,088 B ciphertext). |
| RFC 8452 (AES-GCM-SIV) | https://www.rfc-editor.org/rfc/rfc8452 | RFC (IRTF) | 11 | Fetched. "Encrypting two messages with the same nonce only discloses whether the messages were equal or not." The RFC recommends GCM-SIV where nonce uniqueness cannot be guaranteed, e.g. "multiple encryptors use the same key". Encryption costs a second pass. tryIt 1 reproduced this: recovery True under GCM, False under GCM-SIV, identical repeats identical under both. |
| Ongaro & Ousterhout, Raft (extended) | https://raft.github.io/raft.pdf | paper | 12 | Fetched. Figure 3: Election Safety ("at most one leader can be elected in a given term"), Leader Append-Only, Log Matching, State Machine Safety. Figure 2: currentTerm and votedFor are persistent and the term increases monotonically. These are the facts behind ADR-01-1's alternative. Section 8 (client interaction: unique serial numbers, state machine filters duplicates) was confirmed through a direct quote of the same rule from Ongaro's thesis (chapter 6) in a GitHub issue (secondary, used only to cross-check). |
| draft-ietf-httpapi-idempotency-key-header-08 | https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/ | IETF draft (work in progress) | 10 | Fetched (version 08, 2026-10-22). Key is a structured-field String, UUID recommended. Fingerprint "MAY" be used. 400 when the key is missing, 422 when reused with a different payload, 409 for a concurrent request. Resources may expire keys. Cited as a draft, not a standard. |
| RFC 9420 (MLS) | https://www.rfc-editor.org/rfc/rfc9420.html | RFC | 12 | Not re-fetched; verified for cryptography L400 #20. Used only for the epoch / ratchet-tree comparison (inRealSystems, scaling limit). |
| pyca/cryptography docs (AEAD, ML-KEM) | https://cryptography.io/en/latest/hazmat/primitives/aead/ | official docs | 11 | API used as documented and verified by running: `AESGCM`, `ChaCha20Poly1305`, `AESGCMSIV` (available in this build), `mlkem.MLKEM768PrivateKey`, `x25519`, `HKDF`. |

Dropped: blog posts and vendor pages about Raft dedupe and nonce reuse (not primary). A third-party "Raft-backed
dedup" runbook turned up in search but is not used.

## What ran and what it showed (numbers recomputed by checks_01.py)
- `run_project.py`: 13/13 lines pass. Key package 1,216 B, welcome 1,180 B (1,088 + 32 + 12 + 48), total 2,396 B
  against a 2,400 B budget. 10,000 messages with 205 seeded leader crashes gave 10,101 sealed ciphertexts, 0 reused
  nonces, and 3 identical replicas showing exactly the 10,000 acknowledged messages. Union bound per epoch (about 2,526
  messages) is 4.0e-23.
- `--inject leader-counter`: 1,500 messages, 49 failovers, 109 reused nonces with values 1-5 among them. XOR with a
  known plaintext recovered "msg 00010 from bob: status green". At `--messages 2000`, F1 shows 43 failovers, 2,022
  sealed and 96 reused.
- Seam guards: `no-apply-dedupe` gives 32 duplicates shown out of 300 messages; `accept-stale-epoch` lets carol read
  1 post-removal message; `local-contract-config` gives readable counts 3 / 5 / 3.
- Replay cost (scaling limit): 1,061,514 state-machine applies in the 10k run (about 106 per message) because every
  restart replays the log from index 1.
- tryIt 2: welcome bytes 4,720 / 36,580 / 119,180 raw (3 / 30 / 100 members + sealer); epoch entries 6,563 / 50,559 /
  164,659 B JSON. Risk 2^-32 after 6.074e9 messages per epoch key. 2^32 messages at 10,000/s take 4.97 days.
- Determinism: the seeded scenarios gave identical numbers in run_project.py, the test run and two runs of checks_01.py.
  Ciphertexts differ per run; no printed number depends on them.

## Known gaps
- macOS / Windows not run (pendingCi). The labs use pathlib, sys.executable, utf-8 and no sockets.
- The welcome is a teaching construction (lesson 18's hybrid derive used as a KEM for wrapping). It has not been
  interop-tested against HPKE PQ/T KEMs or an MLS library (offline sandbox).
- The SP 800-38D section 8.3 wording comes from the cryptography topic's earlier evidence, not from this fetch.
- The Raft simulation has no disk, snapshots or partitions with clocks (lesson 12's model). Crash points are seeded,
  not adversarial.
