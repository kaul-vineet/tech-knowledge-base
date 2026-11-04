# Known gaps – Applied Cryptography L100

## Not verified / partially verified
1. **CI not executed.** `.github/workflows/labs.yml` was syntax-checked (YAML parse) and its run loop was simulated locally, but it has not run on GitHub. macOS/Windows runners, Python 3.13, and the action tags `actions/checkout@v7.0.1` / `actions/setup-python@v7.1.0` (taken from the setup-python releases page seen in a web search, not fetched) are unverified. Actions are pinned by tag, not by full commit SHA (SHA not retrieved).
2. **GCM test case 14 values / unofficial mirror removed (2026-10-28).** The earlier source link (csrc.nist.rip copy of the McGrew & Viega GCM spec) was an unofficial mirror and has been removed from L100.json and VERIFIED-RESOURCES. It is replaced by the official **NIST SP 800-38D** (https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf, retrieved), which defines GCM normatively but does **not** contain test case 14. The official NIST-hosted copy of the original spec (csrc.nist.gov/CSRC/media/Projects/Block-Cipher-Techniques/documents/BCM/proposed-modes/gcm/gcm-spec.pdf) was tried and returned no document. So the TC14 hex (`cea7403d…9d18` / tag `d0d1c8a7…b919`) currently rests on: the GCM spec appendix (not extractable from any retrieved official copy), a secondary page (voltaire.tevm.sh, search result) and local pyca/OpenSSL output. Upgrade path: replace with a vector from NIST CAVP `gcmEncryptExtIV256.rsp` once fetchable.
3. **Equivalent API names not individually fetched.** libsodium function names (`crypto_generichash`, `crypto_auth`, `randombytes_buf`, `sodium_bin2base64`, `crypto_secretbox`), `golang.org/x/crypto/chacha20poly1305`, Go `crypto/sha256`/`crypto/hmac`/`crypto/rand`, Java `MessageDigest`, `Mac`, `SecureRandom`, `HexFormat`, and `openssl rand` / `openssl base64` / `openssl cms` usage come from general knowledge and the fetched pages' cross-references, not from a dedicated fetched page each. None of these were executed (no OpenSSL CLI, PyNaCl, Go or Java in the sandbox).
4. **Node.js equivalents** were checked against the v26 docs and `crypto.argon2Sync` exists in the local Node 24.7 (typeof = function), but no Node code was run.
5. **Licences**: OWASP cheat sheet, PyNaCl docs and Python docs licences were not displayed on the fetched pages; marked "unverified" in VERIFIED-RESOURCES. pyca/cryptography licence (`Apache-2.0 OR BSD-3-Clause`) is from the installed package metadata; the GitHub repo page was withheld by the fetch tool.
6. **Timings** (Argon2id ≈0.12 s, scrypt N=2^17 ≈1.5 s) are from the sandbox only; real servers differ. OWASP asks you to benchmark.

## Concepts layer (added 2026-10-28)
7. **L200–L400 concept map is proposed, not agreed.** No agreed curriculum beyond L100 exists in the KB; the map in `CONCEPTS-PRIMER.md` and every "Next: L200 …" line are proposals.
8. **Timings in concept note 5 and the primer** (SHA-256 ≈262,000 guesses/s vs Argon2id ≈11.8/s, ≈22,000×) come from one sandbox run of `research/concept_examples.py`, single core; they are indicative only and vary per machine/run.
9. **Python `os` docs** (for os.urandom/getrandom) were fetched but the page was truncated before the `os.urandom` section; not cited. OS-randomness claims rest on the `secrets` docs.
10. **New sources' licences** (WireGuard site, pip docs) not shown on fetched pages – marked unverified.
11. **`inRealSystems` one-liners** (moved from the notes' "In real systems" bullets on 2026-10-28) describe what the cited specs/docs say (TLS 1.3, WireGuard, pip, JWT/JWA, HTTP Basic); no deployed system was inspected.


## Rebalance (2026-10-28)
12. **Concept share is at the low edge of the target**: 20% (20.2%: concept 1495 / hands-on 5912 words), inside the L100 20-25% band but with little margin; adding hands-on content without touching notes will push it below 20%.
13. **tryIt timing (lesson 5, doubled memory_cost)** is noisy on the shared sandbox: x1.4-x5.4 over several runs; only the PHC prefix and True/False lines are stable.
14. **tryIt `expected` text** is the observed output, in a few cases condensed onto one line (lesson 3 item 1, lesson 4 item 2, lesson 5 items); full verbatim output is in each lab README "Try it" section.
15. **Trimmed from notes**: second worked examples (Random(42) list, 6-digit PIN 2^19.93, RFC 8439 114→130 bytes, HTTP Basic size details) and the third check-yourself question per lesson; values stay in `research/concept_examples.out.txt`.

## Environment limits
- Sandbox has no internet for pip, so `pip install -r requirements.txt` was not run; the pre-installed cryptography is exactly 50.0.2, matching the pin.
- No OpenSSL CLI and no PyNaCl locally → optional equivalents in lesson 1 were not executed.
- `sha256sum` (GNU coreutils 9.4) was available and used in lesson 2; the macOS (`shasum -a 256`) and Windows (`certutil -hashfile`) branches of `os_sha256()` are only unit-tested with recorded output layouts here.
- No simulator is needed for this domain.

## Dropped during research
| Candidate | Reason |
|---|---|
| luca-giuzzi.unibs.it copy of gcm-spec.pdf | unofficial mirror, garbled text extraction |
| riscv-crypto `aes-gcm-test.c` (raw GitHub) | fetch returned no document |
| github.com/pyca/cryptography repo page | fetch withheld by tool safety signal |
| systemslibrarian/crypto-lab-quantum-vault-kpqc test-vectors.md | unvetted personal repo |
| hsmkit.com AES test-vector guide | vendor site with product funnel (no marketing rule) |
| draft-mcgrew-gcm-test-01 | expired Internet-Draft; different (ESP) vectors |
| voltaire.tevm.sh AES-GCM vectors | library docs, used only as a secondary cross-check (score 6/12), not cited in lessons |

## Items intentionally out of scope for L100
Public-key crypto (signatures, key exchange, TLS), key management/KMS, HKDF, streaming AEAD for large files, FIPS mode, post-quantum algorithms.


## Mac mini + Windows + local agent (2026-10-28, PLATFORM-AGENT-SPEC.md)
16. **No macOS or Windows run yet.** Every lesson has `platforms: {mac: expected, windows: expected}`. The sandbox is Linux. The CI matrix (`ubuntu-latest`, `macos-latest` arm64, `windows-latest`; Python 3.12/3.13) has not run, so none of these are marked `tested-ci`.
17. **Unexecuted OS commands.** The zsh/PowerShell commands in lesson 1 (`brew`, `winget`, `py -3.12`, `Activate.ps1`, `Set-Content -NoNewline` + `Get-FileHash`, `where.exe`) were checked against docs, not run. **Updated 2026-10-28 (F06):** the third-party winget indexes (winstall, ragerworks, vmheaven, winget.tech, wingetly) were removed. `ShiningLight.OpenSSL.Light` is now backed by the fetched winget-pkgs manifest folder (3.6.0–4.1.0). Ollama on Windows now follows the shared WORKSTATION-SETUP (`OllamaSetup.exe` from ollama.com/download; winget `Ollama.Ollama` lags), and on macOS `brew install ollama` + `brew services start ollama` (formula page fetched). `Python.Python.3.12` rests on the winget-pkgs tree (shared setup page, checked in the review).
18. **OS OpenSSL facts are not from official vendor pages.** "macOS `/usr/bin/openssl` is LibreSSL" rests on the cryptography docs (Apple ships OpenSSL/LibreSSL libraries) plus one blog run (LibreSSL 3.3.6 on macOS 26.4.1). "No openssl.exe in Windows" rests on a third-party guide; no Apple or Microsoft page was found. The labs do not depend on either.
19. **`os_sha256()` tool order.** On Windows under Git Bash (as in CI), `sha256sum` from Git is found before `certutil`. In plain PowerShell, `certutil` is expected. Localised `certutil` output is handled by a 64-hex regex, but that was not tested on a non-English Windows.
20. **Agent assist runs only against the fake server.** `agent_assist.py --real` (Ollama + `qwen2.5:1.5b`) was not executed because there is no model in the sandbox, so real-model accuracy is unknown. The linter verdict does not depend on it.
21. **Agent-assist linter scope.** `misuse_lint.py` is a teaching linter with 3 rules:
   - CRY001 detects `random.<fn>` calls.
   - CRY002 detects a literal/module-level nonce passed to `.encrypt()`.
   - CRY003 detects a hashlib call whose arguments contain a name with `pass`/`pw`/`pwd`.
   It misses aliased imports (`from random import choice`), nonces reused through other data flow, and passwords under other names. For real projects use maintained tools; their names and rules were not researched here.
22. **Secret guard is heuristic.** `find_secrets()` blocks PEM private-key headers, long hex/base64 strings, base64url strings of ≥ 43 characters with mixed case and a digit (a raw 32-byte key), JWK private members (`"d"`, `"p"`, `"q"`, `"dp"`, `"dq"`, `"qi"`, `"k"`) and AWS key ids (extended for F24, with tests). It will still miss other formats (short passwords, all-lower-case base64url, keys split across lines) and may block harmless long hashes.
23. **RAM figure for the local model** (about 2 GB free while running `qwen2.5:1.5b`) is an estimate from the 986 MB download size. It was not measured.
24. **Concept share dropped to 17.7%** (concept 1500 / hands-on 6982 words; was 20%). This is below the L100 20-25% band because the platform steps and agent assist added hands-on words. Per spec, the notes were not padded; they stay at 240-248 words; note 2 gained 5 words naming the OS hash tools.

## L200 "Build it" (lessons 7-11, 2026-10-28)
25. **Concept share is 23.5%, below the L200 band of 25-30%.** Measured with the spec script: concept 2026 / hands-on 6580 words. The notes are at the 400-word cap (395-399 by `wc -w`), so they were not lengthened. Three things push hands-on up:
    - The new L200 fields `codeWalkthrough` and `buildTask`.
    - The Mac/Windows commands.
    - Lesson 9's agentAssist.
26. **No macOS or Windows run.** All five lessons have `platforms: expected`. The build-task commands use `BUILD_IMPL=… python -m unittest` on zsh and `$env:BUILD_IMPL=…` on PowerShell. Neither was run on those OSes.
27. **The CLI equivalents were not executed in the sandbox**, because age, openssl, mkcert and step are not installed.
    - `test_age_cli.py` (lesson 8) and `test_openssl_cli.py` (lesson 10) are **pending-ci**. They are skipped locally and run in CI where the tools exist: age is installed by CI on ubuntu and macOS; openssl ships on the runners.
    - The Windows `s_client` command (`$null | openssl s_client …`) is unexecuted.
    - On macOS runners `openssl` on PATH may be LibreSSL. The test checks only exit codes, but LibreSSL's `-brief` and `-verify_return_error` behaviour is unverified.
28. **Some equivalents come from general knowledge, not from a fetched page:**
    - `ssh-keygen -Y sign`
    - `openssl pkeyutl -rawin`
    - Node `crypto.sign(null, …)`
    - `nacl.public.SealedBox` and `crypto_box_seal`
    - Go `crypto/ed25519`, `crypto/x509.CreateCertificate`, `tls.Config` and `golang-jwt WithValidMethods`
    - Node `jose jwtVerify`
    - `openssl req -x509`
    - curl `--cacert`
    
    None of these was executed.
29. **The lab's hybrid format is a teaching format, not age or HPKE.**
    - Lesson 8 follows the structure of age's X25519 stanza but uses its own info label and a simple binary layout.
    - It is *not* interoperable with age and does not implement RFC 9180. No HPKE test vector was run (no HPKE in pyca 50).
    - The build-task multi-recipient format is also custom.
30. **The token lab is not a JWT library.**
    - `tokens.py` supports HS256 and EdDSA only, and has no `kid` or JWKS support.
    - It requires `exp` and does not enforce `iss`, `sub` or `typ`.
    - It is labelled "for learning only". Interoperability was checked only against PyJWT 2.15.1, for HS256 and EdDSA.
31. **PyJWT version and licence.** The pin `PyJWT==2.15.1` matches the installed package and the version in the fetched docs; the PyPI page was not fetched. The MIT licence was not shown on the fetched page.
32. **The age, mkcert and step licences** were not shown on the fetched pages. The BSD-3-Clause entries for age and mkcert are from general knowledge.
33. **TLS details depend on the OpenSSL version.**
    - The observed cipher (`TLS_AES_256_GCM_SHA384`) and verify codes 62/20 come from Python linked to OpenSSL 3.3.7.
    - Python builds on macOS (Homebrew or python.org) and on Windows link their own OpenSSL, so the cipher choice and message wording may differ. The verify codes are standard OpenSSL X509_V_ERR values.
34. **Lesson 9 agent assist was tested only against the fake server.**
    - The `[[CERT-EXPLAIN]]` rule in the vendored `fake_model_server.py` is deliberately naive. It is the second documented EXTRA_RULES entry in that copy.
    - No real model was run, so real-model accuracy is unknown.
    - The secret guard is a regex: `PRIVATE KEY`, ≥ 64 hex characters, base64/base64url key-sized strings and JWK private members (extended for F24, with tests). The report it guards is already an allow-listed summary of public certificate fields.
35. **Certificate details in the labs are teaching choices, not a vetted profile.**
    - Leaf validity is 30 days and the root 365 days. The local CA has no CRL/OCSP, no name constraints and no key protection.
    - The output of `--out pki` (lab 9) and `--serve` (lab 10) contains an unencrypted private key. It is meant for local use only.
36. **The L200 concept map in the primer replaces the earlier proposal.** HKDF, envelope encryption and key rotation, also listed in the old proposal, are only partly covered: HKDF appears inside lesson 8, and envelope encryption and rotation are left to L300. The `next` fields of the L100 lessons now name built L200 lessons (F03); the unbuilt proposals are listed under item 38.

## Learning tools + review fixes (2026-10-28, UPDATE-TOOLS-REVIEW-SPEC.md)
37. **Concept share fell again** (F09): L100 16.3% (concept 1500 / hands-on 7730), L200 21.0% (2026 / 7630), measured with the spec script. The new `learningTools` exercises add hands-on words; notes were not padded (L100 ≤ 250, L200 ≤ 400 words).
38. **L300/L400 candidates (moved from the old L100 `next` fields, F03; L200 #7-10 added in the L300 update, R3-05):** signing keys in an HSM/KMS, transparency logs and key revocation (from L200 #7); HPKE, post-quantum hybrids (X-Wing / ML-KEM) and key rotation for encrypted archives (#8); ACME issuance and CA key protection (#9); OCSP stapling, mTLS at scale and TLS 1.3 0-RTT (#10). Earlier list: hash-pinned dependencies and crypto-agility checks in CI; HKDF key derivation on its own; nonce strategies (counter vs random vs XChaCha); envelope encryption and key rotation; password-based key derivation, peppers in a secrets vault and rehash-on-login; versioned ciphertext envelopes and JWK formats.
39. **Learning-tool exercises were not run.** CyberChef, Wireshark, XCA, KeyStore Explorer, step CLI and CrypTool 2 are not installed in the sandbox. Every `expected` value is computed from the lab code (`research/learning_tools_expected.py` + `.out.txt`), and the Python side of lab 10's key log was run (`SSLKEYLOGFILE` → 8-line `keylog.txt`). Unverified details:
    - CyberChef's exact error text on a GCM tag mismatch.
    - Whether XCA's exported PEM is exactly 113 B.
    - Whether `step crypto jwt verify` accepts EdDSA with a PEM key, and the exact effect of `--subtle` (only the docs sentence "required unless disabled with the --subtle flag" was read).
    - The TLS key_share group name, which depends on the OpenSSL version (see 33).
    - Wireshark's loopback capture on Windows (Npcap) and the TLS preference field name.
40. **CrypTool 2 is Windows-only.** Lessons 4 and 8 give the Mac a "use the Windows PC" note; no macOS alternative from the catalogue is offered.
41. **F18 fixed:**
    - `hash_and_hmac.py` now runs the OS hash tool with `encoding="utf-8", errors="replace", timeout=30`. It still parses only the 64-hex line, so localised `certutil` text does not matter.
    - `test_age_cli.py` calls now carry `timeout=60`, plus explicit encoding where text is read.
    - Untested on a non-English Windows.
42. **F01 / F07 status:** the README shows "not yet run on macOS or Windows; CI matrix pending". `validation.pendingCi` lists the unrun files and variants in lessons 1, 2, 6, 8, 9 and 10. The CI workflow in `.github/` was not touched; a separate job builds the root CI.
43. **Cross-topic `seeAlso` (F08)** was added to lesson 10 (→ distributed-systems L100 #2) and lesson 11 (→ application-architecture L200 #10). Only the title of each linked lesson was read, not its content.
44. **F27:** `__pycache__` folders and the stray `.try_05-password-storage.txt` were deleted. There is no `.gitignore` in this topic; one belongs at the repository root.

## L300 "Harden it" (2026-10-28, L300-SPEC.md)
45. **Concept share is below target.** L300: concept 2765 / hands-on 12088 = 18.6% (target 30-35%), measured with the REBALANCE script on `content/L300.json`. Notes are at 533-547 words (cap 550); the failure lab, trade-offs, 7-item walkthroughs, Mac/Windows step variants and the agent-assist output add hands-on words. Notes were not padded and labs were not cut, as the spec asks.
46. **OpenBao was not run.** No container runtime in the sandbox. `openbao_transit.py` follows the 2.7.x API docs; its live test runs only in the ubuntu CI job (`docker run --network host docker.io/openbao/openbao:2.7.2 server -dev -dev-root-token-id=root`, then `bao secrets enable transit`). Unverified:
    - The image tag format `2.7.2` (no registry tag page was fetched; Docker Hub shows `latest`).
    - The JSON shape of the create-key and rotate responses (the client tolerates an empty 204 body).
    - `POST /transit/keys/:name/trim` and `min_available_version` (not used by the lab).
    - Podman on macOS/Windows with `-p 127.0.0.1:8200:8200` and `-dev-listen-address=0.0.0.0:8200` (flags from the development `server` docs, search-result text).
47. **Wycheproof vectors were vendored from mirrors, not from upstream raw files.** raw.githubusercontent.com, jsDelivr and the GitHub file pages returned no document. The 11 Ed25519 tests come from search-result text of BoringSSL's mirrors (tcIds 1-6 from the v1 `ed25519_test.json`; tcIds 10-14 from the older `eddsa_test.json`, marked `flags: ["v0"]`). The 5 AES-GCM tests come from the Wycheproof 0.4 file shipped in pycryptodome 3.7.2 (third-party mirror). Every value was checked against cryptography 50.0.2 before vendoring. The current v1 AES-GCM schema field names were not verified (the lab keeps the 0.4 names). `derived_vectors.json` is lab-made and labelled so. Running the harness on the full upstream files is pending CI/manual work. **Update (REVIEW-L300 R3-03, still open):** see item 59.
48. **minisign and cosign were not run.** minisign flags (`-G -W`, `-S -s -m`, `-V -p -m`) come from release notes; the README/docs page was blocked. The cosign `verify-blob --key ... --bundle` form is inferred from the verify docs, and whether key-only signing needs `--tlog-upload=false` in v3 is unknown, so cosign is documented as an equivalent only. `test_cli_equivalents.py` runs minisign on the macOS CI runner (Homebrew); ubuntu/Windows skip it.
49. **Timing results are machine-dependent.** The naive-loop ratio was about 2.6 here (Linux x64). Apple silicon, Windows timers and noisy CI runners will differ. The unit test only asserts ratio > 1.3 for the naive loop and makes no claim about `compare_digest`. This is a teaching demo, not a side-channel test suite (no dudect-style t-test).
50. **Certificate-lifecycle facts.** The 1-hour notBefore backdate is a teaching choice: Let's Encrypt's own backdating could only be found in a community-forum snippet, so it is not cited. Let's Encrypt's 160-hour certificate GA (Jan 2026) comes from search-result text. OCSP is explained, not implemented (Let's Encrypt planned to turn its responders off on 2025-08-06). The simulated root uses the real current time, so serials and dates change per run; the metrics are relative and deterministic.
51. **Lab file sizes (R3-10, accepted).** `envelope.py` has 127 lines (spec: about 60-120); the others are 83-116 lines. It is kept as one file because the walkthrough, `code` field and tests read it top to bottom. Moving `try_all`/`count_by_kid` into a helper would save about 15 lines but would split the story the failure lab tells.
52. **Console masking.** The sandbox console masks token-like strings (`******`) in displayed output. READMEs and `content/L300.json` were written from captured stdout, so they show the real (demo) values.
53. **`Secret` cannot erase every copy.** Python strings are immutable; the env string, decoded values and logging internals may keep copies. The lab says so and treats `wipe()` as damage reduction.
54. **Learning-tool exercises (CyberChef, step CLI, KeyStore Explorer) were not run.** Expected values come from each lab's `tool_check.py` output. How CyberChef handles an 8-byte GCM tag, and the exact `step certificate inspect` output format, are unchecked.
55. **`next` / `seeAlso`.** L200 #11 now points to L300 #12; the other L200 `next` fields keep their planned follow-up topics (some are now partly covered by L300 #12-#13). L300 `seeAlso` entries link to this topic's own lessons only; no cross-topic L300 links were agreed. Lesson 16's `next` names the planned L400 from the primer.
56. **Agent assist (lesson 16).** The third fake-server rule `[[SECRET-REVIEW]]` is naive on purpose (one false positive, two misses). The secret gate is lesson 9's regex plus this lesson's scanner; both are regex-based and can miss novel secret formats, so redaction plus gate is a backstop, not a guarantee. No real model was run.
57. **gitleaks** ~~is named as an equivalent without a version~~. Resolved in the L300 update: it is now a learning tool (v8.30.1, MIT) from the shared catalog. Its release date is "2026-03-20 (year inferred)" there.
58. **CI changed but not run.** `.github/workflows/labs.yml` gained an L300 step (same matrix), an ubuntu-only OpenBao container step and a macOS-only minisign install. It was YAML-parsed locally, not executed on GitHub. `platforms` stays `expected`.

## L300 update pass (2026-10-28, UPDATE-L300-SPEC.md, REVIEW-L300 findings)
59. **R3-03 Wycheproof provenance: not re-vendored, labelled and checked in CI instead.** The official vectors could not be fetched again on 2026-10-28. web_fetch returned no document for `raw.githubusercontent.com/C2SP/wycheproof/{main,refs/heads/main}/testvectors_v1/aes_gcm_test.json` and `ed25519_test.json`, `github.com/.../raw/...`, the `?plain=1` blob pages, the commits page, the GitHub API and jsDelivr. The GitHub file page returned only the file tree; it showed the latest commit on `aes_gcm_test.json` as "testvectors_v1: reformat JSON files". The local browser did not respond, and the sandbox has no DNS (pip/git cannot reach the network). So:
    - The 16 cases and their values are unchanged.
    - `vectors/NOTICE.md` and the lab README now name the exact downstream copy each case came from and say plainly that none came from upstream.
    - Mirror URLs were removed from lesson 15's `sources` and from the VERIFIED-RESOURCES table (they are recorded only as provenance).
    - `upstream_diff.py` (+ `test_upstream_diff.py`, offline) finds every case by content in an upstream `testvectors_v1/` folder.
    - The new CI job `wycheproof-upstream` clones C2SP/wycheproof `main`, prints the commit and date, and fails on any miss.

    Still open:
    - The first CI run has not happened.
    - The v0 Ed25519 cases (tcId 10-14) may be renumbered or absent in `testvectors_v1/ed25519_test.json`.
    - The v1 AES-GCM field names are assumed equal to the 0.4 names. A key error in that job would show they are not.
60. **R3-04 / R3-05 links.** Lesson 16 now links to ai-agents L300 #16 (Red-teaming prompt injection); the back-link belongs to the ai-agents topic. L200 #7-10 `next` now name built L300 lessons (#14, #12, #13, #13); the unbuilt parts moved to item 38.
61. **R3-13 vendor sources.** Google Cloud KMS (×2), AWS KMS and Docker secrets are no longer lesson sources. Lesson 12 relies on the OpenBao transit docs (rotate, rewrap, working set / `min_decryption_version`, NIST rotation guidance; re-read 2026-10-28) and NIST SP 800-57 Pt 1 Rev 5 (landing page re-read). The vendor pages remain as one-line equivalents. Lesson 16's `/run/secrets/<name>` fact is now carried by the Kubernetes docs plus a one-line Docker equivalent.
62. **R3-14 concept share** is reported for all levels in `documentation/README.md` (L100 16.3%, L200 20.9%, L300 17.8%, topic 18.3%; below 30-35%; notes at their caps, not padded).
63. **New learning tools were not run** (OpenBao web UI/CLI, minisign, Gitleaks). Their expected values are the lab README's own verdicts. Unverified details:
    - the OpenBao UI path and whether the Homebrew build ships the UI;
    - whether `bao read transit/keys/<name>` output shows `latest_version` with that exact label in 2.7.2;
    - whether Gitleaks' default rules flag the low-entropy demo values.

    Lesson 14's `tool_check.py` gained `--out DIR`, so learners get a real MANIFEST.json to sign; it ran here. The lab step for the minisign equivalence test still shows `winget install -e --id jedisct1.minisign` (winget-pkgs manifest 0.12, VERIFIED-RESOURCES). The learning-tool entry uses the catalog's Win64-zip instruction.
64. **R3-06 checked, no change needed.** All five L300 build-task tests take `BUILD_IMPL=<lab module>`, and each shipped lab file is the unfixed version (re-run: fails before, passes on the solution).

## L400 "Design it" + capstone (2026-10-28, L400-SPEC.md)
65. **Concept share is below target.** L400 + capstone: concept 4283 / hands-on 19506 = 18.0% (target 35-40%), measured with the REBALANCE script on `content/L400.json`. The notes are full length (728-750 words; capstone 545). The new design fields (brief, options with evidence, ADR, fitness function, scaling limits), the capstone's milestones and rubric, and the Mac/Windows step variants add hands-on words. Nothing was padded or cut. All levels: L100 16.3%, L200 20.7%, L300 17.7%, L400 18.0%, topic 18.1%.
66. **The quantum-computing L400 #21 cross-link has no confirmed title.** When this was written, `quantum-computing/content/` had no `L400.json`, so lesson 18's `seeAlso` names "quantum-computing L400 #21" with a description of the expected subject (the quantum side of harvest-now-decrypt-later: resource estimates for Shor). That description is a placeholder. Sync the exact title once the quantum L400 lands. The link is one-way, which the spec allows for cross-topic links.
67. **Post-quantum: what was and was not run.**
    - **Run:** cryptography 50.0.2's ML-KEM-768/1024, ML-DSA-44/65/87, ML-DSA X.509 certificates and HPKE `MLKEM768_X25519`, all for real.
    - **Not run:**
      - liboqs-python 0.16.0.1, so the interop check (`oqs_crosscheck.py`, written from the README's `KeyEncapsulation` / `encap_secret` / `decap_secret` / `details` API) runs only in the CI job `l400-equivalents`.
      - oqs-provider. It is named as an equivalent only, because on OpenSSL ≥ 3.5 it disables the algorithms the lab uses.
      - A real TLS X25519MLKEM768 handshake. The sandbox's stdlib `ssl` links OpenSSL 3.3.7, and Python 3.12 lacks `SSLSocket.group()` (added in 3.15). The `pq-tls-probe` job tries Python 3.15 on all three OSes; whether the runners' Python 3.15 links OpenSSL ≥ 3.5 is unverified, and if not the test skips and says why.
    - **Not verified:** that OpenSSL 3.5 puts X25519MLKEM768 in its default TLS groups.
    - **Not used in the lab:** NIST IR 8547's deprecation and disallow dates. Only the landing pages (draft 2024-11-12, final 2026-10-27) were read.
68. **PKCS#11 / SoftHSM2.**
    - `pkcs11_softhsm.py` was written from the python-pkcs11 0.10.1 PyPI README and not run. These calls are unverified: `generate_keypair(store=False, private_template=…)`, `pkcs11.util.ec.encode_ec_public_key` / `encode_ecdsa_signature`, and `pkcs11.exceptions.AttributeSensitive`.
    - The CI token setup (`SOFTHSM2_CONF` in `$RUNNER_TEMP`, `--free`) follows the SoftHSM README, and the module path is searched in two Debian locations.
    - The PKCS#11 v3.1 HTML was read only up to the normative references, so the CKA_SENSITIVE / CKA_EXTRACTABLE / ALWAYS / NEVER semantics in the lab follow the private-key attribute table as commonly documented. Re-check them against §4.9 when the full text is available.
    - SoftHSM2 on Windows was not verified; the lesson says to use WSL2.
    - The software token is a teaching model with no memory protection.
69. **OpenMLS was not run.** The `openmls-equivalent` CI job runs `cargo test -p openmls remove` on upstream main. The test filter is a guess (any test whose name contains "remove"), and the job can take many minutes. The toy tree deliberately omits signatures, credentials, tree hashes, Welcome and the secret tree; its heap-order layout differs from RFC 9420 Appendix C, but the relations are the same.
70. **Threat-model sources.** The STRIDE-per-element applicability table (external S,R; process STRIDE; store and flow T,I,D) is the commonly taught chart. Its original source (Shostack, *Threat Modeling*, or Microsoft SDL material) was not fetched, and the OWASP cheat sheet gives STRIDE and the violated properties but not the per-element chart. Attack-tree costs use the lab's own 1-10 scale. NIST CSWP 39 (final) was withdrawn on 2026-06-29 and superseded by CSWP 39upd1, which was not fetched.
71. **Capstone simplifications.**
    - The KMS is an in-process thread holding KEKs in memory (threat T7, accepted; production would be OpenBao transit or an HSM).
    - The token is the lesson 19 software token, so the signature phase is `classic` (Ed25519 only). ML-DSA in the token waits for SoftHSM2's ML-DSA support, which was added on main after 2.7.0 and is unverified.
    - The ACL cache (300 s) is a deliberate weakness that the audit rules detect.
    - Audit-log truncation at the tail is not detectable by the chain alone (ADR-0022-3).
    - User-facing TLS is out of scope (T3, accepted).
72. **Slow tests on the sandbox mount.** Lesson 21's fitness test (12 control tests in subprocesses) took about 100-180 s, and the 19 capstone tests about 100 s, while using only a few seconds of CPU. File-system latency dominated. On this mount, `TemporaryDirectory` cleanup sometimes failed ("Directory not empty"), so the labs use `ignore_cleanup_errors=True` and create their temporary folders inside the lab folder (never `/tmp`). Leftover `tmp*` folders are safe to delete.
73. **Learning-tool exercises (L400) were not run.**
    - CyberChef: lessons 17 and 20. It is unverified whether CyberChef's HKDF operation takes these exact parameters.
    - Wireshark: lessons 18, 21 and the capstone. Needs an OpenSSL 3.5+ CLI for lesson 18; a Windows OpenSSL 3.5 install is not covered.
    - OpenBao: lesson 19 and the capstone. The CLI error text for a refused export is unchecked.
    - step CLI: capstone.

    Each exercise's expected value is the lab's own printed output.
74. **L400 candidates for further study** (from the old primer line and items 38/55):
    - protocol review of Noise and TLS 1.3 transcripts;
    - fuzzing parsers (envelope, audit log) with Atheris;
    - FIPS 140-3 module boundaries;
    - composite ML-DSA certificates once the LAMPS draft is an RFC;
    - SLH-DSA for firmware signing;
    - HPKE-based MLS ciphersuites with ML-KEM (OpenMLS has added hybrid ciphersuites);
    - transparency logs for audit-log anchoring;
    - ACME issuance with an HSM-held CA key;
    - OCSP stapling and mTLS at scale;
    - TLS 1.3 0-RTT.

## L500 "Theory & Rigour" (lessons 23-27), 2026-10-30
75. **Abstract-only standards.** For ISO/IEC 29147:2018 (paywalled) and FIPS 203, only the landing pages and abstracts were fetched in this pass. The ML-KEM modulus q = 3329 used in lesson 25 is the FIPS 203 parameter but was not re-read from the PDF here. The NIST SP 800-38D §8.3 2^32 random-IV limit is cited as in L100 #4 and was not re-fetched.
76. **OIG report PDF.** `https://oig.justice.gov/reports/2018/o1803.pdf` returned no content through the fetch tool. Lesson 26 relies on the OIG landing page and the official press release (both fetched). Mirror copies seen in search (e.g. courthousenews, theblackvault) were not used as sources.
77. **No "professor's pedagogy review" file in the workspace.** L500-SPEC refers to a 14-week plan "from the review". No such document was found under `working/`, so `content/assessment/syllabus.md` builds the 14-week plan from the spec's assessment weights and the L100-L500 lesson map. Adjust it if the review turns up.
78. **ABET outcomes.** The syllabus maps to the Engineering Accreditation Commission's Criterion 3 outcomes (1)-(7) (2025-2026 criteria, verified). Computing programmes accredited by ABET's Computing Accreditation Commission use a different list, which was not fetched; that mapping is left to the adopting programme.
79. **Proof sketches.** T25.3 (Encrypt-then-MAC) is a reduction sketch; the full treatment is Bellare-Namprempre. T25.4 cites Shoup (1997) for the generic lower bound and Regev for LWE hardness without reproducing those proofs. The numerical checks confirm instances only; the proofs carry the general claims.
80. **Determinism of checks.** All theorem-check outputs are deterministic (seeded test inputs; only invariant facts printed). The one probabilistic line, "0 collisions among 2^20 os.urandom(12) nonces", fails with probability about 2^-57. pyca-generated keys vary per run, but only invariant properties are printed.
81. **Primary-source numbers.** Shannon prints H(K) = log₁₀ 26! as "about 20". The true value is 26.6 (problem 27-P3), and the lesson treats this as a critical-reading exercise. The OCR of the fetched copy is imperfect, so quotes were checked against the abstract and summary only.
82. **Platforms.** The L500 labs ran on Linux only (Python 3.12, cryptography 50.0.2). macOS/Windows status is "expected" until the CI L500 step runs. The labs use no OS-specific calls and print ASCII only.
83. **Concept share.** L500 is deliberately theory-heavy: 4,665 words of concept notes plus proofs in the JSON. It is outside the REBALANCE-SPEC targets by design (L500-SPEC sets its own note lengths).

## Found while writing the explanations (Nov 2026)
- **L400 #19:** KMS-style remote signing took 587.5 µs here against ~5,001.5 µs in the README/ADR-0019, inside the 1 ms limit. The ADR's latency argument against that option is weaker than written; re-measure before relying on it.
- **L500 #25:** problem 25-P8 quoted 147/1000 toy-Regev errors; the check output shows 122/1000. Fixed in the lesson and concept note.
