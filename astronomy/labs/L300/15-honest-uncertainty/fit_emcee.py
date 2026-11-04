"""Library equivalent (pending-ci): the same posterior with emcee's affine-invariant ensemble sampler.

pip install -r ../requirements.txt   (emcee 3.1.6)        python fit_emcee.py
"""
import emcee
import numpy as np

import mcmc
import transit_fit as tf


def run(y, nwalkers=32, steps=4000, seed=5):
    p = tf.fit_lm(y)
    rng = np.random.default_rng(seed)
    start = np.append(p, np.log(2.0)) + 1e-4 * rng.normal(size=(nwalkers, 5))
    sampler = emcee.EnsembleSampler(nwalkers, 5, mcmc.log_prob, args=(y,))
    sampler.run_mcmc(start, steps, progress=False)
    tau = sampler.get_autocorr_time(discard=1000, quiet=True)
    return sampler.get_chain(discard=1000, flat=True, thin=max(1, int(tau.max() / 2))), tau


if __name__ == "__main__":
    flat, tau = run(tf.make_data())
    print("emcee t0 median/std:", np.median(flat[:, 0]).round(5), flat[:, 0].std().round(5),
          "noise scale s:", np.exp(np.median(flat[:, 4])).round(3), "tau max:", tau.max().round(1))
