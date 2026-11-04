# 02 – Hashing and integrity (SHA-256, HMAC)

## Run
```bash
python hash_and_hmac.py
python -m unittest -v     # 4 tests
```

## Expected output (observed locally; file hash is deterministic, HMAC key is random)
```
sha256('abc')        ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad True
sha256('')           e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 True
file (python)        e23c0cda5bcdecddec446b54439995c7260c8cdcf2953eec9f5cdb6948e5898d
file (OS tool)       e23c0cda5bcdecddec446b54439995c7260c8cdcf2953eec9f5cdb6948e5898d via sha256sum
stdlib file_digest   e23c0cda5bcdecddec446b54439995c7260c8cdcf2953eec9f5cdb6948e5898d
after 1-byte tamper  64ae272a9529a4637e6f2a81ed6e1cc111f52f288435df80c2871c416c450eeb MISMATCH -> tampered
HMAC RFC4231 TC2     5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843 True
verify good msg      True
verify edited msg    False
verify wrong key     False
```
`file (OS tool)` uses the first hashing tool the OS has: `sha256sum` (Linux, Git Bash), `shasum -a 256` (macOS), `certutil -hashfile <file> SHA256` (Windows); it prints `None via None` if none is found. Expected on the Mac mini: `via shasum` (or `via sha256sum` if coreutils is installed); on Windows PowerShell: `via certutil` (CI runs bash, so it finds Git's `sha256sum`). PowerShell users can also compare with `Get-FileHash <file>` (SHA256 by default, upper-case hex).

## Vectors
- SHA-256("abc"): NIST example values (FIPS 180).
- HMAC-SHA-256 key "Jefe": RFC 4231 test case 2.

## If it fails
| Symptom | Action |
|---|---|
| Hash of your text differs from another tool | Check encoding/newlines: `echo` adds `\n`; use `printf` (zsh/bash) or `Set-Content -NoNewline` (PowerShell) |

## Try it (concept experiments)
1. Hash the same 1 MB file with `chunk_size` 7, 4096 and 65536. *Predict first*, then compare.
2. Change the HMAC key `Jefe` -> `jefe` and verify the original tag. *Predict first*, then compare.

```bash
python try_it.py
```
Observed locally (cryptography 50.0.2):
```
1) chunk sizes [7, 4096, 65536] -> distinct digests: 1 | digest: e23c0cda5bcdecdd...
2) jefe tag: f5886a2776d40a67... | verifies against Jefe tag: False | bits differing: 136 of 256
```
