## Why it matters
pyca/cryptography is tested against Project Wycheproof; your code around it is not. Teams wrap the library to "help": accept short tags for an old client, trim a signature that arrived with a newline, reduce an out-of-range value. Each convenience turns a reject into an accept. Known-answer tests, a timing check and a nonce audit make these mistakes visible in CI.

## Mental model
Wycheproof is a **crash-test catalogue**: hundreds of cars (inputs), each labelled with the expected outcome (valid, invalid, acceptable). You drive *your* wrapper through them and compare.

```
vectors/*.json ─▶ harness ─▶ your aead_open / sig_verify ─▶ got == result ?  ─▶ PASS / FAIL tcId
                              (library inside is fine; the wrapper is under test)
```

## How it works
1. **Format.** Each file has `algorithm`, `numberOfTests` and `testGroups`. AEAD groups (`AeadTest`) list `key`, `iv`, `aad`, `msg`, `ct`, `tag` and `result`; EdDSA groups (`EddsaVerify`) carry a public key and tests with `msg`, `sig`, `result` and `flags`. The lab vendors 16 Wycheproof tests with the Apache-2.0 licence (copied from downstream copies; CI checks them against upstream), plus 5 derived ones clearly marked as not Wycheproof → see lab steps 1-2 and 7.
2. **Harness.** One loop feeds every test to the wrapper and treats any exception as "invalid". It reports each tcId where the result differs → see lab step 1.
3. **Strict wrappers.** The fix demands a 16-byte tag and 12-byte IV through the high-level `AESGCM` API, exactly 64 signature bytes, and S < L. The build task proves it → see lab step 3.
4. **Timing.** An early-exit byte loop returns sooner when the first byte is wrong. Seeded inputs, interleaved rounds and medians make the difference visible over noise; `hmac.compare_digest` shows none → see lab step 4.
5. **Nonce reuse.** An in-process tripwire refuses a repeated nonce, but a restart resets it. An offline scan of stored ciphertexts catches the seeded-PRNG bug across restarts → see lab step 5.

Worked example (one lab run): all 16 vendored Wycheproof vectors passed even through the lenient wrappers. The derived tests failed 4 of 5: tcIds 9001 and 9002 (8- and 4-byte tags) and 9101 and 9102 (an appended byte, S + L). After the fix all 21 passed. Timing: 397 ns vs 1056 ns (ratio 2.66) for the naive loop, 125 ns vs 125 ns (1.00) for `compare_digest`. The nonce scan found 2 reused nonces after 2 restarts with seeded nonces, and 0 with `os.urandom`.

## Failure modes
- **Truncated tags.** A 4-byte tag means a forgery succeeds once in 2^32 tries instead of 2^128. The only visible symptom is a test vector that should fail but passes.
- **Malleable signatures.** Two byte strings that both verify break de-duplication, replay caches and "signature as ID" designs.
- **Timing tests that flake.** Shared CI runners are noisy. Assert only large, structural effects with generous margins, and treat small ratios as "no evidence", not proof of safety.
- **Nonce reuse across processes.** In-memory checks cannot see it; only a scan of what was stored can.

## Common mistakes
- Testing the library instead of your wrapper, then trusting the wrapper because "it uses a vetted library".
- Copying vectors without their licence or without recording where they came from.
- Comparing secrets with `==` because "it's fast anyway"; use `hmac.compare_digest`.
