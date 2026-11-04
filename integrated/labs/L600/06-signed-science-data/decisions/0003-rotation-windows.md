# 3. Key rotation with retired-key validity windows; dual Ed25519 + ML-DSA-65 release signatures

## Status
Accepted (2026-10-30)

## Context
Science releases are cited for decades and mirrors keep every version forever, so a release key will be rotated
many times while its old signatures must stay checkable. The naive rotation removes the old key from root.json:
`--inject drop-old-key` leaves only v4 verifiable (`old_releases_verify: [4]`), breaking every citation of v1-v3.
Keeping the old key as fully trusted is worse: whoever steals it can sign "v5". Long archive lifetimes also raise the
post-quantum question for signatures: a future attacker forging old-looking releases.

Options:
- A, drop old keys at rotation: old releases fail.
- B, keep old keys trusted: a stolen retired key signs new releases.
- C, retired keys stay listed with `valid_through_version`; a signature counts only if the release version is inside
  its window. Root v2 is signed under TUF section 5.3 rules (threshold of old and new root) and versions must be exactly N+1.

## Decision
C. Release signatures follow cryptography L400 #17's "transition" phase: an Ed25519 AND an ML-DSA-65 signature are
both required (64 + 3,309 bytes); stripping one fails (test_m3). The transparency log fixes the order of releases, so
a retired key cannot quietly re-sign an old version number without a second log entry for monitors to find.

## Consequences
- Measured: v1-v4 verify under root v2; v5 signed with the stolen generation-1 keys is refused
  (`no valid Ed25519 signature from a key trusted for v5`).
- The window is by release version, not wall-clock time: a version number is in the signed data, a time is not
  provable without a trusted timestamp.
- A retired key can still sign a different "v2". Clients that already pinned v2's hash or check the log entry for v2
  catch it; a fresh client needs the log. Revocation for compromise (not routine rotation) should shrink the window and
  re-sign affected releases with the new key.
- Demo keys are derived from fixed seeds for reproducible output; real keys belong in an HSM (cryptography L400 #19)
  and the root key offline.
