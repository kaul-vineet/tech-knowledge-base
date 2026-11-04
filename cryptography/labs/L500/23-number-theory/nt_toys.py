"""Number theory for cryptography, built from scratch: extended Euclid, inverses, CRT, Miller-Rabin,
TEXTBOOK RSA and TEXTBOOK Diffie-Hellman.

*** LEARNING TOYS - INSECURE - NEVER USE FOR REAL DATA ***
Textbook RSA has no padding (deterministic, malleable); textbook DH here has no authentication, no
key derivation and no constant-time arithmetic. Real code: pyca/cryptography RSA-OAEP / RSA-PSS,
X25519 + HKDF, or ML-KEM (L100-L400 lessons).
Run: python nt_toys.py
"""
import secrets


def egcd(a: int, b: int) -> tuple[int, int, int]:
    """Return (g, x, y) with a*x + b*y = g = gcd(a, b) (iterative extended Euclid)."""
    old_r, r, old_x, x, old_y, y = a, b, 1, 0, 0, 1
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_x, x = x, old_x - q * x
        old_y, y = y, old_y - q * y
    return old_r, old_x, old_y


def modinv(a: int, m: int) -> int:
    g, x, _ = egcd(a % m, m)
    if g != 1:
        raise ValueError(f"{a} has no inverse mod {m} (gcd {g})")
    return x % m


def crt(residues: list[int], moduli: list[int]) -> int:
    """The unique x mod prod(moduli) with x = r_i (mod m_i); moduli must be pairwise coprime."""
    n = 1
    for m in moduli:
        n *= m
    x = 0
    for r, m in zip(residues, moduli):
        ni = n // m
        x += r * ni * modinv(ni, m)
    return x % n


def is_probable_prime(n: int, rounds: int = 40) -> bool:
    """Miller-Rabin. Error probability <= 4**-rounds for composite n (random bases)."""
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d, s = d // 2, s + 1
    for _ in range(rounds):
        a = 2 + secrets.randbelow(n - 3)
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def random_prime(bits: int) -> int:
    while True:
        c = secrets.randbits(bits) | (1 << (bits - 1)) | 1  # top bit set, odd
        if is_probable_prime(c):
            return c


# ---------- TEXTBOOK RSA (insecure toy) ----------
def rsa_keygen(bits: int = 1024, e: int = 65537) -> dict:
    while True:
        p, q = random_prime(bits // 2), random_prime(bits // 2)
        phi = (p - 1) * (q - 1)
        if p != q and egcd(e, phi)[0] == 1:
            return {"n": p * q, "e": e, "d": modinv(e, phi), "p": p, "q": q}


def rsa_encrypt(m: int, pub: dict) -> int:
    return pow(m, pub["e"], pub["n"])


def rsa_decrypt(c: int, key: dict) -> int:
    return pow(c, key["d"], key["n"])


def rsa_decrypt_crt(c: int, key: dict) -> int:
    """Same result as rsa_decrypt, via two half-size exponentiations recombined with CRT."""
    p, q, d = key["p"], key["q"], key["d"]
    mp, mq = pow(c, d % (p - 1), p), pow(c, d % (q - 1), q)
    return crt([mp, mq], [p, q])


# ---------- TEXTBOOK DIFFIE-HELLMAN (insecure toy) ----------
def dh_keypair(p: int, g: int) -> tuple[int, int]:
    x = 2 + secrets.randbelow(p - 3)
    return x, pow(g, x, p)


def dh_shared(their_public: int, my_secret: int, p: int) -> int:
    return pow(their_public, my_secret, p)


def main() -> None:
    print("1) egcd(240, 46) =", egcd(240, 46), "| modinv(17, 3120) =", modinv(17, 3120))
    print("2) crt([2, 3, 2], [3, 5, 7]) =", crt([2, 3, 2], [3, 5, 7]))
    key = rsa_keygen(1024)
    m = int.from_bytes(b"pay 100 EUR to Bob", "big")
    c = rsa_encrypt(m, key)
    print("3) textbook RSA round trip:", rsa_decrypt(c, key) == m, "| CRT decrypt agrees:", rsa_decrypt_crt(c, key) == m)
    print("   deterministic (same m -> same c):", rsa_encrypt(m, key) == c)
    # Malleability: anyone holding only the PUBLIC key turns E(m) into E(2m) without knowing m.
    c2 = (c * pow(2, key["e"], key["n"])) % key["n"]
    print("4) malleability: Dec(c * 2^e) == 2*m:", rsa_decrypt(c2, key) == 2 * m)
    p, g = 23, 5  # toy group from the problem set; real DH needs >= 2048-bit p or an elliptic curve
    a, A = dh_keypair(p, g)
    b, B = dh_keypair(p, g)
    print("5) toy DH (p=23, g=5) both sides agree:", dh_shared(B, a, p) == dh_shared(A, b, p))
    print("INSECURE LEARNING TOYS - use RSA-OAEP/PSS, X25519+HKDF or ML-KEM from pyca/cryptography in real code")


if __name__ == "__main__":
    main()
