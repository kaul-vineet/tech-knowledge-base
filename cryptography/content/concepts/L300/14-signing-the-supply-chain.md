## Why it matters
Your installer downloads a release, checks "the signature" and runs the code. Attackers rarely break Ed25519. Instead they change what the signature does not cover: a file swapped on a mirror, an extra plugin dropped next to the signed files, or a release signed by a key that should have been retired. Signing a *manifest of digests* lets one signature cover many files, but only if the install step checks every file against it.

## Mental model
The manifest is a **sealed packing list**. The seal (the signature) proves who wrote the list. Only counting the boxes against the list proves the delivery matches it.

```
build ─▶ files ─▶ MANIFEST.json {path: sha256, size} ─▶ Ed25519 sig (kid) ─▶ publish
install: pinned kid? ─▶ sig over exact bytes? ─▶ same set of files? ─▶ every digest + size? ─▶ copy
```

## How it works
1. **Seeded build and manifest.** The lab builds four files from a seeded generator, so the bytes are identical on every machine. It lists each file's SHA-256 and size under a POSIX path (`app/core.py`, also on Windows) and signs the exact manifest bytes with Ed25519 → see lab step 1.
2. **Pinned signers.** The signature file names a key ID (first 16 hex characters of SHA-256 of the public key). The installer only knows the kids it pins; an unknown signer is rejected before any crypto runs → see lab step 2.
3. **The fault.** A seeded attacker swaps one listed file and adds an unlisted `app/zz_extra.pth`, keeping the old manifest and signature. The naive installer checks the signature, sees all listed files present, and copies 5 files → see lab step 3.
4. **Strict install.** The fix compares the set of files with the manifest in both directions, then checks every size and digest before copying anything → see lab step 5.
5. **Signer rotation.** A keyring holds the old and new kid during a rotation window. When the old kid is removed, releases signed with it no longer install → see tryIt 1. minisign and cosign `sign-blob` do the same job with their own formats → see lab step 6.

Worked example (one lab run): `app/core.py` is 540 bytes with SHA-256 `b9dc24f7…516c`. The seeded attack swapped `README.txt` and added `app/zz_extra.pth`. The naive installer printed `installed 5 files`. The strict one printed `REJECTED: unknown file(s): ['app/zz_extra.pth']`, and with only the swap, `digest mismatch`. Changing one hex digit inside MANIFEST.json gave `manifest signature invalid`.

## Failure modes
- **Unchecked files.** The install step trusts the folder, not the list. You notice when a reproducible-build diff or an extra file in the install tree shows up, or you never notice.
- **Partial verification.** Checking a sample of digests, or copying while verifying, leaves a half-installed tampered release.
- **Stale signer keys.** A leaked old key keeps signing valid-looking releases until its kid is removed from every installer.
- **Mirror rollback.** An attacker serves an older, validly signed release. Frameworks like TUF add version and expiry metadata for this; the lab does not.

## Common mistakes
- Signing each file separately and forgetting the files nobody signed.
- Verifying a re-serialized manifest instead of the exact signed bytes.
- Shipping the private signing key in the build image instead of a CI secret or KMS.
