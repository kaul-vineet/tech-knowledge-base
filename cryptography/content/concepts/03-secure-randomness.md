## Why it matters
Your password-reset token comes from `random.getrandbits(128)` seeded with the server clock. An attacker who knows roughly when you asked for the reset replays every possible seed; the lab recovers the token in under a second. Keys, nonces, salts and tokens are only as strong as their generator.

## Mental model
`random` is a **music box**: same seed, same tune. `secrets` is **dice thrown by the operating system**, which nobody can replay.

```
 random.Random(seed) ──► same seed ⇒ same sequence   (simulations, tests)
 secrets / os.urandom ──► OS CSPRNG ⇒ unpredictable  (keys, nonces, salts, tokens)
```

## How it works
1. **Size in bytes × 8 = strength in bits.** `token_bytes(32)` gives 256 bits for an AES-256 key; a GCM nonce is 12 bytes; `token_urlsafe(32)` prints as 43 characters → see lab step 2.
2. **The search space is what matters.** An attacker doesn't "break" the PRNG; trying every plausible seed is enough. A clock seed known within ±1 hour leaves only 7,201 candidates (about 2^12.8), versus 2^256 for a 32-byte `secrets` token (`research/concept_examples.py`) → see lab step 3.
3. **PRNGs are deterministic.** Python's `random` is the Mersenne Twister, "completely unsuitable for cryptographic purposes": `Random(42)` twice gives the identical sequence, while `secrets` never repeats → see lab step 4.

## Common mistakes
- Using `random.choice` to build a temporary password.
- "Improving" randomness by hashing the time. A hash of a guessable value is still guessable.
- Passing bits where the API expects bytes (`token_bytes(256)` gives 256 *bytes*).
