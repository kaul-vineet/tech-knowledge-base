"""tryIt experiments for lesson 6 (run: python try_it.py)."""
import vv

# 1. Plant a bug: forget the max(0, ...) in the model rule.
buggy = lambda w, service, gap: w + service - gap
bad = vv.waits(20_000, 0.8, 3, rule=buggy)
print(f"buggy rule: min wait {min(bad):.1f} min, mean wait {sum(bad) / len(bad):.1f} min  (negative waits are impossible)")

# 2. Skip the warm-up on short runs (2,000 customers, starting from an empty shop).
for warmup in (0, 500):
    means = [vv.mean_wait(2_000, 0.8, seed, warmup=warmup) for seed in range(1, 51)]
    print(f"warm-up {warmup:3}: average of 50 short runs = {sum(means) / len(means):.2f} min (formula 4.00)")
