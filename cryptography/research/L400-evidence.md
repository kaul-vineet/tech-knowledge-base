# L400 evidence – Applied Cryptography ("Design it", lessons 17-21 + capstone 22)

Method as in L100-L300 (SPEC.md): implementation questions per lesson → primary sources only (specs, RFCs, official docs,
maintained OSS repositories) → score 0-2 on six criteria (keep ≥ 8/12) → every API checked by running it against
**pyca/cryptography 50.0.2** (wheel built with OpenSSL 4.0.3) on Python 3.12.15 in the sandbox. All pages were fetched on 2026-10-28.
Vendor pages appear only as one-line equivalents. What could not be run is listed in each lesson's `validation.pendingCi` and in KNOWN-GAPS.

## Key finding: post-quantum support in cryptography 50.0.2 (verified by docs + run)
- Docs: the `mlkem` module (ML-KEM-768/1024, "Added in version 47.0.0") and the `mldsa` module (ML-DSA-44/65/87, 47.0.0;
  `sign_mu` in 49.0.0; `MLDSAMuHasher` in 50.0.0). Changelog 48.0.0: "Added support for ML-KEM key encapsulation and ML-DSA
  signing when using OpenSSL 3.5.0 or later … post-quantum algorithms are now available to users of our wheels."
  Changelog 50.0.2: wheels compiled with OpenSSL 4.0.3. HPKE (RFC 9180, 47.0.0) offers `KEM.MLKEM768_X25519`, which the docs say is "also known as X-Wing".
- Run: `MLKEM768PrivateKey.generate()` gives a 1,184 B public key, a 1,088 B ciphertext and a 32 B secret. ML-DSA-65 gives a 1,952 B public key and a 3,309 B signature,
  and signing is randomised (two signatures over the same message differ). `hpke.Suite(KEM.MLKEM768_X25519, …)` gives a 1,120 B encapsulation.
  ML-DSA-65 X.509 certificates are 5,396 B (root) and 5,401 B (leaf). `cryptography.hazmat.backends.openssl.backend.openssl_version_text()` = OpenSSL 4.0.3.
- **The stdlib `ssl` module here links OpenSSL 3.3.7** (no ML-KEM groups) and Python 3.12 has no `SSLSocket.group()`, which
  Python 3.15 adds. So the TLS-level X25519MLKEM768 check is pending CI (`pq_tls_probe.py`).
- Conclusion: liboqs-python and oqs-provider are **not needed** for the lab. They stay as pending-CI interop checks; oqs-provider
  disables its own ML-KEM/ML-DSA and the three RFC 10024 hybrids on OpenSSL ≥ 3.5.

## 17 Crypto agility
Questions: How should an algorithm identifier be carried and checked? How do you deprecate without a flag day? How do you dual-sign without a stripping attack?
| Source | Score | Kept/dropped | Key facts used |
|---|---|---|---|
| RFC 7696 (BCP 201) Guidelines for Cryptographic Algorithm Agility | 12 | kept | §2.1 algorithm identifiers (key table with key and algorithm identifier); registry entries are never changed, only marked deprecated; §2.4 negotiation SHOULD be integrity-protected (downgrade); §3.2 too many choices can be harmful; §2.3 / RFC 6916, where a second signature is introduced and the old one phased out |
| NIST CSWP 39 (Considerations for achieving crypto agility) | 10 | kept (landing page) | definition of crypto agility; the final version was withdrawn 2026-06-29 and superseded by CSWP 39upd1 (not fetched) |
| draft-ietf-lamps-pq-composite-sigs-19 | 10 | kept as background | composite ML-DSA with Ed25519; an EUF-CMA caveat; the alternative to our separate dual signatures; RFC Editor queue |
| pyca/cryptography AEAD + Ed25519 + ML-DSA docs | 12 | kept | APIs run |
Dropped: vendor "crypto-agility" blogs (marketing).

## 18 Post-quantum cryptography in practice
Questions: Does cryptography 50.0.2 expose ML-KEM/ML-DSA? What is the current TLS hybrid group and its exact share layout? What does the switch cost?
| Source | Score | Kept/dropped | Key facts used |
|---|---|---|---|
| RFC 10024 (was draft-ietf-tls-ecdhe-mlkem), August 2026 | 12 | kept | X25519MLKEM768 = 0x11EC (Recommended: Y); client share 1216 = 1184 + 32 with ML-KEM first; server share 1120; 64 B secret with ML-KEM first; client MUST check the ciphertext length (illegal_parameter); SecP384r1MLKEM1024 shares 1665/1665; obsoletes X25519Kyber768Draft00 |
| FIPS 203 / FIPS 204 (CSRC pages) | 12 | kept | final 2024-08-13; ML-DSA described as secure against quantum adversaries |
| NIST IR 8547 (final 2026-10-27; ipd 2024-11-12) | 10 | kept (landing pages) | transition approach to PQC; the final cites EO 14412 / OMB M-26-15. Deprecation dates were **not** read from the PDF and are not stated in the lab |
| pyca/cryptography ML-KEM, ML-DSA, HPKE docs + changelog | 12 | kept | see the key finding above |
| liboqs-python (GitHub + PyPI 0.16.0.1, MIT, 2026-09-23) | 10 | kept (pending CI) | `KeyEncapsulation`, `encap_secret`, `decap_secret`, `generate_keypair`, `details`; builds liboqs 0.16.0 on first import; prototyping only |
| oqs-provider (GitHub, MIT) | 9 | kept as equivalent | disables standardised algorithms on OpenSSL ≥ 3.5; "not recommended for production" |
| Python `ssl` docs (3.15) | 11 | kept | `SSLSocket.group()` added in 3.15; `SSLKEYLOGFILE` |

## 19 Keys in hardware-style storage
Questions: Which PKCS#11 attributes make a key non-exportable? How does an app sign through a handle? What can we run without hardware?
| Source | Score | Kept/dropped | Key facts used |
|---|---|---|---|
| OASIS PKCS #11 Specification v3.1 (2023-07-23) | 11 | kept | object/handle/session model, C_Login, C_Sign, C_WrapKey; table of contents read. The attribute semantics of CKA_SENSITIVE / CKA_EXTRACTABLE / ALWAYS / NEVER come from the private-key attribute table: the HTML body around §4.9 was not in the fetched text (KNOWN-GAPS) |
| SoftHSM2 (GitHub README + releases; Homebrew `softhsm` 2.7.0, BSD-2-Clause) | 11 | kept | `softhsm2-util --init-token --slot 0 --label …`; `SOFTHSM2_CONF`; 2.7.0 released Jan 2026; ML-DSA/ML-KEM support added later on main; Ubuntu noble ships 2.6.1 |
| python-pkcs11 0.10.1 (PyPI, MIT) | 10 | kept (pending CI) | `lib.get_token(token_label=)`, `token.open(user_pin=)`, `create_domain_parameters(...).generate_keypair()`, `priv.sign(mechanism=)`; tested against SoftHSMv2 |
| OpenBao transit API 2.7.x | 11 | kept | `exportable` (bool: false) can never be turned off once set; `/transit/export/:key_type/:name`; key types include `mldsa-65`; `external-key` for HSM/KMS-backed keys |

## 20 End-to-end encryption for groups
| Source | Score | Kept/dropped | Key facts used |
|---|---|---|---|
| RFC 9420 Messaging Layer Security | 12 | kept | FS + PCS for groups from 2 to thousands; sender keys need PCS updates that scale with the square of the group size; a Commit gives fresh entropy to members of the new epoch only; resolution / copath / filtered direct path; log(N) encryptions; Updates "SHOULD be sent at regular intervals" |
| OpenMLS (GitHub, MIT) + book "Removing members" | 10 | kept (pending CI) | RFC 9420 implementation; `remove_members`, `merge_staged_commit`, `is_active()`; MTI ciphersuite X25519/AES128GCM/Ed25519 |
Toy deviations from MLS: heap-order tree, no signatures/credentials/tree hashes/Welcome/secret tree (stated in the lab and the ADR).

## 21 Threat modelling
| Source | Score | Kept/dropped | Key facts used |
|---|---|---|---|
| OWASP Threat Modeling Cheat Sheet | 11 | kept | the four questions (Threat Modeling Manifesto); DFD with trust boundaries; the STRIDE table with violated properties; attack trees, misuse cases, LINDDUN; responses mitigate/eliminate/transfer/accept; "Can the agreed upon mitigations be tested?" |
The lab's STRIDE-per-element applicability table (external S,R; process all; store and flow T,I,D) is the commonly taught chart; its original source (Shostack's book) was not fetched (KNOWN-GAPS).

## 22 Capstone
Reuses lessons 9, 10, 12, 16, 17, 18, 19 and 21 by import. No new sources beyond the above.

## Numbers used in notes and ADRs (all from code that ran here; timings are machine-dependent)
See `labs/L400/*/README.md` "Expected output". These include: 31 extra header bytes; 1000/1000; 3,373 B dual signature; 2,336 B hybrid on the wire; 478 B vs 14,106 B certificate chains;
≈35/≈40/≈5,002 µs signing (file/token/KMS); 4/10/14 vs 42/3,906/64,770 encryptions per removal; 48 of 56 leaking pairs; 41 STRIDE
candidates; attack-tree costs 9 → 8 → 6; capstone 6/6 milestones.
