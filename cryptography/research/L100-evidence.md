# L100 research evidence – Applied Cryptography

Research date: 2026-10-28. Method: per lesson 2-3 implementation questions → web_search/web_fetch of official docs, RFCs, NIST, maintained OSS docs → screen → score (implementable, current, authoritative, open, transferable, right depth; 0-2 each) → keep ≥ 8/12 → cross-check each claim against ≥ 2 sources (≥ 1 official) and, where possible, against local execution.

Local environment facts (observed): Python 3.12.15; `cryptography.__version__` = 50.0.2; bundled `OpenSSL 4.0.3 29 Sep 2026`; `hashlib` has sha256/sha3/blake2; no `nacl`, no `openssl` CLI; `sha256sum` (coreutils 9.4) present; Node 24.7.0 (OpenSSL 3.5.2).

---

## Lesson 1 – Set up your crypto workbench
**Questions**: Which cryptography version is current and which Python does it support? Does the wheel bundle OpenSSL (which version)? Is Argon2id available on that version?

| Candidate | Decision | Score |
|---|---|---|
| PyPI cryptography | kept | 9 |
| cryptography.io Installation | kept | 10 |
| cryptography.io Changelog | kept | 10 |
| github.com/pyca/cryptography | dropped – fetch withheld | – |

**Key facts**
- Latest release on PyPI is 50.0.2; supports Python 3.9+ and PyPy3 7.3.11+. (https://pypi.org/project/cryptography/) – local `pip`-installed version is 50.0.2.
- 50.0.2 (2026-09-30) wheels are compiled with OpenSSL 4.0.3. (https://cryptography.io/en/latest/changelog/) – local `openssl_version_text()` = OpenSSL 4.0.3.
- Linux users on a recent pip get a manylinux binary wheel; Rust is only needed to build from source. (https://cryptography.io/en/latest/installation/)
- Licence `Apache-2.0 OR BSD-3-Clause` (local package metadata).

## Lesson 2 – Hashing and integrity
**Questions**: How to hash a large file without loading it into memory? What official vectors exist for SHA-256 and HMAC-SHA-256? How to compare MACs safely?

| Candidate | Decision | Score |
|---|---|---|
| Python hashlib docs | kept | 12 |
| Python hmac docs | kept | 12 |
| NIST SHA256.pdf example | kept | 10 |
| RFC 4231 | kept | 10 |
| OpenSSL openssl-dgst(1) | kept | 10 |

**Key facts**
- `update(a); update(b)` equals `update(a+b)` → streaming hash; `hashlib.file_digest` added in 3.11. (https://docs.python.org/3/library/hashlib.html) – verified locally (streaming == one-shot == `file_digest` == `sha256sum`).
- SHA-256("abc") = BA7816BF 8F01CFEA 414140DE 5DAE2223 B00361A3 96177A9C B410FF61 F20015AD. (NIST SHA256.pdf) – verified locally.
- RFC 4231 TC2: key "Jefe", data "what do ya want for nothing?" → HMAC-SHA-256 5bdcc146…64ec3843. (https://www.rfc-editor.org/rfc/rfc4231.html) – verified locally.
- Use `compare_digest()` instead of `==` to reduce timing-attack exposure. (https://docs.python.org/3/library/hmac.html; RFC 8439 §4 also requires constant-time tag comparison)
- `openssl dgst` default digest is SHA-256; `openssl mac` preferred over `-hmac`. (https://docs.openssl.org/master/man1/openssl-dgst/)
- Hashing a password with plain SHA-256 is unsuitable. (hashlib docs warning; OWASP cheat sheet)

## Lesson 3 – Secure randomness
**Questions**: What does Python document as the secure source for tokens/keys? How many bytes? Why is `random` unsafe, concretely?

| Candidate | Decision | Score |
|---|---|---|
| Python secrets docs | kept | 12 |
| Python random docs | kept | 11 |
| RFC 8439 (nonce uniqueness) | kept | 11 |
| Node.js crypto (randomBytes) | kept | 10 |

**Key facts**
- `secrets` should be used in preference to `random`, which is designed for modelling/simulation, not security. (https://docs.python.org/3/library/secrets.html)
- Mersenne Twister is deterministic and "completely unsuitable for cryptographic purposes"; `random.seed(int)` reproduces sequences. (https://docs.python.org/3/library/random.html) – demonstrated locally: clock-seeded token recovered in 0.078 s.
- 32 bytes (256 bits) considered sufficient for typical use (as of 2015); `DEFAULT_ENTROPY` may change. (secrets docs)
- Nonces must not repeat for a key. (RFC 8439 §2.3, §4)

## Lesson 4 – Authenticated encryption
**Questions**: Exact pyca API for AES-GCM / ChaCha20-Poly1305 (nonce size, tag, exception)? Which official vectors can be run directly? What happens on nonce reuse?

| Candidate | Decision | Score |
|---|---|---|
| cryptography.io AEAD docs | kept | 12 |
| RFC 8439 | kept | 11 |
| GCM revised spec (McGrew & Viega) | kept (values not extracted, see gaps) | 8 |
| Go crypto/cipher | kept | 10 |
| Java Cipher (JDK 21) | kept | 8 |
| OpenSSL openssl-enc(1) | kept | 10 |
| draft-mcgrew-gcm-test-01 | dropped – expired draft, ESP-specific | 5 |
| riscv-crypto aes-gcm-test.c | dropped – fetch failed | – |
| voltaire.tevm.sh vectors | secondary cross-check only | 6 |

**Key facts**
- `encrypt(nonce, data, associated_data)` returns ciphertext with a 16-byte tag appended; ChaCha20Poly1305 nonce is 12 bytes; NIST recommends 96-bit IV for AESGCM; `decrypt` raises `InvalidTag` when ciphertext, key, nonce or AAD is wrong; "NEVER REUSE A NONCE with a key". (https://cryptography.io/en/latest/hazmat/primitives/aead/) – verified locally.
- RFC 8439 §2.8.2 vector: key 80..9f, constant 07000000, IV 4041424344454647, AAD 50515253c0c1c2c3c4c5c6c7 → tag 1ae10b594f09e26a7e902ecbd0600691. (https://www.rfc-editor.org/rfc/rfc8439.html) – verified locally byte-for-byte.
- Repeated nonce → identical keystream; XOR of plaintexts = XOR of ciphertexts. (RFC 8439 §4) – demonstrated locally with AES-GCM.
- GCM IV must be distinct per key; repeated IVs subject to forgery (Java Cipher docs); random-nonce GCM: max 2^32 messages per key (Go `NewGCMWithRandomNonce` docs).
- `openssl enc` does not support GCM/CCM and will not; use `openssl cms`. (https://docs.openssl.org/master/man1/openssl-enc/)

## Lesson 5 – Password storage
**Questions**: Does cryptography 50 expose Argon2id in `hazmat.primitives.kdf.argon2` (docs and locally)? Current OWASP parameters? Official Argon2id/scrypt vectors?

| Candidate | Decision | Score |
|---|---|---|
| cryptography.io KDF docs | kept | 12 |
| OWASP Password Storage Cheat Sheet | kept | 11 |
| RFC 9106 | kept | 11 |
| RFC 7914 | kept | 10 |
| cryptography.io Changelog | kept | 10 |
| PyNaCl password hashing | kept | 9 |
| Go x/crypto/argon2 | kept | 10 |

**Key facts**
- `Argon2id(*, salt, length, iterations, lanes, memory_cost, ad=None, secret=None)` added in 44.0.0; `derive_phc_encoded` / `verify_phc_encoded` added in 45.0.0; memory_cost in KiB, ≥ 8×lanes; raises UnsupportedAlgorithm if OpenSSL lacks Argon2id. (KDF docs; changelog: "Added support for Argon2id when using OpenSSL 3.2.0+" in 44.0.0) – **verified locally**: import succeeds on 50.0.2 and module exposes `Argon2d, Argon2i, Argon2id`; methods `derive, derive_into, derive_phc_encoded, verify, verify_phc_encoded`.
- OWASP (checked 2026-10-28): Argon2id minimum m=19 MiB, t=2, p=1 (equivalents: 46 MiB/t=1, 12 MiB/t=3, 9 MiB/t=4, 7 MiB/t=5); scrypt fallback N=2^17, r=8, p=1; bcrypt ≥10 legacy only; PBKDF2-HMAC-SHA256 600,000 for FIPS; hash should generally take < 1 s. (https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- RFC 9106: 16-byte salt recommended; first recommended option t=1, p=4, 2 GiB; second t=3, p=4, 64 MiB; §5.3 Argon2id vector tag 0d640df5…6b01e659. (https://www.rfc-editor.org/rfc/rfc9106.html) – vector verified locally.
- RFC 7914 §12: scrypt("password","NaCl",1024,8,16,64) = fdbabe1c…cc0640. – verified locally.
- PyNaCl/libsodium default `pwhash.str` is argon2id. (PyNaCl docs)

## Lesson 6 – Encoding vs hashing vs encryption
**Questions**: What does the base64 spec say about security? Official base64/base16 vectors? Authoritative statement on hashing vs encryption for secrets?

| Candidate | Decision | Score |
|---|---|---|
| RFC 4648 | kept | 10 |
| Python base64 docs | kept | 11 |
| OWASP Password Storage (hashing vs encryption section) | kept | 11 |
| cryptography.io AEAD docs | kept | 12 |
| hsmkit.com guide | dropped – vendor product funnel | 4 |

**Key facts**
- "Base encoding visually hides otherwise easily recognized information, such as passwords, but does not provide any computational confidentiality." (RFC 4648 §12)
- BASE64("foobar") = "Zm9vYmFy", BASE16("foobar") = "666F6F626172". (RFC 4648 §10) – verified locally.
- Hashing is one-way; encryption is two-way, so attackers with the key can recover plaintext; passwords should be hashed. (OWASP cheat sheet, "Hashing vs Encryption")
- Python base64 docs point to RFC 4648 §12 security considerations. (https://docs.python.org/3/library/base64.html)

---

## Concepts layer (added 2026-10-28)
**Questions**: Where do these primitives show up in widely used open-source protocols/software? Which official sources back each "In real systems" bullet? Is there an official NIST URL to replace the unofficial GCM mirror?

| Candidate | Decision | Score |
|---|---|---|
| NIST SP 800-38D (nvlpubs.nist.gov) | kept – replaces csrc.nist.rip mirror | 11 |
| csrc.nist.gov …/proposed-modes/gcm/gcm-spec.pdf | dropped – fetch returned no document | – |
| RFC 8446 (TLS 1.3) | kept | 10 |
| WireGuard protocol page | kept | 9 |
| pip secure installs | kept | 10 |
| RFC 7518 (JWA) | kept | 9 |
| RFC 7617 (HTTP Basic) | kept | 9 |
| Python `os` docs (os.urandom) | dropped – page truncated before the relevant section | – |

**Key facts**
- GCM IV uniqueness: probability of repeating an IV under one key shall be ≤ 2^-32; a repeated IV may enable forgery; 96-bit IVs recommended. (NIST SP 800-38D §5.2.1.1, §8)
- TLS 1.3 keeps only AEAD algorithms; uses HKDF; Finished is a MAC over the handshake; ClientHello.random is 32 bytes from a secure RNG. (RFC 8446 §1.2, §2, §4.1.2)
- WireGuard: ChaCha20-Poly1305 (RFC 7539 AEAD) with a 64-bit counter nonce, BLAKE2s, Curve25519, HKDF; "Nonces are never reused"; sliding replay window. (wireguard.com/protocol)
- pip `--require-hashes`: local sha256 hashes protect against remote tampering; requirements must be pinned with `==`; md5/sha1/sha224 excluded. (pip secure installs)
- HS256 = HMAC-SHA-256, key ≥ 256 bits, constant-time comparison MUST be used. (RFC 7518 §3.2)
- HTTP Basic sends base64(user:pass); example `QWxhZGRpbjpvcGVuIHNlc2FtZQ==`; not secure without TLS. (RFC 7617 §1, §2, §4) – example re-computed locally.
- PEM wraps base64-encoded DER between header/footer lines. (Node.js crypto docs)

**Worked-example provenance**: every number in `content/concepts/*.md` and `documentation/CONCEPTS-PRIMER.md` was produced by `research/concept_examples.py`; output captured in `research/concept_examples.out.txt` (avalanche 122/256 bits, Random(42) outputs, 7,201 ≈ 2^12.8 seeds, 10^6 ≈ 2^19.93, RFC 8439 114→130 bytes, nonce-reuse XOR `13110013…4a00`, Argon2id PHC strings for fixed salts, SHA-256 vs Argon2id guess rates, base64/hex sizes). Word counts measured with `wc -w` (primer 825; notes 627–650).


## Rebalance (2026-10-28, REBALANCE-SPEC.md)
- Concept share measured with the spec script: before concept 3912 / hands-on 4621 = 46%; after concept 1495 / hands-on 5912 = 20%.
- Notes trimmed to 240-247 words (wc -w), 4 headings, 3 "How it works" points each mapped to a lab step; primer trimmed 825 → 488 words. No new numbers: all retained values come from `research/concept_examples.out.txt`, the lab outputs or the new `try_it.py` runs.
- Removed note sections moved to L100.json: `inRealSystems`, `useWhen`, `checkYourself` (2 per lesson), `next`; "Go deeper" links merged into `sources` (deduplicated by URL; all were already retrieved sources in VERIFIED-RESOURCES).
- `tryIt`: 12 experiments in `labs/L100/*/try_it.py`, all run locally with cryptography 50.0.2 (Python 3.12); observed output recorded in `expected` and the lab README. CI runs them (the workflow runs every non-test script).


## Platform + local-agent pass (2026-10-28, PLATFORM-AGENT-SPEC.md)
Research questions: (1) Does each OS ship an OpenSSL CLI, and do the labs depend on it? (2) What are the verified install ids for Python/OpenSSL/Ollama on macOS (Homebrew) and Windows (winget)? (3) Which lab code is POSIX-only? (4) Where does a local agent honestly help in L100 crypto, and what deterministic check judges it?

Sources considered:
| Candidate | Kept/dropped | Reason / score |
|---|---|---|
| cryptography.io installation | kept (already listed) | official: static wheels for macOS, Windows, Linux; "does not support the OpenSSL/LibreSSL libraries Apple ships" |
| formulae.brew.sh openssl@3 / python@3.12 / ollama-app | kept 10/10/9 | official package index, Apple-silicon bottles |
| docs.python.org venv | kept 12 | Activate.ps1, Set-ExecutionPolicy RemoteSigned -Scope CurrentUser |
| winget-pkgs Python.Python.3.12 tree | kept 9 | official manifest repo (search result only) |
| winstall / winget.ragerworks ShiningLight.OpenSSL.Light | kept 8 (winstall) | third-party winget indexes agreeing on the id |
| vmheaven.io "Install OpenSSL on Windows" | cross-check only (6) | useful facts (no openssl.exe in Windows, Git Bash copy, PATH, UTF-16 redirect) but page ends in a hosting ad |
| picklog.cc "Update OpenSSL on Mac" | cross-check only (5) | macOS 26.4.1 `/usr/bin/openssl version` = LibreSSL 3.3.6; single blog, AI-run site |
| ssldragon.com check-openssl-version | dropped (5) | vendor page; only confirms "LibreSSL on a stock Mac" |
| learn.microsoft.com Get-FileHash | kept 11 | SHA256 default, output object |
| docs.github.com hosted runners | kept 11 | macos-latest arm64 (M1), windows-latest x64 |
| docs.ollama.com openai-compatibility / gpu | kept 11/11 | /v1/chat/completions at localhost:11434; Metal, NVIDIA CC 5.0+, ROCm, Vulkan |
| ollama.com library qwen2.5:1.5b | kept 9 | 986 MB, Apache-2.0 |
| winget.tech / wingetly Ollama.Ollama | kept 8 (winget.tech) | id Ollama.Ollama agrees in both |
| docs.python.org ast | kept 12 | Call/Attribute/Constant nodes, 1-indexed lineno (used by misuse_lint.py) |

Key facts:
- Labs never use a system OpenSSL: the pinned wheel bundles OpenSSL 4.0.3 (observed) and is statically linked on macOS and Windows (cryptography installation docs).
- macOS: `/usr/bin/openssl` is LibreSSL (cryptography docs mention Apple's OpenSSL/LibreSSL; picklog observed LibreSSL 3.3.6 on macOS 26.4.1). Homebrew `openssl@3` (3.5.9) is keg-only.
- Windows: no openssl.exe ships with Windows (vmheaven); options: `winget install -e --id ShiningLight.OpenSSL.Light`, Git for Windows (Git Bash only). Built-in hashing: `Get-FileHash` (SHA256 default), `certutil -hashfile`.
- Cross-platform code fixes: lab 2 `sha256sum`-only CLI comparison replaced by `os_sha256()` (sha256sum → shasum -a 256 → certutil, regex-parsed, Git Bash `\`-escaped output handled) + pathlib; lab 6 `base64 -d` replaced by `python -m base64 -d`; lab 1 prints `machine` (Darwin arm64 / Windows AMD64 expected). Grep found no SIGALRM/fork/os.uname/hard-coded /tmp; the only server binds 127.0.0.1.
- Agent assist (lesson 6): a deliberately naive fake reviewer confirms 2 of 3 misuses, misses the constant-nonce reuse and over-flags a correct SHA-256 fingerprint; the AST linter is authoritative (observed output in the lab README and `agentAssist.expected`).

## Update 2026-10-28 (review finding F06)
The third-party winget indexes kept above (winstall, ragerworks, vmheaven, winget.tech, wingetly) are no longer cited.
`ShiningLight.OpenSSL.Light` is now backed by the winget-pkgs manifest folder (fetched; 3.6.0–4.1.0). Ollama follows the
shared WORKSTATION-SETUP: on macOS `brew install ollama` + `brew services start ollama` (formulae.brew.sh/formula/ollama,
fetched); on Windows the installer from ollama.com/download/windows (fetched).
