"""Try-it checks for lab 16. Run: python try_it.py   (numpy only)"""
import numpy as np

import circuit_model as cm
import classifier_lab as lab
import solution_init as sol


def global_readout_with_good_init():
    """Try 1: keep the near-identity init but read out the global parity <Z0 Z1 ... Z9>. Still trainable?"""
    return {ro: lab.gradient_scan(10, 20, init=sol.init_weights, samples=10, readout=ro)["median_abs_grad"]
            for ro in ("local", "global")}


def shot_noise_at_prediction(shots=100, seed=5):
    """Try 2: classify the 20 test points from `shots` measurements each instead of the exact <Z0>."""
    xtr, ytr, xte, yte = lab.make_dataset()
    _, exact_acc, (w, b) = lab.train_quantum(xtr, ytr, xte, yte)
    p1 = (1 - cm.outputs(w, xte)) / 2                                  # P(measure 1 on qubit 0)
    z_est = 1 - 2 * np.random.default_rng(seed).binomial(shots, p1) / shots
    return {"exact": exact_acc, f"{shots}_shots": float(np.mean(np.sign(z_est + b) == yte))}


if __name__ == "__main__":
    print("global_readout_with_good_init", global_readout_with_good_init())
    print("shot_noise_at_prediction     ", shot_noise_at_prediction())
