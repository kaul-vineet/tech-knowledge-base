"""Build-task solution for lab 16: near-identity initialisation so wide/deep circuits start with real gradients.

Run: python solution_init.py
Every trainable angle starts close to 0 (normal, sigma 0.05), so each layer starts as ~identity: the first
gradient step sees a shallow circuit (the idea behind identity-block / layerwise initialisation, Grant et al.
2019, cited in PennyLane's barren-plateau demo). Keep the LOCAL <Z0> readout: a global parity readout stays
flat even with this init (tryIt 1).
"""
import json

import numpy as np

import classifier_lab as lab


def init_weights(layers, n, rng, sigma=0.05):
    return rng.normal(0.0, sigma, (layers, n))


if __name__ == "__main__":
    for n, layers in ((2, 2), (6, 12), (10, 20)):
        print(json.dumps(lab.gradient_scan(n, layers, init=init_weights)))
    tr, te, _ = lab.train_quantum(*lab.make_dataset(), init=init_weights)
    print(json.dumps({"model": "quantum 2q x 2 layers, near-identity init", "train_acc": tr, "test_acc": te}))
