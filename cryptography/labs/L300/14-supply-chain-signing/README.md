# 14 – Signing the software supply chain

Read first: `content/concepts/L300/14-signing-the-supply-chain.md`. Full lesson (steps, walkthrough, failure lab, trade-offs, sources): `content/L300.json` (lesson 14).

## Run (same commands on macOS and Windows inside the activated venv)
```bash
python release_sign.py
python -m unittest -v
python try_it.py
python tool_check.py          # SHA-256 of one artifact, for the CyberChef check
python tool_check.py --out release_demo   # also writes the signed demo release for the minisign exercise
```

## Expected output (observed locally: Python 3.12.15, cryptography 50.0.2, Linux sandbox)
```
manifest lists 4 files; signer 4793bac0a5cc620b
clean release                installed 4 files
installer pins another key   REJECTED: unknown signer 4793bac0a5cc620b
fault: attacker swapped README.txt and added app/zz_extra.pth; manifest + signature unchanged
tampered release             installed 5 files
```
Keys, key IDs, serial numbers and nanosecond timings are random or machine-dependent and change per run; everything else is seeded.

Tests (`python -m unittest -v`, all test files in this folder):
```
Ran 9 tests in 0.159s
OK (skipped=1)
```

## Failure lab: break it, then harden it
**Fault (seeded):** `tamper(dist, seed=14)` swaps the content of one listed file (seeded choice: `README.txt`) and adds an unlisted `app/zz_extra.pth`, keeping the old MANIFEST.json and its valid signature.

**Symptom:** see the output above (`tampered release             installed 5 files`).

**Fix = build task:** make `install()` verify the signature by a pinned key, reject unknown and missing files, and check every size and SHA-256 digest BEFORE copying anything.

Hints: Compare `set(manifest['files'])` with the set of files on disk in both directions. · Use `hmac.compare_digest` for the digest strings and copy only after every check passed.

Reference solution: `solution_strict.py` → `python solution_strict.py` prints:
```
clean release:    4 files installed
tampered release: REJECTED: unknown file(s): ['app/zz_extra.pth']
```
**Proof** (`test_build_task.py`). Against the reference solution:
```
Ran 4 tests in 0.107s
OK
```
Against the unfixed lab file (observed — this is the "fails before"):
```
FAIL: test_seeded_attack_rejected (test_build_task.TestStrictInstall.test_seeded_attack_rejected)
FAIL: test_swapped_file_rejected (test_build_task.TestStrictInstall.test_swapped_file_rejected)
FAIL: test_unknown_file_rejected (test_build_task.TestStrictInstall.test_unknown_file_rejected)
Ran 4 tests in 0.152s
FAILED (failures=3)
```
Test **your** `release_sign.py`:

macOS (zsh): `BUILD_IMPL=release_sign python -m unittest -v test_build_task`  
Windows (PowerShell): `$env:BUILD_IMPL="release_sign"; python -m unittest -v test_build_task; Remove-Item Env:BUILD_IMPL`

## Try it (predict first)
1. Rotate the release key: trust old + new kid, then remove the old kid. *Predict:* Which releases still install?
2. Change one hex digit of a digest inside MANIFEST.json (an attacker 'fixing' the hash). *Predict:* Digest error or signature error?

```bash
python try_it.py
```
Observed locally:
```
1) both keys trusted  v1.0.0: 4 files                                  v2.0.0: 4 files
1) old key removed    v1.0.0: REJECTED (unknown signer 34750f98bd59fcfc) v2.0.0: 4 files
2) one hex digit changed in MANIFEST.json: manifest signature invalid
```

## Equivalent tools (pending CI)
`test_cli_equivalents.py` signs and verifies the lab's MANIFEST.json with **minisign** (ISC; 0.12) and is skipped when minisign is not installed (as here). CI installs it with Homebrew on macOS. Install: macOS `brew install minisign`; Windows `winget install -e --id jedisct1.minisign`. The flags used (`-G -W`, `-S -s -m`, `-V -p -m`) come from the minisign release notes; the full docs page could not be fetched (KNOWN-GAPS).

**Sigstore cosign** (Apache-2.0; v3.1.4) does the same for blobs with a key pair: `cosign generate-key-pair`, then `cosign sign-blob --key cosign.key --bundle MANIFEST.bundle.json MANIFEST.json` (add `--yes` in CI). Verify with `cosign verify-blob` and the bundle. Not run here: by default cosign also talks to the public transparency log. Install: `brew install cosign`; `winget install -e --id Sigstore.Cosign`.

## Learning tool check (CyberChef)
```
first line of app/core.py: # app/core.py build 645795
lines: 20 identical lines, each ending with \n; size 540 bytes
sha256: b9dc24f7d532058c476aec857dac72ac30b147cd4fe6acd171f31a435d6e516c
```
In CyberChef, rebuild the file text (20 copies of the first line, each ending in a newline) and run SHA2 (256): the hash must match. A mismatch usually means a missing final newline.

## Learning tool: minisign (pending a manual run)
minisign 0.12 (ISC). macOS: `brew install minisign`. Windows: the Win64 zip from https://github.com/jedisct1/minisign/releases. Write the seeded release to a folder, then sign and verify its manifest:
```
python tool_check.py --out release_demo
wrote 6 files to release_demo | manifest: release_demo/MANIFEST.json
```
Same commands on both machines (from `release_demo`): `minisign -G -W -p ms.pub -s ms.key` (unencrypted demo key), `minisign -S -s ms.key -m MANIFEST.json`, `minisign -V -p ms.pub -m MANIFEST.json`. Then change one hex digit of the `app/core.py` digest (`b9dc24f7…516c`) in MANIFEST.json and verify again. The first verify must pass and the second must fail. That is the same verdict as tryIt 2 (`one hex digit changed in MANIFEST.json: manifest signature invalid`): the signature covers the digests, so an attacker cannot "fix" a hash. Delete `release_demo` and the demo keys afterwards.

## If it fails
| Symptom | Action |
|---|---|
| `unknown signer` | The installer pins other key IDs: add the new kid during a rotation window. |
| `manifest signature invalid` | MANIFEST.json changed after signing (even whitespace): re-sign; never re-serialize before verifying. |
| Digests differ only on Windows | Files opened in text mode change line endings: read and write artifacts in binary mode. |
| minisign test skipped | Expected without minisign; install it to run the equivalence test. |
