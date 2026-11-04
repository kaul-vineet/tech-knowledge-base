"""Try it: two experiments on testable misuse (run: python try_it.py)."""
import timing_demo as td
import wycheproof_check as wc

# 1) Feed the lenient AES-GCM wrapper a tag cut to 4 bytes: how many random tags would an attacker need?
rows = [r for r in wc.run() if r[1] == 9002]
print("1) 4-byte tag accepted by lenient wrapper:", rows[0][4] == "valid", "| forgery odds per try: 1 in", f"{2**32:,}",
      "(16-byte tag: 1 in 2**128)")

# 2) Does the leak grow with the number of matching bytes? Guess wrong at byte 0, 8, 16, 31 (naive loop).
secret = bytes(range(32))
times = []
for pos in (0, 8, 16, 31):
    guess = secret[:pos] + bytes([secret[pos] ^ 1]) + secret[pos + 1:]
    times.append(min(td._median_ns(td.naive_equal, secret, guess, 2000) for _ in range(5)))
print("2) naive loop, wrong at byte 0/8/16/31:", " < ".join(f"{t:.0f} ns" for t in times),
      "| increasing:", all(a < b for a, b in zip(times, times[1:])))
