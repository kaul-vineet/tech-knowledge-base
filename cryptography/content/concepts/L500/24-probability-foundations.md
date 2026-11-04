# Foundations II: probability for cryptography

## Why it matters
Most cryptographic failures are not about breaking AES. They are about something that "can't happen" happening anyway: two messages under the same GCM nonce, two users with the same salt or ID, or a key derived from a password with far less randomness than its length suggests. Probability tells you **how unlikely** "unlikely" is and **how fast** it stops being unlikely. In practice it turns rules of thumb ("rotate keys before 2^32 messages") into numbers you can defend in a design review.

## Definitions
- **Collision.** Among q values drawn independently and uniformly from N possibilities, two are equal.
- **Union bound.** Pr[A₁ ∪ … ∪ A_k] ≤ Σ Pr[Aᵢ].
- **Shannon entropy.** H(X) = −Σ p(x) log₂ p(x) measures average uncertainty in bits.
- **Min-entropy.** H∞(X) = −log₂ max_x p(x). An attacker's best single guess succeeds with probability exactly 2^(−H∞).
- **Negligible function.** ε(n) is negligible if for every c, ε(n) < n^(−c) for all sufficiently large n. Examples: 2^(−n) and 2^(−√n) are negligible; 1/n³ is not.

## Key results
1. **Birthday upper bound (T24.1).** Pr[collision] ≤ q(q−1)/(2N). Proof: there are q(q−1)/2 pairs, each pair collides with probability 1/N, and the union bound adds them up.
2. **Birthday lower bound (T24.2).** Pr[collision] ≥ 1 − exp(−q(q−1)/(2N)). Proof: the probability of no collision is Π(1 − i/N), and 1 − x ≤ e^(−x). Setting the bound to 1/2 gives the threshold q ≈ 1.1774·√N.
3. **Nonce budget (T24.3).** For random 96-bit nonces under one key, the collision probability is at most q²/2^97. That is ≈ 2^−33 at q = 2^32, it reaches 2^−32 at q = 2^32.5 ≈ 6.07·10^9 messages, and it reaches ≈ 39 % at q = 2^48. NIST SP 800-38D limits random-IV GCM to 2^32 invocations per key for this reason.
4. **Entropy and negligibility (T24.4).** H∞ ≤ H ≤ log₂|S|, with equality iff the distribution is uniform. A polynomial times a negligible function is negligible, so an efficient attacker with polynomially many tries still has a negligible chance.

## Intuition
Collisions grow with the number of **pairs**, not the number of items. Twenty-three people form 253 pairs, which is plenty to find one shared birthday among 365. For nonces this means the risk grows quadratically with traffic. Doubling the traffic quadruples the risk, and halving the nonce length (96 → 48 bits) moves the danger point from 2^48 to 2^24 messages.

Min-entropy captures the **weakest point** of a distribution. A PIN scheme where "1234" is chosen 10 % of the time has ≈ 12.4 bits of Shannon entropy but only 3.3 bits of min-entropy, so one guess wins one time in ten.

## Worked example (lab output, labs/L500/24-probability)
- N = 365: the exact product first exceeds 1/2 at q = 23 (P = 0.507297). The upper bound gives 0.693 and the formula gives 22.49.
- N = 2^32: the first q with P ≥ 1/2 is 77164; the formula gives 77163.
- A Monte-Carlo scale model with N = 2^24, q = 4096 and 2000 trials observes 0.400. The lower bound predicts 0.393. The simulation uses a seeded random.Random, which is fine for an experiment and never acceptable for keys.
- 96-bit nonces: 2^32 messages give P = 1.1642·10^−10 = 2^−33.00. The budget for a 2^−32 risk is 6.0740·10^9 = 2^32.50 messages. Among 2^20 nonces from os.urandom(12) the lab found 0 collisions, which is expected because the bound there is ≈ 2^−57.
- **Engineering consequence.** At 10^6 messages per second a single key hits 2^32 messages in 71.6 minutes, and at 10^4 per second in 4.97 days. Fixes: rotate keys (L300 #12), use counter nonces where one writer owns the key, derive per-message keys, or use 192-bit nonces (XChaCha20-Poly1305: ≈ 2^−97 after 2^48 messages).

## Negligible, concretely
Proofs say "the advantage is negligible". To turn that into numbers, plug in parameters. An attacker making 2^40 queries, each succeeding with probability 2^−128, wins with probability at most 2^−88 by the union bound. The lab also confirms numerically that n^10·2^−n < n^−3 for every n ≥ 83. Asymptotic statements hide constants, so always evaluate them at your real parameters.

## Choosing a nonce strategy with these numbers
Write down three quantities: messages per second per key, key lifetime, and an acceptable collision risk (2^−32 is the conventional target). Their product gives q, and the bound q²/2^97 tells you whether random 96-bit nonces fit. If they do not, either shorten the key lifetime (rotation), give each writer its own key and a counter, or switch to a 192-bit nonce construction. Record the calculation in the ADR so the next reviewer can recheck it.

## Common misconceptions
- **"96 bits of nonce means 2^96 messages are safe."** Collisions appear around 2^48, and the conservative budget is 2^32.
- **"Random nonces are always better than counters."** Counters never collide but need state. Random nonces are stateless but have a birthday budget. Choose based on who generates nonces and whether state survives restarts.
- **"Entropy is the length of the secret."** A 16-character password chosen by a human may have the min-entropy of a short PIN. KDF inputs and passwords are judged by min-entropy (NIST SP 800-90B uses min-entropy for entropy sources).
- **"Negligible means zero."** It means smaller than any inverse polynomial, eventually. At small parameters, negligible functions can still be large (2^−n at n = 20 is about one in a million).
- **"The union bound is loose, so ignore it."** For q² ≪ N it is essentially exact. The lab shows the upper and lower bounds agreeing to many digits for 96-bit nonces.

## Where this shows up later
The birthday bound sets hash output sizes (collision resistance of SHA-256 ≈ 2^128), the security of 64-bit block ciphers (Sweet32), the size of random IDs and salts, and the nonce rules for GCM and ChaCha20-Poly1305. Lesson 25 uses the union bound and negligible functions in every proof.
