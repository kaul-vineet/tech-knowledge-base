# L300 research evidence – Applied Cryptography ("Harden it", lessons 12-16)

Research date: 2026-10-28. Method as in `L100-evidence.md`: 2-3 implementation questions per lesson, web_search/web_fetch on specs, official docs and maintained repositories, sources scored 0-2 on six criteria (implementable, current, authoritative, open, transferable, right depth) and kept at ≥ 8/12, claims cross-checked against at least two sources (one official) and against local runs where possible.

Local environment (observed): Python 3.12.15, `cryptography` 50.0.2, no container runtime, no `openssl`, `bao`, `minisign`, `cosign` or `step` binaries, no internet for git/pip. Concept-note numbers come from `l300_concept_examples.py` (output in `l300_concept_examples.out.txt`). Fetch failures are listed in KNOWN-GAPS 46-50.

---

## Lesson 12 – Envelope encryption and key rotation
**Questions:** How do KMS/transit engines rotate a KEK without re-encrypting data? What does a ciphertext header carry? Which API retires an old version?

| Candidate | Decision | Score |
|---|---|---|
| OpenBao transit HTTP API (openbao.org/docs/api/secret/transit/, docs 2.7.x) | kept | 11 |
| OpenBao transit concepts (openbao.org/docs/secrets/transit/) | kept | 11 |
| Google Cloud KMS – envelope encryption + key rotation pages | demoted to a one-line equivalent (R3-13, L300 update) | 8 |
| AWS KMS cryptography essentials | demoted to a one-line equivalent (R3-13, L300 update) | 8 |
| NIST SP 800-57 Pt 1 Rev 5 landing page | kept (only abstract readable) | 8 |
| OpenBao `server` command docs (docs/next, search-result text) | kept for `-dev-root-token-id`, `-dev-listen-address` | 9 |

**Key facts**
- Transit paths: `POST /transit/keys/:name`, `/transit/encrypt/:name` (plaintext base64), `/transit/decrypt/:name`, `/transit/keys/:name/rotate`, `/transit/rewrap/:name` (never returns plaintext), `/transit/keys/:name/config` with `min_decryption_version`, `/transit/datakey/:type/:name` (plaintext|wrapped); deletion needs `deletion_allowed`. Ciphertext prefix `vault:v1:` = wrapped by OpenBao, key version 1. (OpenBao API + concepts)
- GCP: the DEK is wrapped by a KEK; "Rotating keys creates new active key versions, but doesn't re-encrypt your data and doesn't disable or delete previous key versions." AWS: re-encrypt only the data keys instead of the raw data. – matches the lab (rewrap leaves `ct` unchanged, verified locally).
- OpenBao 2.7.2 is the latest release (GitHub releases, ≈2026-10-27); MPL-2.0; `brew install openbao` (2.7.2); winget `OpenBao.OpenBao` only 2.5.4 (stale). Dev mode: `bao server -dev -dev-root-token-id=root`, default `127.0.0.1:8200`, in-memory, unsealed. Image `openbao/openbao` on Docker Hub/quay/ghcr.

## Lesson 13 – Certificate lifecycle
**Questions:** How do you build and check a CRL with pyca/cryptography? When should automated clients renew, and with what randomness? What changed for OCSP and certificate lifetimes?

| Candidate | Decision | Score |
|---|---|---|
| pyca/cryptography X.509 reference (CRL builder, RevokedCertificateBuilder, next_update_utc) | kept | 12 |
| pyca/cryptography OCSP | kept | 11 |
| RFC 5280 (§3.3, §5.1.2.4-5) / RFC 6960 | kept | 11 |
| RFC 9773 (ARI) | kept | 11 |
| Let's Encrypt integration guide / ending-OCSP post / 90→45 days post | kept | 10 |
| CA/B Forum ballot SC-081v3 + Baseline Requirements v2.2.7 | kept | 11 |
| Let's Encrypt 1-hour notBefore backdate (forum thread, snippet only) | dropped – not official | – |

**Key facts**
- `CertificateRevocationListBuilder.last_update` = thisUpdate, `next_update` = when the next CRL will be issued; `is_signature_valid()` alone is insufficient to trust a CRL; `get_revoked_certificate_by_serial_number` returns None if absent. – verified locally.
- RFC 9773: clients select a uniform random time within the suggested window. LE: check ARI twice a day; as a backstop renew with a third of the lifetime left, at a randomized time.
- LE OCSP plan (Dec 2024 post): OCSP URLs dropped 2025-05-07, responders off 2025-08-06. LE 160-hour short-lived certificates (GA Jan 2026, search-result text).
- SC-081: maximum validity 200 days from 2026-03-15, 100 days from 2027-03-15, 47 days from 2029-03-15 (BR v2.2.7 table).

## Lesson 14 – Signing the software supply chain
**Questions:** How do update frameworks bind many files to one signature? How do minisign/cosign sign blobs today? How do signers rotate?

| Candidate | Decision | Score |
|---|---|---|
| TUF specification 1.0.37 | kept | 11 |
| Sigstore docs – signing blobs, self-managed keys, verify | kept | 10 |
| cosign releases (v3.1.4) / Homebrew / winget manifests | kept | 9 |
| minisign releases (0.12) / Homebrew / winget | kept | 9 |
| SLSA provenance v1.1 page (v1.2 current) / in-toto.io | kept (background) | 8 |
| minisign README / docs site | dropped – blocked by the fetch tool | – |

**Key facts**
- TUF: targets metadata lists hashes and sizes (`length`, `hashes`) of target files; a new root must be signed by a threshold of old and new root keys.
- cosign key mode: `cosign generate-key-pair`; `cosign sign-blob --key cosign.key --bundle bundle.sigstore.json <file>`; bundles are the default in v3; `--yes` for CI. minisign 0.10+ prehashes by default; `-W` creates an unencrypted key.
- Lab check: the naive installer installs 5 files from a tampered release; the strict one rejects unknown files and digest mismatches (local runs).

## Lesson 15 – Misuse you can test
**Questions:** Where do Wycheproof vectors live now and what is their JSON shape? What does hmac.compare_digest promise? What happens when a GCM nonce repeats?

| Candidate | Decision | Score |
|---|---|---|
| C2SP/wycheproof repository + README (Apache-2.0, testvectors_v1) | kept | 12 |
| Wycheproof doc/files.md (search-result text: AeadTest result semantics) | kept | 10 |
| BoringSSL mirror of ed25519_test.json / eddsa_test.json (search-result text) | provenance record only, not a source (R3-03); checked against upstream by upstream_diff.py in CI | 9 |
| pycryptodome 3.7.2 copy of aes_gcm_test.json (Wycheproof 0.4, search-result text) | provenance record only, not a source (R3-03); checked against upstream by upstream_diff.py in CI | 8 |
| Python hmac / secrets docs | kept | 12 |
| NIST SP 800-38D; RFC 8452 | kept | 11 |
| Testing Handbook (appsec.guide) Wycheproof harness | kept (background) | 9 |
| raw.githubusercontent / jsDelivr copies of the vector files | dropped – fetch returned no document | – |

**Key facts**
- Wycheproof is a C2SP project, Apache-2.0; `testvectors/` and `testvectors_v1/` were merged into one directory; downstream users include pyca/cryptography, OpenSSL, BoringSSL, Go.
- Files: `algorithm`, `schema`, `numberOfTests`, `header`, `notes`, `testGroups`; EdDSA v1 group type `EddsaVerify`; AES-GCM group `AeadTest` with ivSize/keySize/tagSize; results valid / invalid / acceptable. – every vendored value verified locally against cryptography 50.0.2 (5 AES-GCM, 11 Ed25519).
- compare_digest avoids content-based short-circuiting; lengths/types may still leak. SP 800-38D: probability of a repeated IV under one key ≤ 2^-32; one repeat may allow forgeries. RFC 8452: with GCM-SIV, a repeated nonce only reveals equal plaintexts.
- pyca/cryptography rejects S + L for Ed25519 and GCM tags shorter than 4 bytes (local runs).

## Lesson 16 – Secrets handling in applications
**Questions:** Files, env vars or a store? What must not be logged? Can a logging.Filter rewrite records? How do platforms deliver secrets?

| Candidate | Decision | Score |
|---|---|---|
| OWASP Secrets Management Cheat Sheet | kept | 11 |
| OWASP Logging Cheat Sheet | kept | 11 |
| Python logging docs (Filter objects) | kept | 12 |
| Docker secrets / Kubernetes Secrets docs | Kubernetes kept; Docker demoted to a one-line equivalent (R3-13) | 10 |
| gitleaks / detect-secrets / GitHub secret scanning | kept as equivalents only | 8 |

**Key facts**
- OWASP: env vars are accessible to all processes and may end up in logs or dumps, "not recommended unless the other methods are not possible"; rotate regularly; use a secret management solution; keep secrets out of pipeline output. Logging: remove or mask access tokens, passwords, connection strings, encryption keys.
- Python: filters may modify records in place, and since 3.12 may return a replacement LogRecord (the lab modifies in place, so it also works on 3.9-3.11).
- Docker: secrets mounted under `/run/secrets/<secret_name>` (swarm). Kubernetes: Secrets stored unencrypted in etcd by default; mounted Secret volumes are updated.
- Agent assist: the gate reuses lesson 9's `SECRET` regex plus this lesson's scanner; tests use only the vendored fake model server.

## L300 update pass (2026-10-28)
- Re-read the OpenBao transit concepts page (2.7.x). It covers rotate (new version added to the keyring; old data still decrypts), rewrap ("does not reveal the plaintext"), the working set (`min_decryption_version` archives older versions and can be moved back in an emergency), and NIST rotation guidance (rotate AES-GCM keys before about 2^32 encryptions, per SP 800-38D). This replaces the vendor KMS pages for lesson 12.
- Re-read the NIST SP 800-57 Part 1 Rev. 5 landing page: May 2020, Elaine Barker, DOI 10.6028/NIST.SP.800-57pt1r5.
- Tried to fetch the upstream Wycheproof `testvectors_v1/aes_gcm_test.json` and `ed25519_test.json`: raw, blob, `?plain=1`, `/raw/`, the API, the commits page, jsDelivr and the local browser all failed (KNOWN-GAPS 59). The GitHub file page showed the tree and the latest commit title for aes_gcm_test.json ("testvectors_v1: reformat JSON files").
- New learning tools for 12/14/16 come from the shared catalog (OpenBao v2.7.2 MPL-2.0, minisign 0.12 ISC, Gitleaks v8.30.1 MIT); they were not re-fetched here.
