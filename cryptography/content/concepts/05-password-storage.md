## Why it matters
Your user table leaks. With plain SHA-256, a GPU tests billions of guesses and recovers common passwords in hours. With Argon2id and a unique salt, every guess costs memory and time *per user*, and most passwords survive.

## Mental model
A password hash is a **deliberately slow, salted lock**: you open it once per login, an attacker billions of times.

```
 password + salt (16 B) ──► Argon2id(m=19 MiB, t=2, p=1) ──►
 $argon2id$v=19$m=19456,t=2,p=1$<salt>$<hash>
```

## How it works
1. **Slow and memory-hard.** Argon2id's knobs are memory `m` (KiB), passes `t` and lanes `p`; OWASP's minimum is m=19 MiB, t=2, p=1. In the sandbox SHA-256 managed about 262,000 guesses/s against about 11.8 for Argon2id, roughly 22,000× slower (`research/concept_examples.py`, indicative only) → see lab step 2.
2. **Unique salt, self-describing string.** A random 16-byte salt makes equal passwords hash differently. The PHC string stores algorithm, parameters, salt and hash together, so you can raise parameters later. `hunter2` with salt `AAAA…` gives hash `mgNIy2Zf…`, with salt `BBBB…` an unrelated `APjZ7vE+…` (`research/concept_examples.py`) → see lab step 3.
3. **Verify by recomputing.** `verify_phc_encoded()` reads salt and parameters from the stored string, re-runs Argon2id and raises `InvalidKey` on mismatch. A trailing space or a different case fails too: there is no fuzzy match → see lab step 4.

## Common mistakes
- One global salt for all users, or none.
- Writing your own `sha256(salt + password)` loop, or encrypting passwords.
- Catching every exception on verify; catch `InvalidKey` and treat others as bugs.
