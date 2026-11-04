# L200 research evidence – Applied Cryptography ("Build it", lessons 7-11)

Research date: 2026-10-28. Method as in `L100-evidence.md`. I wrote 2-3 implementation questions per lesson, then used web_search/web_fetch on RFCs, official library docs and maintained open-source repositories. Each source was screened and scored 0-2 on six criteria (implementable, current, authoritative, open, transferable, right depth), and kept at ≥ 8/12. Every claim was cross-checked against at least two sources, one of them official, and against local execution where possible.

Local environment (observed): Python 3.12.15, `cryptography` 50.0.2, stdlib `ssl` linked to OpenSSL 3.3.7, PyJWT 2.15.1 installed, Node 24.7. No `openssl`, `age`, `mkcert` or `step` binaries are installed. Concept-note numbers come from `l200_concept_examples.py` (output in `l200_concept_examples.out.txt`).

---

## Lesson 7 – Digital signatures with Ed25519
**Questions:**
- How do you sign and verify, and what exception does a failure raise?
- How are Ed25519 keys serialized (raw, PEM, OpenSSH)?
- Which official vector proves the implementation?

| Candidate | Decision | Score |
|---|---|---|
| RFC 8032 (EdDSA) | kept | 11 |
| pyca/cryptography – Ed25519 signing | kept | 12 |

**Key facts**
- Ed25519 keys are 32 octets and signatures are 64 octets. TEST 1 is: secret `9d61b19d…7f60`, public key `d75a9801…511a`, empty message, signature `e5564300…100b`. (RFC 8032 §7.1) – reproduced locally.
- RFC 8032 §1 states that a unique random number is not required for each signature, so signing is deterministic. – verified locally (try_it 1).
- `sign()` returns 64 bytes and `verify()` raises `InvalidSignature`. Raw serialization requires the Raw format, otherwise use PKCS8/OpenSSH (private) or SubjectPublicKeyInfo/OpenSSH (public). (pyca docs) – verified locally: PEM 119/113 bytes, OpenSSH 80 bytes.

## Lesson 8 – Key exchange and hybrid encryption
**Questions:**
- How does X25519 agreement become an AEAD key?
- How does age do it?
- What must be checked for degenerate keys?
- How does HPKE standardize the pattern?

| Candidate | Decision | Score |
|---|---|---|
| RFC 7748 | kept | 11 |
| pyca/cryptography – X25519 | kept | 12 |
| C2SP age spec (c2sp.org/age and GitHub age.md) | kept | 11 |
| RFC 9180 HPKE | kept | 10 |
| age README (FiloSottile/age) | kept | 9 |
| raw.githubusercontent.com C2SP age.md / c2sp.org/age@v1.0.0 | dropped – fetch returned no document | – |

**Key facts**
- RFC 7748 §6.1 vector: a `77076d0a…2c2a`, B `de9edb7d…2b4f`, K `4a5d9d5b…1742`. Implementations MAY abort on an all-zero K. – reproduced locally. pyca raises `ValueError` for an all-zero peer key.
- pyca docs: for most applications the shared key should be passed to a KDF, and a new private key must be generated for each exchange.
- age X25519 stanza: salt = ephemeral share ‖ recipient, info = "age-encryption.org/v1/X25519", wrap key = HKDF-SHA-256, body = ChaCha20-Poly1305 with a fixed 12-byte zero nonce, abort on an all-zero shared secret. (C2SP age.md) – the lab uses the same structure with its own label.
- HPKE combines a KEM, a KDF and an AEAD. DHKEM(X25519, HKDF-SHA256) has id 0x0020. For X25519, recipients MUST abort on an all-zero DH output. (RFC 9180 §4, §7.1, §7.1.4)
- age CLI usage: `age-keygen -o key.txt`, `age -r age1… > file.age`, `age --decrypt -i key.txt`. Install with `brew install age` or `winget install --id FiloSottile.age`. (age README)

## Lesson 9 – A local certificate authority
**Questions:**
- Which extensions do a root and a server leaf need?
- How do you run path validation in Python?
- What do mkcert and step do instead?

| Candidate | Decision | Score |
|---|---|---|
| pyca/cryptography – X.509 tutorial | kept | 12 |
| mkcert README | kept | 9 |
| smallstep – step certificate | kept | 8 |

**Key facts**
- The pyca tutorial root uses BasicConstraints(ca=True), KeyUsage(key_cert_sign, crl_sign) and SKI. The leaf uses SAN, BasicConstraints(ca=False), KeyUsage, EKU and AKI. Verification uses `PolicyBuilder().store(Store([root])).build_server_verifier(DNSName(...)).verify(leaf, intermediates)`, and the tutorial chain has length 3. – the lab and build task use the same API. The build task's 3-link chain verifies locally.
- A root without KeyUsage fails with "Certificate is missing required extension" (observed locally, cryptography 50.0.2).
- mkcert: `mkcert -install` creates a local CA in the system trust store. Its README warns that `rootCA-key.pem` "gives complete power to intercept secure requests" from the machine. Install with brew (macOS) or choco/scoop (Windows).
- step: `step certificate create foo foo.crt foo.key --profile root-ca`, and `--ca/--ca-key/--san` for leaf certificates. (smallstep docs)

## Lesson 10 – TLS on localhost
**Questions:**
- What do `create_default_context` and `PROTOCOL_TLS_CLIENT` enforce?
- What do verification errors expose?
- Which `s_client` options reproduce the checks?

| Candidate | Decision | Score |
|---|---|---|
| Python docs – ssl | kept | 12 |
| OpenSSL – openssl-s_client(1) | kept | 10 |
| RFC 8446 (already retrieved for L100) | kept | 10 |

**Key facts**
- `PROTOCOL_TLS_CLIENT` enables CERT_REQUIRED and check_hostname by default. CERT_REQUIRED alone does not match hostnames. Since Python 3.10 the minimum version is TLS 1.2. `SSLCertVerificationError` has `verify_code` and `verify_message`. `version()` and `cipher()` describe the negotiated session. (Python ssl docs) – observed locally: TLSv1.3 TLS_AES_256_GCM_SHA384, codes 62 and 20.
- `s_client` supports `-connect`, `-servername`, `-CAfile`, `-verify_return_error` and `-brief`. (OpenSSL docs, master and 3.5/4.x pages) – not executed locally (no binary). `test_openssl_cli.py` runs in CI.
- macOS ships LibreSSL as `/usr/bin/openssl` (from the L100 evidence). The lab uses Homebrew `openssl@3` for identical options.

## Lesson 11 – Tokens done right
**Questions:**
- Which RFC 8725 rules stop alg:none and key confusion?
- How must exp, nbf and aud be checked?
- How does PyJWT expose the same controls?

| Candidate | Decision | Score |
|---|---|---|
| RFC 8725 (JWT BCP) | kept | 12 |
| PyJWT usage docs (2.15.1) | kept | 10 |
| RFC 7519 (JWT) | not fetched separately – PyJWT docs and RFC 8725 quote the relevant text | – |

**Key facts**
- RFC 8725 §2.1: "alg" can be changed to "none", and RS256 can be swapped to HS256 with the public key used as the HMAC secret. §3.1: libraries MUST let the caller specify the supported algorithms, and "each key MUST be used with exactly one algorithm". §3.9: the relying party MUST validate aud. §3.5: passwords MUST NOT be used directly as HS256 keys.
- PyJWT: `decode(..., algorithms=[...])`, `audience=` raises `InvalidAudienceError`, `ExpiredSignatureError`, `leeway`, `options={"require": [...]}`, EdDSA support. jti is used to detect replays. – verified locally against PyJWT 2.15.1 (`test_pyjwt_equivalence.py`).

## Agent assist (lesson 9)
I reused the vendored `labs/_shared/local_agent`. The fake server got one more documented EXTRA_RULES entry, `[[CERT-EXPLAIN]]`, which is deliberately naive: it misreads "not yet valid" as EXPIRED. The Ollama source is the one already kept in L100. No real model was run.

## Learning-tools pass (2026-10-28)
Questions:
- Which catalogue tools can check each lab's printed output?
- Does Python's ssl write a key log that Wireshark can use?
- Which `step crypto jwt verify` flags fit tokens that have no `iss` claim?

Sources:
- Tool facts come from `shared/LEARNING-TOOLS-CATALOG.md`.
- Python ssl docs (fetched): `create_default_context()` enables key logging when `SSLKEYLOGFILE` is set (since 3.8). Checked locally: lab 10 with `SSLKEYLOGFILE` wrote 8 lines (1 comment + 7 secrets).
- CyberChef `Argon2.mjs` (fetched): operation arguments and defaults. The exercise uses the lab's parameters (t=2, m=19456, p=1) with salt `somesalt`.
- smallstep `jwt verify` reference (fetched): `--iss` is required unless `--subtle` is given.

Expected values: `learning_tools_expected.py` → `learning_tools_expected.out.txt`.
