"""Probability for cryptography: birthday bounds, nonce-collision risk, entropy and min-entropy.
Exact values use fractions/log-space so tiny probabilities (2^-33) are not lost to rounding.
Run: python prob_tools.py
"""
import math
from collections import Counter


def collision_exact(q: int, n: int) -> float:
    """P[some collision] among q independent uniform draws from n values (exact product, log-space)."""
    if q > n:
        return 1.0
    log_none = sum(math.log1p(-i / n) for i in range(q)) if q < 10**6 else _log_none_fast(q, n)
    return -math.expm1(log_none)


def _log_none_fast(q: int, n: int) -> float:
    # sum_{i<q} log(1 - i/n) = -sum_k (1/k) * S_k / n^k with S_k = sum_{i<q} i^k; first terms suffice when q << n
    s1 = q * (q - 1) / 2
    s2 = (q - 1) * q * (2 * q - 1) / 6
    return -(s1 / n + s2 / (2 * n * n))


def collision_upper(q: int, n: int) -> float:
    """Union bound: P <= q(q-1) / (2n)."""
    return q * (q - 1) / (2 * n)


def collision_lower(q: int, n: int) -> float:
    """From 1 - x <= e^-x: P >= 1 - exp(-q(q-1)/(2n))."""
    return -math.expm1(-q * (q - 1) / (2 * n))


def q_for_probability(p: float, n: int) -> float:
    """Draws needed for collision probability p (inverting the exponential approximation)."""
    return math.sqrt(2 * n * math.log(1 / (1 - p)))


def shannon_entropy(probs) -> float:
    return -sum(p * math.log2(p) for p in probs if p > 0)


def min_entropy(probs) -> float:
    return -math.log2(max(probs))


def empirical(samples) -> list[float]:
    c = Counter(samples)
    return [v / len(samples) for v in c.values()]


def main() -> None:
    n96 = 2**96
    for q in (2**28, 2**32, 2**40, 2**48):
        p = collision_exact(q, n96)
        print(f"96-bit random nonces, q = 2^{int(math.log2(q))}: P[collision] = {p:.3e} (~2^{math.log2(p):.1f})")
    q = q_for_probability(2**-32, n96)
    print(f"messages per key for risk 2^-32: {q:.3e} (~2^{math.log2(q):.2f})")
    print(f"at 1,000,000 messages/s one key reaches 2^32 messages in {2**32 / 1e6 / 60:.1f} minutes")
    pin = [0.1] + [0.9 / 9999] * 9999
    print(f"4-digit PIN where '1234' has 10%: Shannon {shannon_entropy(pin):.2f} bits, min-entropy {min_entropy(pin):.2f} bits")


if __name__ == "__main__":
    main()
