# Foundations III: security definitions, games and reductions

## Why it matters
"Is this encryption secure?" has no answer until you say **against whom** and **what counts as winning**. Modern cryptography answers with games. A challenger runs the scheme, an adversary interacts through well-defined oracles, and security means every efficient adversary's **advantage** is negligible. The games explain the rules from L100-L400, such as "never reuse a nonce", "always authenticate before decrypting" and "don't sign raw RSA", as consequences rather than folklore. They also tell you exactly what a proof does and does not promise.

## Definitions
- **Perfect secrecy** (Shannon): Pr[M = m | C = c] = Pr[M = m] for all m and c.
- **Advantage**: Adv(A) = |Pr[A outputs 1 in experiment 1] − Pr[A outputs 1 in experiment 0]|.
- **IND-CPA**: A may query Enc on any messages. It submits m₀ and m₁ of equal length and receives Enc(m_b), and must guess b.
- **IND-CCA**: the same game plus a decryption oracle for every ciphertext except the challenge.
- **INT-CTXT**: A wins if it outputs a new ciphertext that decrypts.
- **EUF-CMA**: A receives signatures on messages of its choice and wins with a valid signature on a message it never queried.
- **Reduction**: an algorithm B that turns any adversary A against scheme S into a solver for problem P. It proves "P hard ⇒ S secure", with the loss quantified.

## Key results
1. **One-time pad (T25.1).** C = M ⊕ K with uniform K is perfectly secret. Perfect secrecy forces |K| ≥ |M|, because if some message cannot decrypt from c, its posterior probability drops to 0.
2. **Determinism kills IND-CPA (T25.2).** If Enc is deterministic, an adversary queries Enc(m₀) and compares it with the challenge, giving advantage 1. This covers ECB, GCM with a fixed nonce and Encrypt-and-MAC (whose tag MAC(m) repeats).
3. **Encrypt-then-MAC (T25.3).** An INT-CTXT attacker A yields a MAC forger B: B simulates encryption with its own key and forwards A's forgery. Any new valid ciphertext carries a MAC on a never-queried string. INT-CTXT plus IND-CPA gives IND-CCA (Bellare & Namprempre).
4. **Hardness has a price (T25.4).** Baby-step giant-step solves discrete log in a group of order q with ≤ 2⌈√q⌉ operations. Shoup (1997) showed generic algorithms cannot do better, so 256-bit curves give ~128-bit security. LWE (behind ML-KEM, FIPS 203) is linear algebra made hard by small noise.

## Intuition
A security definition is a **contract** listing what the attacker may do. IND-CPA lets the attacker get its own messages encrypted, which is realistic whenever users can make a server encrypt their input. IND-CCA also lets it see decryptions of tampered ciphertexts, which is realistic whenever error messages or behaviour differ. EUF-CMA says seeing signatures must not help forge new ones.

A reduction is a **contrapositive with a simulator**. If you could break the scheme, I could use you as a subroutine to break something everyone believes is hard. The proof is only as good as that belief and the simulation.

## Worked example (lab output, labs/L500/25-security-definitions)
- **OTP.** With a non-uniform prior on 3-bit messages, the posterior equals the prior for 64/64 (m, c) pairs. Shorten the key to 2 bits and all 32 possible pairs leak: Pr[M = 7 | C = 7] = 4/13 against a prior of 2/9. Reusing a pad gives c₁ ⊕ c₂ = m₁ ⊕ m₂: True.
- **IND-CPA (1000 games).** AES-ECB 1.000, AES-GCM with a fixed nonce 1.000, Encrypt-and-MAC 1.000, AES-GCM with a random nonce 0.000, Encrypt-then-MAC 0.000.
- **IND-CCA bit-flip adversary.** AES-CTR without a MAC 1.000 (flipping a ciphertext bit flips the plaintext bit, and the oracle happily decrypts). AES-GCM 0.002 and EtM 0.015, which is pure guessing noise because the oracle refuses tampered ciphertexts.
- **Reduction, run as code.** With 1-byte tags over 2560 trials, A forges EtM 12 times and B, running A inside its MAC game with the same coins, forges the MAC 12 times. The expectation is 2560/256 = 10. Equal counts show the simulation is exact.
- **EUF-CMA.** Textbook RSA signatures (n = 3233) accept 100/100 no-message forgeries (pick σ, publish m = σ^e). They also accept multiplicative forgeries from two oracle queries (σ₆·σ₇ signs 42). pyca RSA-PSS rejects the product of two signatures.
- **Hardness.** BSGS recovers x in groups of order ≈ 2^16 … 2^28 with ≤ 2⌈√q⌉ operations each. LWE with q = 3329 and n = 16: Gaussian elimination recovers s exactly without noise and fails with noise in [−2, 2]. Toy Regev decryption has 0/1000 errors when |e| ≤ 2 and 122/1000 when |e| ≤ 300, against a q/4 = 832 threshold. pyca ML-KEM-768 has a 1184-byte encapsulation key, a 1088-byte ciphertext and a 32-byte shared secret.

## Why AEAD composition matters
Encrypt-and-MAC leaks plaintext equality. MAC-then-Encrypt makes the receiver decrypt before checking, so padding and timing differences turn the receiver into a decryption oracle. Encrypt-then-MAC checks first and drops forgeries, and its proof reduces to MAC unforgeability. AEAD modes (GCM, ChaCha20-Poly1305) package this structure plus associated data, which is why the course uses them everywhere.

## Common misconceptions
- **"Secure means the key can't be recovered."** IND-CPA is broken long before key recovery. Learning one bit about the plaintext, or whether two messages are equal, counts as a break.
- **"A proof means it's unbreakable."** A proof is relative to a model (oracles, no side channels), an assumption (DL, LWE, PRP) and concrete losses. Implementations can still leak through timing or misuse (L300 #15).
- **"Encryption gives integrity."** CTR mode is perfectly IND-CPA and completely malleable.
- **"OTP is the gold standard to aim for."** It requires a key as long as all traffic, used once, plus a separate integrity mechanism. Practical systems trade perfect secrecy for computational security.
- **"LWE is hard because the matrix is big."** Without noise it is easy linear algebra. The **noise** creates the hardness, and parameters must keep decryption noise below q/4.
