"""Security definitions as runnable games: perfect secrecy, IND-CPA, IND-CCA, EUF-CMA, the Encrypt-then-MAC
reduction, baby-step giant-step (discrete log) and a toy LWE (Regev) scheme.

*** TEACHING CODE - the weak schemes here (ECB, unauthenticated CTR, Encrypt-and-MAC, textbook RSA signatures,
toy LWE) exist to LOSE these games. Real code: AES-GCM / ChaCha20-Poly1305, Ed25519, ML-KEM (L100-L400). ***
The challenger's coin and the adversary's guesses come from a seeded random.Random so results are reproducible;
keys and nonces come from os.urandom. Run: python games.py
"""
import hashlib
import hmac
import math
import os
import random
from fractions import Fraction
from itertools import product

from cryptography.exceptions import InvalidSignature, InvalidTag
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# ---------- perfect secrecy ----------
def posterior_table(bits: int, key_bits: int, prior: dict) -> dict:
    """Pr[M = m | C = c] for c = m XOR k with k uniform on key_bits low bits (key_bits == bits is the OTP)."""
    joint = {}
    for m, k in product(range(2**bits), range(2**key_bits)):
        c = m ^ k
        joint[(m, c)] = joint.get((m, c), 0) + prior[m] * Fraction(1, 2**key_bits)
    pc = {}
    for (m, c), v in joint.items():
        pc[c] = pc.get(c, 0) + v
    return {(m, c): v / pc[c] for (m, c), v in joint.items()}


# ---------- schemes under test ----------
def ecb_scheme():
    key = os.urandom(32)
    def enc(m: bytes) -> bytes:  # deterministic: one AES block, no IV
        e = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
        return e.update(m) + e.finalize()
    return enc, None


def gcm_scheme(fixed_nonce: bool = False):
    aead, n0 = AESGCM(AESGCM.generate_key(bit_length=256)), os.urandom(12)
    def enc(m: bytes) -> bytes:
        n = n0 if fixed_nonce else os.urandom(12)
        return n + aead.encrypt(n, m, None)
    def dec(c: bytes) -> bytes:
        return aead.decrypt(c[:12], c[12:], None)
    return enc, dec


def ctr_scheme():
    key = os.urandom(32)
    def enc(m: bytes) -> bytes:
        n = os.urandom(16)
        e = Cipher(algorithms.AES(key), modes.CTR(n)).encryptor()
        return n + e.update(m) + e.finalize()
    def dec(c: bytes) -> bytes:
        d = Cipher(algorithms.AES(key), modes.CTR(c[:16])).decryptor()
        return d.update(c[16:]) + d.finalize()
    return enc, dec


def composed_scheme(order: str, tag_len: int = 32):
    """order = 'EtM' (tag over ciphertext) or 'E&M' (tag over plaintext). CTR + HMAC-SHA256, independent keys."""
    ctr_enc, ctr_dec = ctr_scheme()
    mk = os.urandom(32)
    mac = lambda data: hmac.new(mk, data, hashlib.sha256).digest()[:tag_len]
    def enc(m: bytes) -> bytes:
        c = ctr_enc(m)
        return c + (mac(c) if order == "EtM" else mac(m))
    def dec(ct: bytes) -> bytes:
        c, t = ct[:-tag_len], ct[-tag_len:]
        if order == "EtM":
            if not hmac.compare_digest(mac(c), t):
                raise InvalidTag
            return ctr_dec(c)
        m = ctr_dec(c)
        if not hmac.compare_digest(mac(m), t):
            raise InvalidTag
        return m
    return enc, dec, mac


# ---------- games ----------
M0, M1 = b"attack at dawn!!", b"retreat at dusk!"


def ind_cpa_equality_adversary(enc, b: int) -> int:
    """Query Enc(m0) itself, then compare with the challenge: whole ciphertext, or the last 32 bytes (a tag)."""
    seen = enc(M0)
    ch = enc(M1 if b else M0)
    return 0 if ch == seen or ch[-32:] == seen[-32:] else 1


def advantage(ones_exp1: int, ones_exp0: int, trials: int) -> float:
    """Adv = |Pr[A outputs 1 in experiment 1] - Pr[A outputs 1 in experiment 0]| (Boneh-Shoup style)."""
    return abs(ones_exp1 - ones_exp0) / trials


def run_ind_cpa(make_scheme, trials: int, rng: random.Random) -> float:
    enc = make_scheme()[0]
    ones = [sum(ind_cpa_equality_adversary(enc, b) for _ in range(trials)) for b in (0, 1)]
    return advantage(ones[1], ones[0], trials)


def run_ind_cca_bitflip(make_scheme, tag_len: int, trials: int, rng: random.Random) -> float:
    """Adversary flips one bit of the challenge body and asks the decryption oracle (allowed: c' != c)."""
    enc, dec = make_scheme()[:2]
    ones = [0, 0]
    for b in (0, 1):
        for _ in range(trials):
            ch = bytearray(enc(M1 if b else M0))
            ch[len(ch) - tag_len - 1] ^= 1  # last plaintext-carrying byte
            try:
                guess = 0 if dec(bytes(ch))[:15] == M0[:15] else 1
            except InvalidTag:
                guess = rng.randrange(2)  # oracle refused: the adversary learns nothing and guesses
            ones[b] += guess
    return advantage(ones[1], ones[0], trials)


def textbook_rsa_verify(m: int, sig: int, n: int, e: int) -> bool:
    return 0 <= m < n and pow(sig, e, n) == m


def textbook_rsa_forgeries(n: int, e: int, d: int, rng: random.Random, attempts: int) -> tuple[int, int]:
    """(a) no-message attack: pick sigma, set m = sigma^e. (b) chosen-message attack: sign m1, m2, output
    (m1*m2 mod n, s1*s2 mod n) - a message never queried. Returns accepted counts for (a) and (b)."""
    a = sum(textbook_rsa_verify(pow(s, e, n), s, n, e) for s in (rng.randrange(2, n) for _ in range(attempts)))
    b = 0
    for _ in range(attempts):
        m1, m2 = rng.randrange(2, n), rng.randrange(2, n)
        s1, s2 = pow(m1, d, n), pow(m2, d, n)  # the signing oracle
        m = m1 * m2 % n
        b += m not in (m1, m2) and textbook_rsa_verify(m, s1 * s2 % n, n, e)
    return a, b


def ed25519_forgery(rng: random.Random, attempts: int) -> int:
    pub = ed25519.Ed25519PrivateKey.generate().public_key()
    wins = 0
    for _ in range(attempts):
        try:
            pub.verify(rng.randbytes(64), b"forged message")
            wins += 1
        except InvalidSignature:
            pass
    return wins


def _etm_encrypt(ek: bytes, nonce: bytes, m: bytes, mac) -> bytes:
    e = Cipher(algorithms.AES(ek), modes.CTR(nonce)).encryptor()
    c = nonce + e.update(m) + e.finalize()
    return c + mac(c)


def etm_reduction(trials: int, seed: int, tag_len: int = 1) -> tuple[int, int]:
    """A forges against EtM (truncated tags) by guessing. B, given only a MAC oracle, runs A and simulates the
    encryption oracle itself. Keys, nonces and A's coins come from the same seeded streams in both experiments,
    so B's simulation is exactly A's real view: per-trial outcomes (and the counts) are identical."""
    def adversary_a(enc_oracle, rng):
        c = bytearray(enc_oracle(b"transfer 10 EUR")[:-tag_len])
        c[-1] ^= 0x01  # a ciphertext never returned by the oracle
        return bytes(c) + rng.randbytes(tag_len)

    def tagger(mk):
        return lambda d: hmac.new(mk, d, hashlib.sha256).digest()[:tag_len]

    keys_a, coins_a, wins_a = random.Random(seed), random.Random(seed + 1), 0
    for _ in range(trials):  # real INT-CTXT experiment: the challenger owns ek and mk
        ek, mk, nonce = keys_a.randbytes(32), keys_a.randbytes(32), keys_a.randbytes(16)
        mac = tagger(mk)
        forged = adversary_a(lambda m: _etm_encrypt(ek, nonce, m, mac), coins_a)
        wins_a += hmac.compare_digest(mac(forged[:-tag_len]), forged[-tag_len:])
    keys_b, coins_b, wins_b = random.Random(seed), random.Random(seed + 1), 0
    for _ in range(trials):  # EUF-CMA experiment: the challenger owns only mk; B picks ek and the nonce itself
        ek_b, mk, nonce_b = keys_b.randbytes(32), keys_b.randbytes(32), keys_b.randbytes(16)
        mac_oracle = tagger(mk)
        forged = adversary_a(lambda m: _etm_encrypt(ek_b, nonce_b, m, mac_oracle), coins_b)
        wins_b += hmac.compare_digest(mac_oracle(forged[:-tag_len]), forged[-tag_len:])  # unqueried data
    return wins_a, wins_b


# ---------- hardness: discrete log and LWE ----------
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d, s = d // 2, s + 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):  # deterministic for n < 3.3e24
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def safe_prime(qbits: int, rng: random.Random) -> tuple[int, int]:
    while True:
        q = rng.getrandbits(qbits) | (1 << (qbits - 1)) | 1
        if is_prime(q) and is_prime(2 * q + 1):
            return 2 * q + 1, q


def bsgs(g: int, h: int, p: int, order: int) -> tuple[int, int]:
    """Solve g^x = h (mod p) for x < order in O(sqrt(order)) multiplications. Returns (x, group operations)."""
    m = math.isqrt(order - 1) + 1
    table, e = {}, 1
    for j in range(m):
        table.setdefault(e, j)
        e = e * g % p
    factor, gamma = pow(g, -m, p), h
    for i in range(m):
        if gamma in table:
            return i * m + table[gamma], m + i + 1
        gamma = gamma * factor % p
    raise ValueError("no solution")


Q_LWE = 3329  # the ML-KEM modulus (FIPS 203)


def solve_mod(a_rows: list[list[int]], b: list[int], q: int = Q_LWE) -> list[int] | None:
    """Gaussian elimination mod prime q on a square system; None if singular."""
    n = len(a_rows)
    m = [row[:] + [bi] for row, bi in zip(a_rows, b)]
    for col in range(n):
        piv = next((r for r in range(col, n) if m[r][col] % q), None)
        if piv is None:
            return None
        m[col], m[piv] = m[piv], m[col]
        inv = pow(m[col][col], -1, q)
        m[col] = [v * inv % q for v in m[col]]
        for r in range(n):
            if r != col and m[r][col]:
                f = m[r][col]
                m[r] = [(vr - f * vc) % q for vr, vc in zip(m[r], m[col])]
    return [m[r][n] for r in range(n)]


def lwe_instance(n: int, samples: int, err: int, rng: random.Random):
    s = [rng.randrange(Q_LWE) for _ in range(n)]
    a = [[rng.randrange(Q_LWE) for _ in range(n)] for _ in range(samples)]
    e = [rng.randint(-err, err) for _ in range(samples)]
    b = [(sum(x * y for x, y in zip(row, s)) + ei) % Q_LWE for row, ei in zip(a, e)]
    return s, a, b


def regev_bits(n: int, samples: int, err: int, bits: int, rng: random.Random) -> int:
    """Encrypt `bits` random bits with toy Regev; return the number of decryption errors."""
    s, a, b = lwe_instance(n, samples, err, rng)
    errors = 0
    for _ in range(bits):
        mu = rng.randrange(2)
        r = [rng.randrange(2) for _ in range(samples)]
        u = [sum(r[i] * a[i][j] for i in range(samples)) % Q_LWE for j in range(n)]
        v = (sum(r[i] * b[i] for i in range(samples)) + mu * (Q_LWE // 2)) % Q_LWE
        d = (v - sum(x * y for x, y in zip(u, s))) % Q_LWE
        errors += int(Q_LWE // 4 < d < 3 * Q_LWE // 4) != mu
    return errors


def main() -> None:
    rng = random.Random(25)
    print("IND-CPA advantage (equality adversary, 400 games):")
    for name, mk in [("AES-ECB (deterministic)", ecb_scheme), ("AES-GCM random nonce", gcm_scheme),
                     ("AES-GCM fixed nonce", lambda: gcm_scheme(True)),
                     ("Encrypt-and-MAC", lambda: composed_scheme("E&M")), ("Encrypt-then-MAC", lambda: composed_scheme("EtM"))]:
        print(f"  {name:26s} {run_ind_cpa(mk, 400, rng):.3f}")
    print("IND-CCA advantage (bit-flip + decryption oracle, 400 games):")
    for name, mk, t in [("AES-CTR (no MAC)", ctr_scheme, 0), ("AES-GCM", gcm_scheme, 16),
                        ("Encrypt-then-MAC", lambda: composed_scheme("EtM"), 32)]:
        print(f"  {name:26s} {run_ind_cca_bitflip(mk, t, 400, rng):.3f}")
    a, b = textbook_rsa_forgeries(3233, 17, 2753, rng, 100)
    print(f"EUF-CMA textbook RSA (n = 3233): no-message forgeries accepted {a}/100, multiplicative {b}/100;",
          f"Ed25519 random signatures accepted {ed25519_forgery(rng, 100)}/100")


if __name__ == "__main__":
    main()
