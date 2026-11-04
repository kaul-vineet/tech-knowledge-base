# Applied Cryptography – Concepts primer

Read this once before Lesson 1. Numbers come from `research/concept_examples.py` (output in `research/concept_examples.out.txt`) or a cited source.

## What it is for

Applied cryptography is a set of vetted building blocks you combine to protect data. You don't design them; you pick the right one and use it correctly. You meet them every day:
- **TLS 1.3** (web/API traffic) allows only AEAD for record protection ([RFC 8446](https://www.rfc-editor.org/rfc/rfc8446.html)).
- **WireGuard** VPN encrypts packets with ChaCha20-Poly1305 ([protocol](https://www.wireguard.com/protocol/)).
- **pip `--require-hashes`** rejects packages whose SHA-256 doesn't match the pin ([pip](https://pip.pypa.io/en/stable/topics/secure-installs/)).
- **Login systems** store passwords as Argon2id hashes ([OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)).

## One mental model: four questions, four tools

Ask what you must protect against; each answer maps to one primitive, and every primitive needs good randomness.

```
             What must be protected?
                        |
   +------------+-------+------+--------------+
   | changes    | changes      | readers      | a guessable
   | (public)   | (who wrote?) | (secrecy)    | secret (password)
   v            v              v              v
 HASH         MAC (HMAC)     AEAD           PASSWORD HASH
 SHA-256      key + msg      key + nonce    Argon2id + salt

   keys, nonces, salts and tokens come from a CSPRNG (secrets / os.urandom)
   ENCODING (base64, hex) is not on this map: it protects nothing.
```

## Concept map: L100 → L400

L100-L400 and the capstone are built.
- **L100 – Run it:** pinned toolchain, hash vs HMAC, CSPRNG vs PRNG, AEAD with nonces and AAD, Argon2id, encoding vs hashing vs encryption.
  *Local agent:* explains findings of a misuse linter on a snippet; the linter judges (lesson 6).
- **L200 – Build it (built):** Ed25519 signatures and key serialization, X25519 + HKDF + AEAD encryption to a public key (age/HPKE pattern), a local CA with X.509 path validation, TLS on localhost (+ mTLS), signed tokens with an algorithm allow-list (RFC 8725).
  *Local agent (lesson 9):* explains a certificate-validation failure; the verifier and `diagnose()` decide, and no keys are sent.
- **L300 – Harden it (built):** envelope encryption and KEK rotation (OpenBao transit), certificate renewal and CRLs, signed release manifests, Wycheproof vectors with timing and nonce-reuse checks, secrets in logs and key rotation.
  *Local agent (lesson 16):* reviews a redacted log for leaks; a deterministic scanner decides and a secret gate blocks key material.
- **L400 – Design it:** crypto agility, post-quantum (ML-KEM, ML-DSA, hybrids), keys in hardware (PKCS#11), group E2EE (MLS), threat models; capstone: encrypted document service.
  *Local agent (proposal):* suggests fuzz seeds and review-checklist items; fuzzers and vectors decide; no key material in prompts.

## Glossary

| Term | Meaning |
|---|---|
| Hash | Fixed-size, one-way fingerprint; SHA-256 gives 32 bytes. |
| HMAC | Keyed tag proving the sender holds the key. |
| CSPRNG | The OS's secure random generator, read via `secrets`. |
| Nonce | Number used once; 12 bytes for AES-GCM/ChaCha20-Poly1305, never repeated per key. |
| AEAD / AAD | Encryption plus integrity in one call / data authenticated but not encrypted. |
| Tag | 16-byte authenticator appended to AEAD ciphertext. |
| Salt | Unique random value stored with each password hash. |
| PHC string | `$argon2id$v=19$m=..,t=..,p=..$salt$hash`. |
| Test vector | Published input/output pair that proves an implementation correct. |

## Common misconceptions

1. **"Base64 hides it."** No. RFC 4648 §12: base encoding gives no confidentiality. `QWxhZGRpbjpvcGVuIHNlc2FtZQ==` decodes to `Aladdin:open sesame` without a key.
2. **"A hash proves who sent it."** No. Anyone can recompute SHA-256; authenticity needs a key (HMAC or AEAD).
3. **"SHA-256 is fine for passwords if I add a salt."** No. It's far too fast: about 262,000 guesses/s against about 12 for Argon2id with OWASP parameters (sandbox, single core, indicative only).
