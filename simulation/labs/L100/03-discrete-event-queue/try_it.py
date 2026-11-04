"""tryIt experiments for lesson 3 (run: python try_it.py)."""
import des_queue as dq

# 1. Add 10% more customers (lam 0.8 -> 0.88). Predict: wait grows by ~10%?
for lam in (0.8, 0.88):
    waits, _ = dq.simulate(200_000, 1, lam=lam)
    print(f"lam={lam}: simulated Wq={sum(waits) / len(waits):.2f} min, formula Wq={dq.mm1_wq(lam):.2f} min")

# 2. Short run: only 200 customers, three seeds.
for seed in (1, 2, 3):
    waits, _ = dq.simulate(200, seed)
    print(f"200 customers, seed {seed}: mean wait {sum(waits) / len(waits):.2f} min")
