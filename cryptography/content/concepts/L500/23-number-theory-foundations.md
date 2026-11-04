# Foundations I: number theory for public-key cryptography

## Why it matters
Every public-key operation you ran in L200-L400 — an RSA certificate, an X25519 handshake, a signature check — is arithmetic in Z_n or in a group built on it. Libraries hide the arithmetic, which is right for production code. When you review a design, though, you need to know **why** decryption returns the plaintext, **which** algebraic facts an attacker can exploit, and **what** a "hardness assumption" actually assumes. This lesson proves the four facts RSA rests on. It then builds textbook RSA and Diffie-Hellman from scratch, as toys, so you can watch correctness and insecurity happen side by side.

## Definitions
- **Z_n** is the set {0, …, n−1} with + and × taken mod n. We write a ≡ b (mod n) when n divides a − b.
- **gcd(a, b)** is the largest integer dividing both. a and b are **coprime** when gcd = 1.
- The **modular inverse** a⁻¹ mod n is the x with ax ≡ 1 (mod n).
- **Euler's totient** φ(n) counts the residues coprime to n. For distinct primes p, q: φ(pq) = (p−1)(q−1). The **Carmichael function** λ(pq) = lcm(p−1, q−1) divides φ(n).
- **Textbook RSA**: public (n, e), private d with ed ≡ 1 (mod λ(n)). Enc(m) = m^e mod n, Dec(c) = c^d mod n.
- **Textbook DH**: public prime p and generator g. Alice sends A = g^a, Bob sends B = g^b, and both compute g^(ab).

## Key results
1. **Bézout / extended Euclid (T23.1).** The algorithm keeps the invariant r = a·x + b·y while it runs Euclid's remainders. It ends with ax + by = gcd(a, b). So a is invertible mod m exactly when gcd(a, m) = 1, and the inverse costs O(log m) steps.
2. **Euler's theorem (T23.2).** If gcd(a, n) = 1 then a^φ(n) ≡ 1. Proof idea: multiplying all reduced residues by a only permutes them. Fermat's little theorem is the case n = p. The converse is false: 561 passes the Fermat test for base 2 but is composite. That is why key generation uses Miller-Rabin.
3. **CRT (T23.3).** Residues modulo pairwise-coprime moduli determine a unique residue modulo their product, and the map respects + and ×. You can compute "mod n" as "mod p and mod q" and recombine.
4. **RSA correctness (T23.4).** For every m in Z_n, m^(ed) ≡ m (mod n). Prove it mod p and mod q separately, using Fermat when the prime does not divide m and the trivial 0 ≡ 0 when it does. Then glue the two results with the CRT. The case gcd(m, n) > 1 is exactly where "just apply Euler mod n" fails.

## Intuition
Think of Z_n as a clock with n hours. Multiplying by a coprime a shuffles the hours without collisions, which is the heart of Euler's theorem. The CRT says a clock with pq hours behaves like a pair of clocks with p and q hours ticking together. RSA's trapdoor is that **you** know the two small clocks (p and q), so you can compute λ(n) and d. Everyone else sees only the big clock, and recovering d from (n, e) is as hard as factoring n.

## Worked example (lab output, labs/L500/23-number-theory)
Take p = 61, q = 53, so n = 3233 and φ(n) = 3120. Extended Euclid on (3120, 17) gives 17⁻¹ = 2753 = d. Encrypting m = 65 gives c = 2790.

The check runs **all 3233 messages** through encryption and decryption: 3233/3233 round-trip, including the 113 messages that share a factor with n. With a real 2048-bit key from pyca/cryptography 50.0.2, 45/45 test messages round-trip, including m = p and m = 5q. pyca's stored CRT values dmp1, dmq1 and iqmp equal d mod (p−1), d mod (q−1) and q⁻¹ mod p as computed by our code, and pyca's d satisfies ed ≡ 1 mod λ(n).

Then the insecurity, using only the public key. An attacker multiplies the ciphertext by 2^e: c' = 2790·2^17 mod 3233 = 3017. The key holder decrypts c' to **130 = 2·65**. Enc(6)·Enc(7) decrypts to 42. This is **malleability**, and the same algebra that proves correctness enables it.

Toy DH with p = 23, g = 5, a = 6, b = 15 gives A = 8, B = 19 and a shared key of 2 on both sides. The lab cross-checks the formula against pyca's finite-field DH on a 512-bit group: pow(Y, x, p) equals pyca's exchange output. pyca 50.0.2 also emits a deprecation warning for finite-field DH, which tells you the ecosystem has moved to X25519 and ML-KEM.

## What a numerical check proves (and does not)
An exhaustive check over n = 3233 is a **proof for that n** but not for all n. Random checks with 2048-bit keys catch implementation bugs but prove nothing in general. The general statement comes from the proof. The check guards against a wrong proof or a buggy implementation. Both together are the standard of this level.

## Common misconceptions
- **"RSA works because of Euler's theorem mod n."** Euler needs gcd(m, n) = 1. The full proof needs Fermat per prime plus the CRT.
- **"d must be computed mod φ(n)."** Any d with ed ≡ 1 mod λ(n) works. That d is smaller, it is what pyca and RFC 8017 use, and it gives the same results.
- **"If it decrypts correctly, it is secure."** Textbook RSA is correct and still deterministic (equal plaintexts give equal ciphertexts) and malleable (Enc(m) becomes Enc(2m)). With e = 3 and a small m it is even invertible by an integer cube root (42³ = 74088 < n). OAEP or a KEM fixes this. Lesson 25 makes "secure" precise.
- **"DH is secure because exponentiation is hard to undo."** That is only true in the right groups, against passive attackers. A man in the middle breaks unauthenticated DH without solving any discrete log (lesson 27).
- **"Passing the Fermat test means prime."** Carmichael numbers such as 561 fool it.

## Where this shows up later
CRT decryption (≈4× faster) appears in every RSA library. Inverses mod n appear in ECDSA and Ed25519 arithmetic. Discrete logarithms underlie X25519 (L200 #8). Shor's algorithm breaks exactly these number-theoretic problems, which motivates the LWE assumption in lesson 25 and ML-KEM in L400 #18.
