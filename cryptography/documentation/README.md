# Applied Cryptography – L100 + L200 + L300 + L400 + capstone + L500 theory

**Status: not yet run on macOS or Windows; CI matrix pending.**

**Start here.** This domain teaches software engineers to *use* vetted cryptography correctly. L100 covers hashing, MACs, randomness, authenticated encryption, password storage, and telling encoding / hashing / encryption apart. L200 covers signatures, public-key encryption, a local CA, TLS and tokens. L300 hardens it: key rotation, certificate renewal, release signing, misuse tests and secrets in applications. L400 designs with it: crypto agility, post-quantum hybrids, keys in hardware-style storage, group end-to-end encryption and threat models as code, and the capstone builds an encrypted document service from all of it. L100-L400 keep theory to what you need to run the code. **L500 "Theory & Rigour"** (lessons 23-27) adds the undergraduate foundations: number theory, probability and security definitions, each with proofs and code checks, plus an ethics lesson and a primary-literature seminar. A course assessment pack sits in `content/assessment/`. No home-made crypto, except textbook RSA/DH toys in L500 that are clearly labelled insecure.

- Main toolchain: Python 3.12 (3.9+ works) + **pyca/cryptography 50.0.2** (Apache-2.0 OR BSD-3-Clause) + stdlib `hashlib`, `hmac`, `secrets`, `base64`.
- Equivalents in every lesson: libsodium/PyNaCl, OpenSSL CLI, Node.js `node:crypto`, Go `crypto/*`, Java JCA.
- Target machines: Apple-silicon Mac mini (macOS) and Windows 11 PC; no special hardware or simulator is needed (see `documentation/HARDWARE.md`). Each lesson has a `platforms` field (`expected` until the macOS/Windows CI jobs pass).
- Agent assist (lessons 6, 9, 16, 21 and the capstone): a local model (Ollama, OpenAI-compatible endpoint from `LOCAL_MODEL_URL`, model from `LOCAL_MODEL`) reviews code for crypto misuse (lesson 6), explains a certificate-validation failure (lesson 9) reviews a redacted log for leaked secrets (lesson 16), proposes threats that a checker classifies (lesson 21) or explains audit anomalies that rules found (capstone). In every case, deterministic code is the judge. Default runs use a deterministic fake server, so no model is needed.

## L100 lesson map ("Run it")

Tools column: open-source learning tools for the lesson (`learningTools` field); see `documentation/LEARNING-TOOLS.md`.

| # | Level | Lesson | Lab folder | Status | Tools |
|---|---|---|---|---|---|
| 1 | Setup | Set up your crypto workbench | `labs/L100/01-setup-workbench` | validated-local (+ pendingCi) | – |
| 2 | L100 | Hashing and integrity: SHA-256 and HMAC | `labs/L100/02-hashing-integrity` | validated-local (+ pendingCi) | CyberChef |
| 3 | L100 | Secure randomness: secrets vs random | `labs/L100/03-secure-randomness` | validated-local | – |
| 4 | L100 | Authenticated encryption: AES-256-GCM and ChaCha20-Poly1305 | `labs/L100/04-authenticated-encryption` | validated-local | CyberChef, CrypTool 2 (Windows) |
| 5 | L100 | Password storage: Argon2id (and scrypt fallback) | `labs/L100/05-password-storage` | validated-local | CyberChef |
| 6 | L100 | Encoding vs hashing vs encryption | `labs/L100/06-encoding-hashing-encryption` | validated-local (+ pendingCi) | CyberChef |

**Validation key.** `validated-local` = the lab script, tests and tryIt ran in the Linux sandbox and the README shows that output.
`validation.pendingCi` (shown here as "+ pendingCi") lists the files or variants that have **not** run yet: OS-specific branches, optional CLI tests, `--real` model runs.
`platforms` stays `expected` until the macOS/Windows CI jobs pass. Learning-tool exercises are manual and marked "pending a manual run".

Full lesson content (steps, glossary, equivalents, sources): `content/L100.json`.

## L200 lesson map ("Build it")

Each lab starts from working code. You **extend** it with one small feature (`buildTask`), and `test_build_task.py` proves it works. Each lab folder has a reference `solution_*.py`. By default the test checks the solution; set `BUILD_IMPL` to check your own file (the command is in each README). There are 400-word notes in `content/concepts/L200/`, and each lesson has a `codeWalkthrough`. No new setup is needed. The only optional extra is `python -m pip install -r requirements-L200.txt` (adds PyJWT 2.15.1 for lesson 11's equivalence test).

| # | Lesson | Lab folder | You build | Status | Tools |
|---|---|---|---|---|---|
| 7 | Digital signatures with Ed25519 | `labs/L200/07-ed25519-signatures` | keyring verify (key rotation) | validated-local | XCA |
| 8 | Key exchange and hybrid encryption (X25519 + HKDF + AEAD) | `labs/L200/08-hybrid-encryption` | multi-recipient (age-style file key) | validated-local (+ pendingCi: age CLI test) | Wireshark, CrypTool 2 (Windows) |
| 9 | A local certificate authority (+ agent assist) | `labs/L200/09-local-ca` | intermediate CA | validated-local (+ pendingCi: `--real` model) | XCA, KeyStore Explorer |
| 10 | TLS on localhost | `labs/L200/10-tls-localhost` | mutual TLS | validated-local (+ pendingCi: openssl s_client test) | Wireshark (SSLKEYLOGFILE) |
| 11 | Tokens done right (learning code, not for production) | `labs/L200/11-tokens` | jti replay guard | validated-local (incl. PyJWT 2.15.1) | CyberChef, step CLI |

Cross-topic links (`seeAlso`): lesson 10 ↔ distributed-systems L100 #2 (Two services talking over HTTP); lesson 11 ↔ application-architecture L200 #10 (OpenID Connect + PKCE). Every L100 `next` names a real L200 lesson. Every L200 `next` names a built L300 lesson: 7 → #14, 8 and 11 → #12, 9 and 10 → #13. The unbuilt follow-ups are L400 candidates (KNOWN-GAPS 38). L300 lessons cite their own L100/L200 prerequisites in `seeAlso`; lesson 16 also links to ai-agents L300 #16 (Red-teaming prompt injection).

Full lesson content: `content/L200.json`. Lab 10 imports lab 9's `local_ca.py`, so do lesson 9 first.

## L300 lesson map ("Harden it")

Each lab starts from code that **works** on the happy path, then a seeded, deterministic fault makes it fail (`failureLab`: fault, symptom, fix, proof). The fix is the `buildTask`; `test_build_task.py` fails against the unfixed lab file and passes against the reference solution (README shows both runs). Notes of 450-550 words are in `content/concepts/L300/`; each lesson adds `tradeOffs` and a 7-item `codeWalkthrough`. No new packages: stdlib + `cryptography==50.0.2`. Lessons 12, 13 and 16 emit JSON-line logs/metrics you read to diagnose.

| # | Lesson | Lab folder | Fault → hardening | Status | Tools |
|---|---|---|---|---|---|
| 12 | Envelope encryption and key rotation | `labs/L300/12-envelope-rotation` | rewrap job crashes, old KEK deleted → retire-after-rewrap | validated-local (+ pendingCi: OpenBao transit container) | CyberChef, OpenBao |
| 13 | Certificate lifecycle: short-lived certs, renewal and revocation | `labs/L300/13-cert-lifecycle` | expired cert still served → jittered renewal loop + expiry alert | validated-local | step CLI, KeyStore Explorer |
| 14 | Signing the software supply chain | `labs/L300/14-supply-chain-signing` | swapped/extra files with a valid manifest signature → strict install | validated-local (+ pendingCi: minisign test) | CyberChef, minisign |
| 15 | Misuse you can test: Wycheproof vectors, timing and nonce reuse | `labs/L300/15-testable-misuse` | wrapper accepts truncated tags / non-canonical signatures → strict checks | validated-local (+ pendingCi: upstream provenance diff, full upstream vectors) | CyberChef |
| 16 | Secrets handling in applications (+ agent assist) | `labs/L300/16-secrets-handling` | secret in a JSON log line → redaction filter + log-scanning test | validated-local (+ pendingCi: `--real` model) | CyberChef, Gitleaks |

Full lesson content: `content/L300.json`. Lesson 13 imports lab 9's `local_ca.py`; lesson 16's agent assist reuses lesson 9's secret gate. Lesson 15 vendors 16 Project Wycheproof cases under Apache-2.0. They were copied from downstream copies, not from upstream C2SP, and `upstream_diff.py` plus a CI job check them against upstream (`vectors/NOTICE.md`, KNOWN-GAPS 47). Lesson 16's `next` names L400 #17.

**Hands-on leads, concepts are short:** read `documentation/CONCEPTS-PRIMER.md` once, then the lesson's 200-250-word concept note in `content/concepts/` (`conceptNote` field; each "How it works" point names the lab step that shows it) and run the lab. Lab code comments name the concept at the line where it happens. After the lab, run the two `tryIt` experiments (`python try_it.py`, predict first) and answer `checkYourself` with the checkpoint. `inRealSystems`, `useWhen` and `next` (the L200 topic) are one-liners in each lesson object.

## L400 lesson map ("Design it") and capstone

Each lesson poses a design brief with measurable constraints, compares 2-3 options with evidence the lab generates (`measure_options.py`, `pq_measure.py`, `key_storage_options.py`, `compare_designs.py`, the threat model), records the decision as a Nygard ADR in the lab folder, and keeps it true with a fitness function. The seeded failure lab is the build task: the shipped file is unfixed, and `BUILD_TARGET=mine python -m unittest -v test_build_task` checks your own file (`BUILD_IMPL=<module>` still works). Notes are 600-750 words in `content/concepts/L400/`. New in the JSON: `designBrief`, `options`, `decisionRecord`, `fitnessFunction`, `scalingLimits`. No new packages are needed: cryptography 50.0.2 already ships ML-KEM, ML-DSA and HPKE `MLKEM768_X25519`. liboqs-python, SoftHSM2/python-pkcs11, a Python 3.15 TLS probe and OpenMLS are equivalents that run in CI only (`requirements-L400-ci.txt`).

| # | Lesson | Lab folder | Decision (ADR) | Fitness function | Status | Tools |
|---|---|---|---|---|---|---|
| 17 | Crypto agility: versioned envelopes, negotiation and dual signing | `labs/L400/17-crypto-agility` | per-algorithm ids + registry + policy phases | `agility_lint` (0 hard-coded algorithms) | validated-local | CyberChef |
| 18 | Post-quantum cryptography in practice: ML-KEM, ML-DSA and hybrids | `labs/L400/18-post-quantum` | strict X25519MLKEM768, no fallback | PQ policy (PQ-safe, ≤ 2,400 B, no fallback) | validated-local (+ pendingCi: liboqs, TLS group probe) | Wireshark |
| 19 | Keys in hardware-style storage: PKCS#11, non-exportable keys and key ceremonies | `labs/L400/19-hsm-pkcs11` | non-exportable token keys, sign via handles | no key export (static + inventory) | validated-local (+ pendingCi: SoftHSM2) | OpenBao |
| 20 | End-to-end encryption for groups: pairwise, sender keys and MLS-style epochs | `labs/L400/20-group-e2ee` | MLS-style tree, removal blanks the path | seeded membership sequence (0 leaks, ≤ 2·log2 n) | validated-local (+ pendingCi: OpenMLS) | CyberChef |
| 21 | Threat modelling cryptographic systems: STRIDE, attack trees and tests (+ agent assist) | `labs/L400/21-threat-model` | threat model as code, controls proven by tests | 0 checker problems, 12/12 control tests pass | validated-local (+ pendingCi: `--real` model) | Wireshark |
| 22 | Capstone: an encrypted document service (+ agent assist) | `labs/L400/22-capstone` | 4 ADRs (KMS behind mTLS, envelope reuse, signed audit chain, PQ sharing) | lint, key export, threat model, secrets in logs, scorecard 6/6 | validated-local (+ pendingCi: OpenBao/HSM-backed KMS, `--real`) | Wireshark, OpenBao, step CLI |

`python run_capstone.py` prints one JSON line per milestone (M1-M6) and `{"scorecard": "capstone", "passed": 6, "total": 6, "decided_by": "code"}`. The capstone imports lessons 9, 10, 12, 16, 17, 18, 19 and 21 rather than copying them (`paths.py`). Its architecture is in `architecture.mmd`. Lesson 18 links to quantum-computing L400 #21 (see KNOWN-GAPS 66). Lesson 21's fitness test and the capstone tests are slow on network mounts (minutes), but use only a few seconds of CPU.

Full lesson content: `content/L400.json`.

## L500 lesson map ("Theory & Rigour") and assessment pack
Each theory lesson goes definitions → theorems with proofs → a numerical check that runs here (`theorem_checks.py`, output stored verbatim in `content/L500.json` `checkOutput`) → a problem set with worked solutions and a rubric. Lessons 26-27 have no code. Concept notes (`content/concepts/L500/`) are 712-1049 words.

| # | Title | Lab / material | Theorems (proved + checked) | Problems | Status |
|---|---|---|---|---|---|
| 23 | Foundations I: number theory for public-key cryptography | `labs/L500/23-number-theory` (textbook RSA/DH toys, **insecure**) | Bézout/extended Euclid; Euler (Fermat); CRT; RSA correctness | 8 | validated-local |
| 24 | Foundations II: probability for cryptography | `labs/L500/24-probability` | birthday upper bound; lower bound + 50 % threshold; 96-bit nonce budget; entropy inequalities + negligible functions | 9 | validated-local |
| 25 | Foundations III: security definitions, games and reductions | `labs/L500/25-security-definitions` | OTP perfect secrecy + key bound; deterministic ⇒ not IND-CPA; Encrypt-then-MAC reduction; BSGS O(√q) + LWE intuition | 8 | validated-local |
| 26 | Ethics: encryption, lawful access and responsible disclosure | case study Apple-FBI 2016; ACM/IEEE codes; ISO/IEC 29147; CERT CVD; EAR 740.17 / Wassenaar | - | 6 | sources verified |
| 27 | Reading seminar: Diffie & Hellman (1976) and Shannon (1949) | 2 readings × 5 guiding questions + critical response | - | 6 | URLs verified |

Assessment pack (`content/assessment/`):
- `syllabus.md`: 14-week plan, weights, policies, CS2023 and ABET mapping.
- `midterm.md` and `final.md`, with model answers.
- `concept-inventory.json`: 15 pre/post misconception items.
- `capstone-oral-defence.md`, `peer-review-adr.md` and `team-roles.md`.

Question bank: `content/qbank/L500.json` has 45 MCQs (9 per lesson).

Validate with:
- `python research/l500_checks.py`: theorem outputs and problem answers;
- `python research/check_l500_qbank.py`: the qbank rules for L500 (`tools/check_qbank.py` reads L100-L400 only);
- `python research/qbank_checks.py`: every calculation and output answer, L100-L500.

Rebuild the JSON from `research/l500_data_*.py` with `python research/build_l500.py`, and the bank with `python research/build_l500_qbank.py`.

## How to run the labs
Full workstation setup (both machines, incl. Ollama): `../../shared/WORKSTATION-SETUP.md`.

macOS (zsh):
```zsh
cd cryptography                       # this domain folder
brew install python@3.12
python3.12 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt       # cryptography==50.0.2 (bundles its own OpenSSL)
cd labs/L100/01-setup-workbench
python sanity_check.py                # each lab: run the script ...
python -m unittest -v                 # ... then its tests
python try_it.py                      # ... then the two tryIt experiments
```
Windows 11 (PowerShell):
```powershell
cd cryptography
winget install -e --id Python.Python.3.12
py -3.12 -m venv .venv; .venv\Scripts\Activate.ps1    # blocked? Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
$env:PYTHONUTF8 = "1"                                  # UTF-8 output for the labs
python -m pip install -r requirements.txt
cd labs\L100\01-setup-workbench
python sanity_check.py; python -m unittest -v; python try_it.py
```
The lab commands after setup are identical on both OSes (lab code uses `pathlib`, `tempfile`, explicit UTF-8, `127.0.0.1` only). OpenSSL CLI availability differs (macOS: LibreSSL at `/usr/bin/openssl`; Windows: none built in); the labs do not need it, see lesson 1.
Each lab README shows the exact command and the output observed when it was validated.

Every lab checks itself against official test vectors where one exists: NIST SHA-256 example, RFC 4231 (HMAC), RFC 8439 §2.8.2 (ChaCha20-Poly1305), GCM spec test case 14 (AES-256-GCM), RFC 9106 §5.3 (Argon2id), RFC 7914 §12 (scrypt), RFC 4648 §10 (base64/base16). L200 adds RFC 8032 §7.1 TEST 1 (Ed25519) and RFC 7748 §6.1 (X25519).

## CI
`.github/workflows/labs.yml` installs the pinned requirements and runs every lab script and unittest suite on `ubuntu-latest`, `macos-latest` (Apple silicon, arm64) and `windows-latest` (Python 3.12 and 3.13, `shell: bash`), plus the vendored local-agent helper tests (fake model server only). An L200 job runs the same loop over `labs/L200` after installing `requirements-L200.txt`, and also installs the `age` CLI on ubuntu and macOS. On runners with an `openssl` binary, `test_openssl_cli.py` runs as well. An L300 step runs every `labs/L300` lab the same way; on ubuntu it first starts an OpenBao 2.7.2 dev container (transit enabled) for lesson 12's live test, and on macOS it installs minisign for lesson 14. A separate ubuntu job, `wycheproof-upstream`, shallow-clones C2SP/wycheproof and runs lesson 15's `upstream_diff.py`. It fails if any vendored case is not found verbatim upstream, and it logs the upstream commit and date. An L400 step runs every `labs/L400` lab (scripts, unittests, fitness functions) and also asserts that each `test_build_task.py` FAILS with `BUILD_TARGET=mine` (the shipped file is unfixed). Three extra jobs cover what the sandbox cannot run: `l400-equivalents` (ubuntu: SoftHSM2 + python-pkcs11 for lesson 19, liboqs-python interop for lesson 18, from `requirements-L400-ci.txt`), `pq-tls-probe` (Python 3.15 on all three OSes; it reports the negotiated TLS group, or skips if the runner's Python links OpenSSL < 3.5) and `openmls-equivalent` (ubuntu: OpenMLS's remove tests, the production equivalent of lesson 20). GitHub only reads workflows from the repository root `.github/`; if this folder is not the repo root, move the file there and set `DOMAIN_DIR`. An L500 step runs the three theory labs (scripts and unittests) and then `research/l500_checks.py`, `research/check_l500_qbank.py` and `research/qbank_checks.py` on all three OSes.

## Safety rule used throughout
Don't invent your own crypto. Use vetted libraries and their high-level APIs; never reuse an AEAD nonce; never store passwords with fast hashes or reversible encryption.

## Other files
- `documentation/HARDWARE.md` – what runs on the Mac mini vs the Windows PC, RAM/disk, GPU notes.
- `documentation/LEARNING-TOOLS.md` – CyberChef, Wireshark, XCA, KeyStore Explorer, step CLI, CrypTool 2, OpenBao, minisign, Gitleaks: role, licence, installs, lessons.
- `documentation/VERIFIED-RESOURCES.md` – sources kept, with licence and score.
- `labs/_shared/local_agent/` – vendored local-agent helper (`client.py`, `fake_model_server.py` with three documented rules: `[[CRYPTO-REVIEW]]` for L100, `[[CERT-EXPLAIN]]` for L200, `[[SECRET-REVIEW]]` for L300).
- `documentation/KNOWN-GAPS.md` – what is unverified or was dropped.
- `research/L100-evidence.md`, `research/L200-evidence.md`, `research/L300-evidence.md`, `research/L400-evidence.md`, `research/L500-evidence.md` – research questions, sources considered, key facts.
- `research/concept_examples.py`, `research/l200_concept_examples.py` and `research/l300_concept_examples.py` (+ `.out.txt`) – compute every number used in the concept notes.
- `research/learning_tools_expected.py` (+ `.out.txt`) – computes the `expected` values of the learning-tool exercises from the lab code.
- Concept share (spec measure script): after rebalance 2026-10-28 concept 1495 / hands-on 5912 words = 20% (was 46%); after the platform + agent-assist pass concept 1500 / hands-on 6982 = 17.7% (below the 20-25% band because hands-on content grew; notes not padded).
- L200 concept share (same script on `content/L200.json`): concept 2026 / hands-on 6580 words = 23.5%. This is below the 25-30% band, because the notes are at the 400-word cap and the new codeWalkthrough, buildTask, Mac/Windows and agent-assist content add hands-on words (KNOWN-GAPS 25).
- After the learning-tools + review pass (2026-10-28): L100 concept 1500 / hands-on 7730 = 16.3%; L200 concept 2026 / hands-on 7630 = 21.0%. The `learningTools` exercises add hands-on words; notes were not padded (KNOWN-GAPS 37).
- L300 (same script on `content/L300.json`): concept 2765 / hands-on 12088 words = 18.6%, below the 30-35% target; notes are 533-547 words (cap 550) and labs were not cut (KNOWN-GAPS 45).
- **Concept share after L400 (2026-10-28, same REBALANCE script, every level):** L100 concept 1500 / hands-on 7730 = 16.3% · L200 2026 / 7764 = 20.7% · L300 2777 / 12922 = 17.7% · **L400 + capstone 4283 / 19506 = 18.0%** (target 35-40%) · whole topic 10586 / 47922 = 18.1%. The L400 notes are full length (728-750 words; capstone 545). The design fields (brief, options, ADR pointer, fitness, scaling limits) and the capstone's milestones and rubric add hands-on words; nothing was padded or cut (KNOWN-GAPS 65).
- **Concept share, measured after the L300 update pass (2026-10-28, same script, all levels):** L100 concept 1500 / hands-on 7730 = 16.3% · L200 concept 2026 / hands-on 7673 = 20.9% · L300 concept 2777 / hands-on 12828 = 17.8% · whole topic concept 6303 / hands-on 28231 = 18.3%. Target 30-35%. The notes are at their caps (L100 ≤ 250, L200 ≤ 400, L300 ≤ 550 words). The new learning tools, provenance step and links added hands-on words, and nothing was padded (KNOWN-GAPS 45).
- **Concept share after L400 (2026-10-28, same REBALANCE script, every level):** L100 concept 1500 / hands-on 7730 = 16.3% · L200 2026 / 7764 = 20.7% · L300 2777 / 12922 = 17.7% · **L400 + capstone 4283 / 19506 = 18.0%** (target 35-40%) · whole topic 10586 / 47922 = 18.1%. The L400 notes are full length (728-750 words; capstone 545). The design fields (brief, options, ADR pointer, fitness, scaling limits) and the capstone's milestones and rubric add hands-on words; nothing was padded or cut (KNOWN-GAPS 65).
