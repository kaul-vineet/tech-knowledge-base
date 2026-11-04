"""Theorem 25.1 (Hull & Dobell 1962): x_(k+1) = (a x_k + c) mod m has full period m for every seed iff
(i) gcd(c, m) = 1, (ii) a - 1 is divisible by every prime factor of m, (iii) a - 1 is divisible by 4 if 4 | m.
Corollary (RANDU, a = 65539 = 2^16 + 3, c = 0, m = 2^31): a^2 = 6a - 9 (mod 2^31), so
x_(k+2) = 6 x_(k+1) - 9 x_k (mod 2^31): every triple lies on one of a few planes."""
import math


def prime_factors(m):
    out, p = set(), 2
    while p * p <= m:
        while m % p == 0:
            out.add(p)
            m //= p
        p += 1
    return out | ({m} if m > 1 else set())


def hull_dobell(a, c, m):
    return (math.gcd(c, m) == 1 and all((a - 1) % p == 0 for p in prime_factors(m))
            and ((a - 1) % 4 == 0 if m % 4 == 0 else True))


def period(a, c, m, seed=0):
    seen, x, k = {}, seed, 0
    while x not in seen:
        seen[x] = k
        x, k = (a * x + c) % m, k + 1
    return k - seen[x]


for m in (64, 60, 81):  # 2^6, 2^2*3*5, 3^4
    agree = full = 0
    for a in range(m):
        for c in range(m):
            is_full = period(a, c, m) == m
            full += is_full
            agree += is_full == hull_dobell(a, c, m)
    print(f"m = {m}: {m * m} (a, c) pairs, full period for {full}; Hull-Dobell predicts all {agree}/{m * m}")
    assert agree == m * m

M = 2**31
print(f"RANDU: a^2 mod 2^31 = {65539**2 % M}, (6a - 9) mod 2^31 = {(6 * 65539 - 9) % M}")
x, xs = 1, []
for _ in range(100_000):
    x = 65539 * x % M
    xs.append(x)
bad = sum((xs[k + 2] - 6 * xs[k + 1] + 9 * xs[k]) % M != 0 for k in range(len(xs) - 2))
ks = {(xs[k + 2] - 6 * xs[k + 1] + 9 * xs[k]) // M for k in range(len(xs) - 2)}
print(f"RANDU triples violating x2 = 6 x1 - 9 x0 (mod 2^31): {bad} of {len(xs) - 2}; distinct planes used: {len(ks)}")
assert bad == 0 and len(ks) <= 15
lcg = [12345]
for _ in range(16):
    lcg.append((1664525 * lcg[-1] + 1013904223) % 2**32)
print("lowest bit of an m = 2^32 LCG (a = 1664525, c = 1013904223):", "".join(str(v & 1) for v in lcg), "-> period 2")
