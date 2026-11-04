## Why it matters
You publish `release.tar.gz`; a user downloads it through a flaky mirror. Did they get exactly your bytes? Later your API receives `amount=100`. Did *your* frontend send it? A hash answers the first question. Only a keyed MAC answers the second.

## Mental model
A hash is a **fingerprint** anyone can take; an HMAC is a **wax seal** only holders of your stamp (the key) can make.

```
 HASH:  message ─────────► SHA-256 ──► 32-byte digest  (anyone can recompute)
 HMAC:  message + key ───► HMAC-SHA-256 ──► 32-byte tag (needs the key)
```

## How it works
1. **Fixed output, streamed input.** SHA-256 turns any input into 32 bytes (64 hex characters). `update(a); update(b)` equals `update(a+b)`, so a 1 MB file hashed in 64 KB chunks matches the OS tool (`sha256sum`, `shasum`, `certutil`) → see lab step 2.
2. **Avalanche.** A tiny change flips about half the output bits: `SHA256("abc")` and `SHA256("abd")` differ in 122 of 256 bits (`research/concept_examples.py`). One flipped byte in the lab file gives a completely different digest → see lab step 3.
3. **HMAC adds a key; verify in constant time.** With key `Jefe`, the RFC 4231 test message gives `5bdcc146…64ec3843`. Without the key nobody can tag an edited message. Compare tags with `hmac.compare_digest`, never `==` → see lab step 5.

## Common mistakes
- Publishing the checksum on the same server as the file, so an attacker swaps both.
- Comparing tags with `==` instead of `hmac.compare_digest`.
- Building a "keyed hash" as `sha256(key + msg)` instead of HMAC.
