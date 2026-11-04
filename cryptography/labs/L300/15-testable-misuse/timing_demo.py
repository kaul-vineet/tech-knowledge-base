"""Timing leak, measured: an early-exit byte loop vs hmac.compare_digest. Statistical and noisy by nature:
seeded inputs, interleaved rounds, medians. Numbers differ per machine; the RATIO is what to look at."""
import hmac
import random
import statistics
import time

SEED = 15


def naive_equal(a: bytes, b: bytes) -> bool:
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if x != y:
            return False  # early exit: run time grows with the length of the matching prefix
    return True


def _median_ns(cmp, secret, guess, reps):
    times = []
    for _ in range(reps):
        start = time.perf_counter_ns()
        cmp(secret, guess)
        times.append(time.perf_counter_ns() - start)
    return statistics.median(times)  # median: robust against scheduler spikes


def experiment(cmp, seed=SEED, rounds=7, reps=2000):
    """Median time for a guess wrong at byte 0 vs wrong at byte 31 (31 correct bytes leaked by timing)."""
    secret = random.Random(seed).randbytes(32)  # seeded so every run compares the same bytes
    early = bytes([secret[0] ^ 1]) + secret[1:]
    late = secret[:-1] + bytes([secret[-1] ^ 1])
    a, b = [], []
    for _ in range(rounds):  # interleave so CPU frequency changes hit both guesses alike
        a.append(_median_ns(cmp, secret, early, reps))
        b.append(_median_ns(cmp, secret, late, reps))
    return statistics.median(a), statistics.median(b)


if __name__ == "__main__":
    for name, cmp in (("naive loop", naive_equal), ("hmac.compare_digest", hmac.compare_digest)):
        early, late = experiment(cmp)
        print(f"{name:<20} wrong at byte 0: {early:>6.0f} ns | wrong at byte 31: {late:>6.0f} ns | ratio {late / early:.2f}")
    print("A ratio well above 1 means time reveals how many leading bytes were right.")
