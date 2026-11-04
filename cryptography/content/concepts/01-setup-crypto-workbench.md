## Why it matters
Your teammate's script works on their laptop but fails on yours with `UnsupportedAlgorithm`, or quietly gives a different result. Crypto code depends on *which* library version and *which* OpenSSL build actually runs. If you can't name both, you can't trust or reproduce a result.

## Mental model
Your code talks to a thin Python layer; the real arithmetic runs in a compiled engine underneath. A known-answer test is your multimeter: it checks the whole stack end to end.

```
 lab code ──► pyca/cryptography 50.0.2 ──► bundled OpenSSL 4.0.3
          └─► stdlib hashlib/hmac/secrets ──► OS CSPRNG
```

## How it works
1. **Pin the library.** `requirements.txt` says `cryptography==50.0.2`, so every machine and CI runner installs the same API → see lab step 2.
2. **The wheel bundles its own engine, and features depend on it.** `backend.openssl_version_text()` reports the bundled OpenSSL 4.0.3, not your system `openssl`. Argon2id needs cryptography 44+ *and* OpenSSL 3.2+, so the sanity check derives a tiny key instead of only importing the class → see lab step 3.
3. **Known-answer tests prove correctness.** Feed a published input, compare with the published output. pyca, stdlib and the CLI all give `SHA256("abc") = ba7816bf…f20015ad`, the NIST value → see lab step 5.

## Common mistakes
- Installing into the global Python instead of a venv, so another project's pin overrides yours.
- Checking `import cryptography` but never running a known-answer test.
- Reading `openssl version` and believing it describes the library inside the wheel.
