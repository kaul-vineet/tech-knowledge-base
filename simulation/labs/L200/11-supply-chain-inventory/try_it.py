"""tryIt experiments for lesson 11 (run: python try_it.py)."""
import numpy as np

import inventory as inv


def simulate_one_stream(s, S, rep):
    """Same model, but weather, demand AND lead times come from ONE generator, each drawn when it is needed."""
    rng = np.random.default_rng([rep, 0])
    on_hand, arriving, cost, lost, orders = S, np.zeros(inv.DAYS + 5, dtype=int), 0.0, 0, 0
    for t in range(inv.DAYS):
        weather = rng.gamma(4.0, 0.25) if t % 7 == 0 else weather
        on_hand += arriving[t]
        d = rng.poisson(inv.MEAN_DEMAND * weather)
        sold = min(on_hand, d)
        lost, on_hand = lost + d - sold, on_hand - sold
        position = on_hand + arriving[t + 1:].sum()
        if position <= s:
            arriving[t + rng.integers(1, 5)] += S - position  # this extra draw shifts every later demand
            orders += 1
        cost += inv.HOLD * on_hand
    return (cost + inv.ORDER * orders + inv.LOST * lost) / inv.DAYS


# 1. Same seeds for both policies, but a single shared stream. Predict: is the comparison still sharp?
diffs = [simulate_one_stream(30, 90, r) - simulate_one_stream(30, 80, r) for r in range(30)]
m, h = inv.ci(diffs)
print(f"same seeds, ONE shared stream: S=90 minus S=80 = {m:+.2f} +/- {h:.2f}")
m, h = inv.compare((30, 80), (30, 90))
print(f"same seeds, one stream per purpose (lab): {m:+.2f} +/- {h:.2f}")

# 2. Halve the lost-sale penalty (4.00 -> 2.00). Predict: does the bigger order-up-to level still pay?
inv.LOST = 2.0
m, h = inv.compare((30, 80), (30, 90))
print(f"lost sale costs 2.00: S=90 minus S=80 = {m:+.2f} +/- {h:.2f} per day")
