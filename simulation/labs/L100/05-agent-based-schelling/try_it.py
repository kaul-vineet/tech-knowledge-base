"""tryIt experiments for lesson 5 (run: python try_it.py)."""
import schelling as s

# 1. Raise the preference from 30% to 50% similar wanted.
for want in (0.3, 0.5):
    s.WANT = want
    _, h = s.run(seed=42, max_steps=200)
    print(f"want {100 * want:.0f}%: end % similar {h[-1][0]:.1f}, % unhappy {h[-1][1]:.1f}, steps {len(h) - 1}")

# 2. Same 30% rule, five different seeds.
s.WANT = 0.3
print("seeds 1-5 end % similar:", [round(float(s.run(seed=k)[1][-1][0]), 1) for k in range(1, 6)])
