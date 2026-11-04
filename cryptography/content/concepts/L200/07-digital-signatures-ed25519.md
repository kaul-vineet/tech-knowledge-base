## Why it matters
You publish `app-1.0.tar.gz` on a mirror. A SHA-256 checksum helps only if it arrives safely, and HMAC needs a secret shared with every downloader. A signature fixes both: you keep a private key, publish the public key once, and anyone can check that the file came from you, unchanged.

## Mental model
A signature is a **wax seal anyone can inspect but only you can press**.

```
 private key ──sign(file)──► 64-byte .sig              (signer only)
 public key + file + .sig ──verify──► OK | InvalidSignature   (anyone)
```

## How it works
1. **Key pair.** An Ed25519 private key is 32 random bytes and the public key is 32 bytes derived from it. Sharing the public key reveals nothing about the private key → see lab step 1.
2. **Serialization.** On disk the private key is PKCS#8 PEM (119 bytes) and the public key is SubjectPublicKeyInfo PEM (113 bytes). Raw, both are 32 bytes. OpenSSH is a third encoding → see lab step 2.
3. **Detached signature.** `sign(data)` returns 64 bytes, stored next to the file as `app-1.0.tar.gz.sig`. The release itself is not modified → see lab step 3.
4. **Verify.** Verification needs only the public key. It raises `InvalidSignature` if one byte of the file or signature changes, or if the key is wrong → see lab step 4.
5. **Deterministic.** Ed25519 needs no per-signature random number, so the same key and message always give the same signature. That is why a fixed test vector can check it.

Worked example (RFC 8032 §7.1 TEST 1, empty message): secret `9d61b19d…7f60` gives public key `d75a9801…511a` and signature `e5564300…100b`. The lab reproduces both.

## Trade-offs
| Use when | Avoid when |
|---|---|
| One party signs, many verify (releases, packages, audit logs) | Both sides share a secret and need only integrity: HMAC is simpler |
| You want small keys and signatures (32 + 64 bytes) | A standard or HSM mandates RSA or ECDSA P-256 |
| You need deterministic, nonce-free signing | You need confidentiality: a signature hides nothing |

## Common mistakes
- Shipping the private key in the release or the repository. Only `.pub` goes public.
- Fetching the public key from the same mirror as the file, so an attacker can swap both. Pin it out of band.
- Reading "valid signature" as "safe to run". It proves who signed, not that the code is harmless.
