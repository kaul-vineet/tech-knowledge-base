"""Numerical checks for the lesson-24 results: birthday upper/lower bounds, the 50 % threshold, the
96-bit nonce budget, entropy inequalities and negligible functions. Deterministic output: simulations use
random.Random(24) (a simulation, not key material); the os.urandom check prints a count that is 0 with
probability 1 - 2^-57.
Run: python theorem_checks.py
"""
import math
import os
import random
from fractions import Fraction

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from prob_tools import (collision_exact, collision_lower, collision_upper, min_entropy, q_for_probability,
                        shannon_entropy)

R = random.Random(24)


def exact_fraction(q: int, n: int) -> Fraction:
    none = Fraction(1)
    for i in range(q):
        none *= Fraction(n - i, n)
    return 1 - none


def t24_1() -> None:
    cases = [(n, q) for n in (365, 2**16, 2**32) for q in (2, 10, 23, 100, 300, 1000, 10**4, 10**5) if q <= n]
    ok = sum(collision_exact(q, n) <= collision_upper(q, n) + 1e-15 for n, q in cases)
    print("[T24.1] Union bound P[collision] <= q(q-1)/(2N)")
    print(f"exact <= bound in {ok}/{len(cases)} (N, q) cases; N = 365, q = 23: exact {float(exact_fraction(23, 365)):.6f}, "
          f"bound {collision_upper(23, 365):.6f}")
    print(f"96-bit nonces, q = 2^32: bound = 2^{math.log2(collision_upper(2**32, 2**96)):.2f}")


def t24_2() -> None:
    cases = [(n, q) for n in (365, 2**16, 2**32) for q in (2, 10, 23, 100, 300, 1000, 10**4, 10**5) if q <= n]
    ok = sum(collision_lower(q, n) <= collision_exact(q, n) + 1e-15 for n, q in cases)
    q50 = next(q for q in range(1, 400) if exact_fraction(q, 365) >= Fraction(1, 2))
    n32 = 2**32
    q50_32 = next(q for q in range(77000, 78000) if collision_exact(q, n32) >= 0.5)
    trials, q, n = 2000, 4096, 2**24
    hits = sum(len({R.randrange(n) for _ in range(q)}) < q for _ in range(trials))
    print("[T24.2] Lower bound P >= 1 - exp(-q(q-1)/(2N)) and the 50 % threshold q ~ 1.1774 sqrt(N)")
    print(f"lower <= exact in {ok}/{len(cases)} cases")
    print(f"N = 365: first q with P >= 1/2 is {q50} (formula {q_for_probability(0.5, 365):.2f})")
    print(f"N = 2^32: first q with P >= 1/2 is {q50_32} (formula {q_for_probability(0.5, n32):.0f})")
    print(f"simulation N = 2^24, q = 4096, {trials} trials: observed {hits / trials:.3f}, predicted {collision_lower(q, n):.3f}")


def t24_3() -> None:
    n96 = 2**96
    p32 = collision_exact(2**32, n96)
    q_budget = q_for_probability(2**-32, n96)
    nonces = {os.urandom(12) for _ in range(2**20)}
    nonce = os.urandom(12)
    overhead = len(AESGCM(AESGCM.generate_key(bit_length=256)).encrypt(nonce, b"hello", None)) - len(b"hello")
    print("[T24.3] Nonce budget for 96-bit random nonces under one key")
    print(f"P[collision] after 2^32 messages = {p32:.4e} = 2^{math.log2(p32):.2f}")
    print(f"messages for risk 2^-32 = {q_budget:.4e} = 2^{math.log2(q_budget):.2f}; risk 1/2 at 2^{math.log2(q_for_probability(0.5, n96)):.2f}")
    print(f"collisions among 2^20 os.urandom(12) nonces: {2**20 - len(nonces)} | pyca AES-GCM: {len(nonce) * 8}-bit nonce, {overhead}-byte tag")


def t24_4() -> None:
    ok = 0
    for _ in range(1000):
        k = R.randrange(2, 64)
        w = [R.random() for _ in range(k)]
        p = [x / sum(w) for x in w]
        ok += min_entropy(p) <= shannon_entropy(p) + 1e-12 <= math.log2(k) + 2e-12
    pin = [0.1] + [0.9 / 9999] * 9999
    poly_negl = next(n for n in range(1, 5000) if all(m**10 * 2.0**-m < m**-3 for m in range(n, 5000)))
    print("[T24.4] H_min <= H <= log2|X| (equality iff uniform); poly * negligible is negligible")
    print(f"random distributions satisfying both inequalities: {ok}/1000")
    print(f"uniform 2^128: H = H_min = {min_entropy([2.0**-128]):.0f} bits | PIN with P('1234') = 0.1: "
          f"H = {shannon_entropy(pin):.2f}, H_min = {min_entropy(pin):.2f} bits")
    print(f"n^10 * 2^-n < n^-3 for every n >= {poly_negl} (checked to 5000); 1/n^3 is not negligible (n^4 * n^-3 = n grows)")
    print(f"2^40 queries, 2^-128 per query: union bound 2^{math.log2(2**40 * 2.0**-128):.0f}")


if __name__ == "__main__":
    t24_1()
    t24_2()
    t24_3()
    t24_4()
