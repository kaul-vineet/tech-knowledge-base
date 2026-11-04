# Reading seminar: Shannon (1949) and Diffie & Hellman (1976)

## Why read the originals
Textbooks give you the cleaned-up results. The originals show you the questions their authors faced, the assumptions they chose, and the predictions they got right and wrong. Both papers are short enough to read in an afternoon, and together they frame the whole course. Shannon tells you what secrecy costs if the attacker has unlimited computing power. Diffie and Hellman show how to escape that cost by betting on computational hardness. We link to copies hosted by an author and a university course page and summarise them. We do not reproduce them.

## Shannon, "Communication Theory of Secrecy Systems" (BSTJ, 1949)
**Problem.** Shannon wanted a mathematical theory of "true" secrecy systems, where the enemy can intercept everything and knows the system in use but not the key.

**Model.** He treated a secrecy system as a **family of transformations**, one per key, with prior probabilities on keys and messages. Cryptanalysis is then the computation of posterior probabilities. His assumption that the enemy knows the system is the ancestor of the open-design principle behind every game in lesson 25.

**Results to look for.**
- **Perfect secrecy** means posteriors equal priors. It is possible, but with finitely many messages it needs at least as many keys (lesson 25, T25.1).
- **Redundancy** in a language lets a cryptanalyst narrow the possible messages as more ciphertext arrives.
- **Equivocation** measures the uncertainty that remains. The **unicity distance**, roughly H(K)/D, estimates how much ciphertext makes the solution unique. His example is simple substitution at about 30 letters.
- **Practical secrecy** is the amount of work needed to find that unique solution. That is the opening modern computational cryptography walks through.

**Reading tip.** Re-derive one of his numbers yourself. log₁₀ 26! is 26.6, not the "about 20" in the paper, so the unicity estimate moves from about 30 to about 38 letters (problem 27-P3). Checking numbers is part of reading critically. Notice that the conclusion survives the correction.

## Diffie & Hellman, "New Directions in Cryptography" (IEEE Trans. IT, 1976)
**Problem.** Conventional cryptography needs a secure channel to deliver keys in advance. With n users there are (n² − n)/2 possible pairs. Business also needs a digital equivalent of a written signature.

**Two proposals.**
- **Public key cryptosystems.** Separate enciphering and deciphering keys, where the deciphering key is infeasible to compute from the enciphering key.
- **Public key distribution systems.** Two parties agree on a key over a public channel. Their construction uses Y = α^X mod q, with K = α^(XᵢXⱼ) computed by each side from the other's public value.

**Security claim.** Computing K appears to require a discrete logarithm. They state openly that they have **no proof** that the system is secure if logs are hard, and they estimate about 2^100 operations for a 200-bit q against 400 multiplications for users.

**Also in the paper.**
- The **one-way authentication** problem, which became digital signatures.
- A classification of ciphertext-only, known-plaintext and chosen-plaintext attacks.
- One-way functions and **trap doors**, the idea RSA realised a year later.
- A requirement that the public key file be protected from modification, an early form of what PKI provides.

**Reading tip.** Compare their threat list with lesson 25. Chosen-ciphertext attacks and active man-in-the-middle attacks on the key exchange are not yet in focus. That is why modern protocols authenticate the transcript (L200 #9-#10) and derive keys with a KDF (L200 #8).

## Connecting the two
Shannon shows that unconditional secrecy is expensive. Diffie and Hellman cite the one-time pad's information-theoretic basis and choose computational security instead: systems "secure due to the computational cost of cryptanalysis". Lessons 23-25 sit between them:
- number theory supplies the hard problems;
- probability turns "infeasible" into budgets;
- security games replace "the enemy's posterior" with "the adversary's advantage".

## How to write the critical response
1. Summarise in your own words. Short quotations need page or section references, and long passages are not allowed.
2. Pick one claim and test it against later knowledge: index calculus, Shor's algorithm, IND-CCA or authenticated key exchange.
3. Connect it to a system you used: AES-GCM, X25519, Ed25519 or ML-KEM.
4. Take a position and argue it. Then state what evidence would change your mind.
