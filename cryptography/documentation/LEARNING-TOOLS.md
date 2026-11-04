# Learning tools – Applied Cryptography

Open-source tools to **see**, **prototype** or **check** what the labs do. Facts come from `../../shared/LEARNING-TOOLS-CATALOG.md`
(checked 2026-10-28, with source URLs); no cross-cutting tool maps to this topic. Lessons 1 and 3 have none.

| Tool | Role | Licence (OSI) | Mac mini install | Windows install | Lessons |
|---|---|---|---|---|---|
| CyberChef | CHECK / SEE | Apache-2.0 (yes) | Browser, or the offline release zip (github.com/gchq/CyberChef/releases); Docker `ghcr.io/gchq/cyberchef` | Browser or offline zip (runs fully client-side) | 2, 4, 5, 6, 11, 12, 14, 15, 16, 17, 20 |
| Wireshark | INSPECT | GPL-2.0 (yes) | `brew install --cask wireshark-app` or the official universal .dmg | Official x64/Arm64 installer (bundles Npcap) | 10, 8, 18, 21, 22 |
| XCA | BUILD WITHOUT CODE / INSPECT | BSD-3-Clause (yes) | `brew install --cask xca` | `xca-2.9.0-win64.msi`, portable zip, or Microsoft Store 9N9K02V7XR1B | 9, 7 |
| KeyStore Explorer | INSPECT | GPL-3.0 (yes) | `brew install --cask keystore-explorer` (or kse-570-arm64.dmg) | `winget install -e --id KaiKramer.KeyStoreExplorer` (or kse-570-setup.exe) | 9, 13 |
| step CLI (smallstep) | CHECK | Apache-2.0 (yes) | `brew install step` | `winget install -e --id Smallstep.step` (manifest at 0.30.6) or `step_windows_0.31.0_amd64.zip` | 11, 13, 22 |
| CrypTool 2 | SEE | Apache-2.0 (yes) | not available (Windows/.NET only) | EXE installer or ZIP from cryptool.org (no admin) | 4, 8 |
| OpenBao (transit engine + web UI) | SEE / CHECK | MPL-2.0 (yes) | `brew install openbao`, or the lab's container `docker.io/openbao/openbao:2.7.2 server -dev` | partial: container (Docker Desktop / Podman); native binary not checked | 12, 19, 22 |
| minisign | CHECK | ISC (yes) | `brew install minisign` | Win64 zip from the GitHub releases | 14 |
| Gitleaks | CHECK | MIT (yes) | `brew install gitleaks` | `gitleaks_8.30.1_windows_x64.zip` / `windows_arm64.zip` from the GitHub releases | 16 |

Exercises are in each lesson's `learningTools` field (max 2; capstone 3). L300: unwrap a demo DEK (12), inspect a 160-hour certificate (13), hash a release artifact (14), open a Wycheproof vector (15), decode a base64 "secret" (16); OpenBao, minisign and Gitleaks mirror labs 12, 14, 16. L400: decrypt an agile envelope (17), recompute an epoch key with HKDF (20), see the X25519MLKEM768 key share (18; OpenSSL 3.5+), prove a flow is encrypted (21) and the KMS asks for a client certificate (22), sign through a transit key with no export (19), rotate and rewrap a DEK (22), inspect the mTLS certificate (22). Their `expected` values are the lab's own printed output
(L100-L300 recomputed by `research/learning_tools_expected.py`, L400 from `tool_check.py` or the lab run). The tools were not run
in the sandbox: each exercise is pending a manual run.

## How to use these tools
They complement the code labs: you still write and run the Python. Use a tool to **see** the idea, **build without code** (an XCA chain next to `local_ca.py`), or **check** your result (CyberChef or
`step` must give the same digest, plaintext or claims). A mismatch means different input bytes (often a newline), parameters
or keys. Use demo keys only, never real secrets, and delete Wireshark key-log files after use.

## Not recommended / changed
- **jwt.io debugger**: proprietary (Okta/Auth0). Use CyberChef JWT Decode / JWT Verify instead; it runs client-side.
- **mkcert**: stale (last release 2022) and hides the CA-building lesson 9 teaches; kept only as an equivalent.
- **JCrypTool**: unmaintained since Sep 2023. **CrypTool-Online**: licence unverifiable; use CrypTool 2.
- **XCA**: last release 2.9.0 (2025-03-28), maintenance borderline.
- **TruffleHog** (AGPL-3.0): overlaps Gitleaks for lesson 16, and its verification step logs in to third-party services with the secrets it finds.
- **Sigstore cosign**: overlaps minisign for lesson 14 and by default records signatures in the public Rekor log; kept as an equivalent in the lab only. **Rekor Search UI**: searches that public log; the labs never upload.
