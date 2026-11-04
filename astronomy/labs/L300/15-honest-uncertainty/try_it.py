"""tryIt for lesson 15.
1. Shipped uncertainty(), but the pipeline's flux_err is RIGHT this time (0.0020): is the coverage still bad?
2. MCMC with only 1 000 steps (burn 200): what do the autocorrelation time and effective samples say?
"""
import numpy as np

import mcmc
import transit_fit as tf

if __name__ == "__main__":
    tf.SIGMA_REPORTED = 0.0020
    print("1. flux_err = true scatter: coverage", dict(zip(tf.NAMES, tf.coverage().round(3).tolist())))
    tf.SIGMA_REPORTED = 0.0010
    post, acc, tau = mcmc.run(tf.make_data(), steps=1_000, burn=200)
    print(f"2. 1000 steps: acceptance {acc:.3f}, tau {tau:.0f}, chain/tau {len(post) / tau:.0f} "
          f"(emcee docs: > ~50 is often enough), s = {np.exp(np.median(post[:, 4])):.3f}")
