"""PCG64 and Philox concepts in NumPy: state-transition (PCG64 = 128-bit LCG + output permutation, advance() jumps
ahead) versus counter-based (Philox: output = bijection(counter, key); any position is computable directly)."""
import numpy as np

a = np.random.PCG64(42)
skip = np.random.Generator(np.random.PCG64(42))
skip.integers(0, 2**64, size=1000, dtype=np.uint64, endpoint=False)  # draw 1,000 64-bit outputs
a.advance(1000)  # jump the LCG state 1,000 steps in O(log n) work
print("PCG64: 1,001st output after drawing 1,000 == after advance(1000):",
      skip.integers(0, 2**64, dtype=np.uint64) == np.random.Generator(a).integers(0, 2**64, dtype=np.uint64))
p1 = np.random.Philox(key=7, counter=0)
p2 = np.random.Philox(key=7, counter=0)
p2.advance(250)  # Philox makes 4 x 64-bit words per counter value; advance counts counter steps
g1, g2 = np.random.Generator(p1), np.random.Generator(p2)
first = g1.integers(0, 2**64, size=1004, dtype=np.uint64)
print("Philox: word 1,000 via counter advance(250) equals the stream's word 1,000:", first[1000] == g2.integers(0, 2**64, dtype=np.uint64))
kids = np.random.SeedSequence(2025).spawn(3)
print("SeedSequence.spawn -> independent streams, first draws:",
      [round(float(np.random.Generator(np.random.PCG64(k)).random()), 4) for k in kids])
print("periods: PCG64 2^128; Philox4x64 2^256 - 1 (NumPy docs)")
