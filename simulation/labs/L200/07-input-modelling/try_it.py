"""tryIt experiments for lesson 7 (run: python try_it.py)."""
import numpy as np

import fit_inputs as fi

x = fi.load()

# 1. Only 30 measurements (the first 30 rows). Predict: does the KS ranking still pick lognormal clearly?
small = x[:30]
ds = {f(small)["name"]: fi.ks_statistic(small, f(small)["cdf"]) for f in fi.FITTERS}
print("n=30: " + ", ".join(f"{k} D={v:.3f}" for k, v in ds.items()) + f" | 1.36/sqrt(30)={1.36 / np.sqrt(30):.3f}")

# 2. How wrong is the exponential input at different loads? Ratio of mean waits vs the resampled data.
for load in (0.5, 0.7, 0.85):
    lam = load / x.mean()
    exp_w = fi.queue_waits(fi.fit_exponential(x)["sample"], lam).mean()
    data_w = fi.queue_waits(lambda rng, n: rng.choice(x, n), lam).mean()
    print(f"load {load:.2f}: exponential input {exp_w:6.2f} min vs data {data_w:6.2f} min -> {exp_w / data_w:.2f}x")
