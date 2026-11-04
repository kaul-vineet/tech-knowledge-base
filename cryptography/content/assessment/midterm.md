# Midterm exam (week 7) - 90 minutes, 60 marks

**Covers:** L100 (lessons 1-6), L200 (lessons 7-10) and L500 lessons 23-25 (to the end of IND-CPA/IND-CCA).
**Rules:** closed book. One A4 sheet of your own notes is allowed. A calculator is allowed, but show your working.
**Answers:** model answers and marking points are below. The numbers were verified with the lab code (labs/L500, Python 3.12, cryptography 50.0.2).

---

## Q1 - Derivation (10 marks)
(a) Use the extended Euclidean algorithm to compute 7⁻¹ mod 40. Show every step. (4)
(b) Toy textbook RSA uses p = 5, q = 11, e = 3. Compute n, φ(n) and d, then encrypt m = 9 and decrypt the result. (4)
(c) State one reason why this scheme must never be used as-is, even with a 2048-bit n. (2)

**Model answer.**
(a) 40 = 5·7 + 5; 7 = 1·5 + 2; 5 = 2·2 + 1. Back-substitute:
1 = 5 − 2·2 = 5 − 2·(7 − 5) = 3·5 − 2·7 = 3·(40 − 5·7) − 2·7 = 3·40 − 17·7.
So 7⁻¹ ≡ −17 ≡ **23** (check: 7·23 = 161 = 4·40 + 1). [2 for the steps, 2 for the answer]
(b) n = 55, φ(n) = 40, d = 3⁻¹ mod 40 = **27** (3·27 = 81 = 2·40 + 1). c = 9³ mod 55 = 729 − 13·55 = **14**. Dec(14) = 14^27 mod 55 = **9**. [1 each]
(c) Any one of: deterministic (equal plaintexts give equal ciphertexts, so it is not IND-CPA); malleable (c·2^e decrypts to 2m); a small m with e = 3 can be recovered by an integer cube root. Use OAEP or a KEM instead. [2]

## Q2 - Short explanation (8 marks)
A developer stores the GCM nonce in a config file and reuses it after every restart. Explain what an attacker who records traffic learns (a) about confidentiality and (b) about integrity. Name the remedy.

**Model answer.**
(a) Same key and same nonce means the same keystream, so c₁ ⊕ c₂ = m₁ ⊕ m₂. Known or guessable plaintext reveals the other message. [3]
(b) Two messages under one nonce let the attacker solve for the GHASH authentication key and then forge tags for new ciphertexts (L300 #15). [3]
Remedy: unique nonces per key, using a persistent counter or a random 96-bit nonce within the 2^32-message budget, or rotating or deriving keys per session. [2]

## Q3 - Prediction (8 marks)
Predict the IND-CPA advantage of the equality adversary (query Enc(m₀), compare with the challenge) against (a) AES-GCM with a fixed nonce and (b) AES-GCM with random nonces. Then predict the outcome of the bit-flip IND-CCA adversary against (c) AES-CTR without a MAC and (d) AES-GCM. Justify each prediction in one line.

**Model answer.** (lab: labs/L500/25-security-definitions)
(a) **1** - with a fixed nonce, encryption is deterministic.
(b) **≈ 0** - fresh nonces make ciphertexts differ, so equality never helps.
(c) **1** - flipping a ciphertext bit flips the same plaintext bit, and the decryption oracle returns the modified plaintext.
(d) **≈ 0** - the tag check rejects the modified ciphertext, so the adversary has to guess.
[2 each: 1 for the prediction, 1 for the reason]

## Q4 - Calculation (8 marks)
A service assigns **random 64-bit request IDs** and issues 2^30 of them. (a) Give the union-bound estimate of the probability of a duplicate. (b) Give the exponential lower bound. (c) Recommend a fix.

**Model answer.**
(a) q(q−1)/(2N) ≈ 2^60/2^65 = 2^−5 ≈ **0.031**. [3]
(b) 1 − exp(−q(q−1)/(2N)) ≈ **0.0308**, so a duplicate is about 3 % likely. [3]
(c) Use 128-bit random IDs (about 2^−69 at the same count), or a counter scoped per issuer. [2]

## Q5 - Design critique (10 marks)
Critique this login design and propose fixes, naming the lesson each fix comes from:
"Passwords are stored as SHA-256(password). Session tokens are `str(random.random())`. API tokens are JWTs and the server accepts the algorithm named in the token header."

**Model answer.**
- **Fast unsalted hash.** Identical passwords collide, rainbow tables apply and GPUs can guess billions of passwords per second. Fix: Argon2id with a per-user salt and tuned memory cost (L100 #5). [3]
- **`random.random()` is a predictable PRNG.** An attacker can predict other users' tokens. Fix: `secrets.token_urlsafe(32)` (L100 #3). [3]
- **Header-chosen algorithm.** This allows `alg: none` or HS/RS confusion. Fix: the verifier pins the algorithm and the key, and checks exp/aud/iss (L200 #11). [3]
- Overall: there is no threat model. [1]

## Q6 - Proof (8 marks)
Prove that if gcd(a, n) = 1, then x ↦ a·x mod n is a permutation of the set U of residues coprime to n. Then use this to prove Euler's theorem.

**Model answer.**
- Closure: a·x is coprime to n because no prime factor of n divides a or x. [2]
- Injective: if ax ≡ ay, multiplying by a⁻¹ (which exists because gcd = 1, by Bézout) gives x ≡ y. [2]
- A finite injective map from U to U is a permutation. [1]
- Euler: the product of a·x over U is congruent to the product of x over U, so a^φ(n)·∏x ≡ ∏x. Since ∏x is invertible, a^φ(n) ≡ 1. [3]

## Q7 - Short explanation (8 marks)
Explain why textbook RSA signatures (σ = m^d mod n) are not EUF-CMA secure, giving two different forgeries. Then explain why Ed25519 (L200 #7) and RSA-PSS do not suffer from them.

**Model answer.**
- **No-message forgery:** pick σ and publish m = σ^e. [2]
- **Multiplicative forgery:** σ₁σ₂ is a valid signature on m₁m₂ (lab: σ₆·σ₇ signs 42). [2]
- **Ed25519** hashes the message with a nonce derived from the key, and its verification equation has no exploitable algebraic structure on m. [2]
- **RSA-PSS** hashes and randomly pads, so multiplying signatures does not produce a valid encoding of any chosen message. In the lab, the product of two PSS signatures was rejected. [2]
