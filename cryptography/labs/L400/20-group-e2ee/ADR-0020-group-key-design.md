# ADR-0020: Group messaging uses an MLS-style ratchet tree with epochs; removal blanks the removed path

## Status
Accepted for design (2026-10-28, lesson 20 lab). The toy tree is a teaching model. Production uses a reviewed RFC 9420
implementation such as OpenMLS (MIT, Rust); its equivalence check is pending CI.

## Context
Project rooms hold 8–256 members who join and leave every week. Requirements: (1) a removed member must not read
anything sent after removal; (2) a member whose device was compromised must be able to recover (post-compromise
security); (3) removal must stay cheap as rooms grow. Measured in `compare_designs.py` (encryptions done by the sender or committer):

| Design | Per message (n=256) | Per removal n=8 / 64 / 256 | Bytes per removal at 256 |
|---|---|---|---|
| Pairwise fan-out | 255 | 0 / 0 / 0 | 0, but every message costs 255 AEAD encryptions |
| Sender keys | 1 | 42 / 3,906 / 64,770 | ≈5.2 MB |
| MLS-style tree (toy) | 1 | 4 / 10 / 14 | 1,120 |

Removing the last member of a 256-member room took ≈90 ms in total for the toy, including all 255 members processing the commit in Python.

## Decision
1. Use one group epoch secret per epoch. Application keys come from `HKDF(epoch_secret, "app")`, and messages carry their epoch.
2. Every membership change or key update is a Commit with fresh entropy. The new path secrets are HPKE-encrypted to the resolution of each copath node, about log2(n) encryptions. The next epoch is `HKDF(init_secret || commit_secret)`.
3. A Remove blanks the removed leaf **and its whole direct path** before the Commit (RFC 9420 §12.1.3).
4. Members send an empty Commit (update) regularly, for example daily or when they become active again. This bounds the window an attacker gains from a compromised device.
5. Fitness function: `test_fitness_removal.py`. In a seeded random sequence of removals and updates (n=16), no removed member reads a later epoch, every current member does, and no commit costs more than 2·log2(n) HPKE encryptions.

## Consequences
- Removal cost grows with log n. It stays practical at 256, where sender keys need about 65,000 public-key encryptions.
- Commits must be totally ordered per group: two concurrent commits fork the epoch. That needs a delivery service that sequences commits (MLS's DS role), plus the fork-resolution tooling OpenMLS documents.
- The toy omits signatures on commits, credentials (the authentication service), tree hashes, the Welcome message and the secret tree; all of these are mandatory in MLS. Do not ship the toy.
- Pairwise fan-out remains acceptable for groups under about 5 people when simplicity beats bandwidth; the Signal-style double ratchet per pair then provides FS and PCS.
- The seeded fault shows that a single missing step, not blanking the path, breaks removal in 48 of 56 committer/removed pairs, and the lab's ordinary sync tests do not notice. Only the fitness test catches it.
