# ADR-01-1: Random 96-bit nonces for message AEAD, not a leader-local counter

## Status
Accepted (L600 project 01, 2026-10-30). Fitness functions: F1 "no nonce reuse across 10k messages with random
failovers" and F4 "rotate before the random-nonce limit" in `run_project.py`; build task `tests/test_p01_build_task.py`.

## Context
Messages are sealed with AES-256-GCM under one epoch key that every replica's sealer shares (the sealer identity is
welcomed into each epoch like a member). Whoever is Raft leader seals. GCM is counter mode underneath: the same key and
nonce on two different messages repeats the keystream, so XOR of the ciphertexts equals XOR of the plaintexts, and the
GHASH key can be recovered for forgeries (NIST SP 800-38D, section 8 and Appendix A).
The first design used a per-sealer counter (`nonce_derived.py`, shipped). It lives in the leader's memory, is not
replicated, and ignores the term. After a failover the new leader starts again at 1 under the same key. On the seeded
failure lab (1,500 messages, 49 failovers) lesson 15's scan found 109 reused nonces, and one known plaintext
recovered another member's message.

## Decision
Draw every message nonce from the OS CSPRNG (`os.urandom(12)`, `RandomNonce`). Keep no nonce state. Any node may seal,
and a restart needs nothing to recover. The sealer refuses to seal once an epoch reaches `MAX_MSGS_PER_EPOCH = 2^32`
(NIST SP 800-38D section 8.3 limit for RBG-based IVs). Membership changes rotate the key much earlier anyway.
Alternative kept and tested: `solution/nonce_derived.py` = term (4 B) || per-term counter (8 B). This is the deterministic
construction of SP 800-38D section 8.2.1, with the Raft term as the "fixed field". Raft's Election Safety makes it
unique as long as only the leader seals.

## Consequences
- 10,000 messages with 205 seeded leader crashes: 0 reused nonces across 10,101 sealed ciphertexts. The birthday
  bound for 2,526 messages per epoch is 4.0e-23.
- No coupling between the crypto layer and consensus internals: the sealer never reads the term.
- Per-key volume is capped near 2^32 messages. The counter alternative removes that cap but makes the crypto depend
  on "only the leader seals" and "terms are durable". Both are invariants a later refactor (follower sealing, a load
  balancer in front of every node) could break silently.
- A misuse-resistant AEAD (AES-GCM-SIV, RFC 8452) is the defence-in-depth option. tryIt 1 shows the same reuse leaks
  nothing beyond equality there. It costs a second pass on encryption.
