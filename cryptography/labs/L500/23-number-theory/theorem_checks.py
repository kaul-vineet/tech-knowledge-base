"""Numerical checks for the lesson-23 theorems (Bezout, Euler/Fermat, CRT, RSA correctness) plus the
textbook-DH and malleability demonstrations. Output is deterministic: inputs come from random.Random(500)
(test inputs only, never key material) and only invariant facts are printed.
Run: python theorem_checks.py
"""
import math
import random
import warnings

from cryptography.hazmat.primitives.asymmetric import dh, rsa

from nt_toys import crt, egcd, modinv, rsa_decrypt, rsa_decrypt_crt, rsa_encrypt

R = random.Random(500)


def phi(n: int) -> int:
    """Euler's totient from the factorisation: n * prod(1 - 1/p) over primes p | n."""
    result, m, p = n, n, 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            result -= result // p
        p += 1
    return result - result // m if m > 1 else result


def t23_1() -> None:
    ok = inv_ok = 0
    for _ in range(5000):
        a, b = R.getrandbits(256) + 1, R.getrandbits(256) + 1
        g, x, y = egcd(a, b)
        ok += a * x + b * y == g == math.gcd(a, b)
        try:
            inv = modinv(a, b)
            inv_ok += g == 1 and (a * inv) % b == 1 % b
        except ValueError:
            inv_ok += g != 1
    print("[T23.1] Bezout / extended Euclid")
    print(f"a*x + b*y = gcd(a, b) = math.gcd(a, b): {ok}/5000 random 256-bit pairs")
    print(f"inverse exists exactly when gcd = 1 (and a*inv = 1 mod b): {inv_ok}/5000")
    print(f"egcd(240, 46) = {egcd(240, 46)} | modinv(17, 3120) = {modinv(17, 3120)}")


def t23_2() -> None:
    pairs = good = 0
    for n in range(2, 401):
        f = phi(n)
        for a in range(1, n):
            if math.gcd(a, n) == 1:
                pairs += 1
                good += pow(a, f, n) == 1
    primes = [p for p in range(2, 2000) if all(p % d for d in range(2, math.isqrt(p) + 1))]
    fermat = sum(pow(a, p - 1, p) == 1 for p in primes for a in (2, 3, 5, 7) if a % p)
    tests = sum(1 for p in primes for a in (2, 3, 5, 7) if a % p)
    # Carmichael number 561 = 3*11*17 fools the plain Fermat test - why Miller-Rabin is used instead
    print("[T23.2] Euler's theorem a^phi(n) = 1 (mod n) when gcd(a, n) = 1")
    print(f"exhaustive n = 2..400: {good}/{pairs} coprime pairs satisfy it")
    print(f"Fermat a^(p-1) = 1 (mod p), {len(primes)} primes < 2000, bases 2,3,5,7: {fermat}/{tests}")
    print(f"phi(3233) = {phi(3233)} = (61-1)*(53-1) = {60 * 52}; 2^560 mod 561 = {pow(2, 560, 561)} (561 is composite)")


def t23_3() -> None:
    images = {(x % 3, x % 5, x % 7) for x in range(105)}
    agree = sum(crt([x % 3, x % 5, x % 7], [3, 5, 7]) == x for x in range(105))
    k = rsa.generate_private_key(public_exponent=65537, key_size=2048).private_numbers()
    key = {"n": k.public_numbers.n, "e": k.public_numbers.e, "d": k.d, "p": k.p, "q": k.q}
    ms = [R.randrange(key["n"]) for _ in range(20)]
    same = sum(rsa_decrypt_crt(rsa_encrypt(m, key), key) == rsa_decrypt(rsa_encrypt(m, key), key) == m for m in ms)
    print("[T23.3] Chinese remainder theorem")
    print(f"x -> (x mod 3, x mod 5, x mod 7) on 0..104: {len(images)} distinct images (bijection onto 3*5*7 = 105)")
    print(f"crt() reconstructs x: {agree}/105 | crt([2, 3, 2], [3, 5, 7]) = {crt([2, 3, 2], [3, 5, 7])}")
    print(f"pyca 2048-bit key: CRT decryption = plain decryption = m for {same}/20 random m")
    print("pyca CRT parameters match ours: dmp1 =", k.dmp1 == k.d % (k.p - 1), "| dmq1 =", k.dmq1 == k.d % (k.q - 1),
          "| iqmp =", k.iqmp == modinv(k.q, k.p))


def t23_4() -> None:
    n, e, d = 3233, 17, 2753
    allm = sum(pow(pow(m, e, n), d, n) == m for m in range(n))
    shared = sum(1 for m in range(n) if math.gcd(m, n) > 1)
    k = rsa.generate_private_key(public_exponent=65537, key_size=2048).private_numbers()
    key = {"n": k.public_numbers.n, "e": k.public_numbers.e, "d": k.d}
    ms = [R.randrange(key["n"]) for _ in range(40)] + [k.p, 5 * k.q, 0, 1, key["n"] - 1]
    rt = sum(rsa_decrypt(rsa_encrypt(m, key), key) == m for m in ms)
    lam = math.lcm(k.p - 1, k.q - 1)
    print("[T23.4] RSA correctness m^(e*d) = m (mod n) for every m in Z_n")
    print(f"n = 3233 (61*53), e = 17, d = 2753: {allm}/3233 messages round-trip, incl. {shared} with gcd(m, n) > 1")
    print(f"pyca 2048-bit key (e = 65537): {rt}/45 round-trip (40 random + p, 5q, 0, 1, n-1)")
    print("pyca d satisfies e*d = 1 mod lcm(p-1, q-1):", (key["e"] * key["d"]) % lam == 1)


def demos() -> None:
    n, e, d = 3233, 17, 2753
    c = pow(65, e, n)
    c_mal = (c * pow(2, e, n)) % n
    print("[D23] textbook RSA malleability and textbook DH (insecure toys)")
    print(f"Enc(65) = {c}; attacker sends c * 2^e mod n = {c_mal}; Dec = {pow(c_mal, d, n)} (= 2 * 65)")
    print(f"Enc(6) * Enc(7) mod n decrypts to {pow(pow(6, e, n) * pow(7, e, n) % n, d, n)} (= 6 * 7)")
    p, g, a, b = 23, 5, 6, 15
    A, B = pow(g, a, p), pow(g, b, p)
    print(f"DH p=23 g=5 a=6 b=15: A = {A}, B = {B}, B^a = {pow(B, a, p)}, A^b = {pow(A, b, p)}")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        params = dh.generate_parameters(generator=2, key_size=512)  # 512-bit: demo size only, too small for real use
        x, y = params.generate_private_key(), params.generate_private_key()
        pyca = int.from_bytes(x.exchange(y.public_key()), "big")
        pn = params.parameter_numbers()
        ours = pow(y.public_key().public_numbers().y, x.private_numbers().x, pn.p)
    print("pyca FFDH exchange == our pow(Y, x, p):", pyca == ours,
          "| pyca 50.0.2 warns FFDH deprecated:", any("deprecated" in str(i.message) for i in w))


if __name__ == "__main__":
    t23_1()
    t23_2()
    t23_3()
    t23_4()
    demos()
