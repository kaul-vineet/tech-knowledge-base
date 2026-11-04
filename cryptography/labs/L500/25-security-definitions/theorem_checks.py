"""Numerical checks for the lesson-25 results: OTP perfect secrecy (and the key-length bound), deterministic
encryption is not IND-CPA, the Encrypt-then-MAC reduction and IND-CCA, baby-step giant-step and toy LWE.
Deterministic output: challenger coins / adversary guesses / instances come from random.Random(2500).
Run: python theorem_checks.py
"""
import math
import os
import random
from fractions import Fraction

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import mlkem, padding, rsa

from games import (Q_LWE, bsgs, composed_scheme, ctr_scheme, ecb_scheme, etm_reduction, gcm_scheme, lwe_instance,
                   posterior_table, regev_bits, run_ind_cca_bitflip, run_ind_cpa, safe_prime, solve_mod,
                   textbook_rsa_forgeries)

R = random.Random(2500)


def t25_1() -> None:
    prior = {m: Fraction(m + 1, 36) for m in range(8)}  # deliberately non-uniform prior on 3-bit messages
    otp = posterior_table(3, 3, prior)
    short = posterior_table(3, 2, prior)
    leak = sum(v != prior[m] for (m, _), v in short.items())
    m1, m2 = b"meet at the gate", b"bring the ledger"
    pad = os.urandom(16)
    c1, c2 = bytes(a ^ k for a, k in zip(m1, pad)), bytes(a ^ k for a, k in zip(m2, pad))
    print("[T25.1] One-time pad: Pr[M = m | C = c] = Pr[M = m]; perfect secrecy needs |K| >= |M|")
    print(f"3-bit OTP, non-uniform prior: posterior = prior for {sum(v == prior[m] for (m, _), v in otp.items())}/64 (m, c) pairs")
    print(f"2-bit key on 3-bit messages: {leak} of {len(short)} possible (m, c) pairs have posterior != prior; "
          f"e.g. Pr[M=7 | C=7] = {short[(7, 7)]} vs prior {prior[7]}")
    print("pad reused: c1 XOR c2 == m1 XOR m2:", bytes(a ^ b for a, b in zip(c1, c2)) == bytes(a ^ b for a, b in zip(m1, m2)))


def t25_2() -> None:
    print("[T25.2] Deterministic (or nonce-reusing) encryption has IND-CPA advantage 1")
    for name, mk in [("AES-ECB (deterministic)", ecb_scheme), ("AES-GCM fixed nonce", lambda: gcm_scheme(True)),
                     ("Encrypt-and-MAC (tag on m)", lambda: composed_scheme("E&M")),
                     ("AES-GCM random nonce", gcm_scheme), ("Encrypt-then-MAC", lambda: composed_scheme("EtM"))]:
        print(f"  {name:28s} advantage {run_ind_cpa(mk, 1000, R):.3f} (1000 games)")


def t25_3() -> None:
    wins_a, wins_b = etm_reduction(2560, seed=2525)
    print("[T25.3] Encrypt-then-MAC: Adv_INT-CTXT(A) <= Adv_EUF-CMA(B), and IND-CPA + INT-CTXT => IND-CCA")
    print(f"1-byte tags, 2560 trials: A forges EtM {wins_a} times, B (running A) forges the MAC {wins_b} times; "
          f"equal: {wins_a == wins_b}; expected about 2560/256 = {2560 // 256}")
    for name, mk, t in [("AES-CTR (no MAC)", ctr_scheme, 0), ("AES-GCM", gcm_scheme, 16),
                        ("Encrypt-then-MAC", lambda: composed_scheme("EtM"), 32)]:
        print(f"  IND-CCA bit-flip adversary vs {name:18s} advantage {run_ind_cca_bitflip(mk, t, 1000, R):.3f}")


def t25_4() -> None:
    print("[T25.4] Hardness: BSGS solves discrete log in O(sqrt(q)); LWE without error is linear algebra")
    for qbits in (16, 20, 24, 28):
        p, q = safe_prime(qbits, R)
        x = R.randrange(1, q)
        found, ops = bsgs(4, pow(4, x, p), p, q)  # 4 = 2^2 generates the order-q subgroup
        bound = 2 * (math.isqrt(q - 1) + 1)
        print(f"  q ~ 2^{qbits}: recovered x: {found == x}, group ops {ops} <= 2*ceil(sqrt(q)) = {bound}: {ops <= bound}")
    s, a, b = lwe_instance(16, 16, 0, R)
    s2, a2, b2 = lwe_instance(16, 16, 2, R)
    print(f"  q = {Q_LWE}, n = 16: error 0 -> elimination recovers s: {solve_mod(a, b) == s}; "
          f"error in [-2, 2] -> recovers s: {solve_mod(a2, b2) == s2}")
    print(f"  toy Regev, m = 32 samples: decryption errors {regev_bits(16, 32, 2, 1000, R)}/1000 bits with |e| <= 2, "
          f"{regev_bits(16, 32, 300, 1000, R)}/1000 with |e| <= 300 (threshold q/4 = {Q_LWE // 4})")
    sk = mlkem.MLKEM768PrivateKey.generate()
    ss, ct = sk.public_key().encapsulate()
    print(f"  pyca ML-KEM-768: encapsulation key {len(sk.public_key().public_bytes_raw())} B, ciphertext {len(ct)} B, "
          f"shared secret {len(ss)} B, decapsulates: {sk.decapsulate(ct) == ss}")


def demos() -> None:
    a, b = textbook_rsa_forgeries(3233, 17, 2753, R, 100)
    k = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pub, n = k.public_key(), k.public_key().public_numbers().n
    pss = padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH)
    s1, s2 = (int.from_bytes(k.sign(m, pss, hashes.SHA256()), "big") for m in (b"pay 10", b"pay 20"))
    forged = (s1 * s2 % n).to_bytes(256, "big")
    try:
        pub.verify(forged, b"pay 10pay 20", pss, hashes.SHA256())
        pss_ok = True
    except InvalidSignature:
        pss_ok = False
    print("[D25] EUF-CMA: textbook RSA signatures vs RSA-PSS")
    print(f"textbook RSA n = 3233: no-message forgeries accepted {a}/100, multiplicative (2 oracle queries) {b}/100")
    print(f"pyca RSA-PSS 2048: product of two signatures accepted: {pss_ok}")


if __name__ == "__main__":
    t25_1()
    t25_2()
    t25_3()
    t25_4()
    demos()
