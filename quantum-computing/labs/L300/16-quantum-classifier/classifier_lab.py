"""Lab 16 - a tiny variational quantum classifier vs a classical baseline, and flat gradients at scale.

Run:  python classifier_lab.py     (numpy only; writes logs/train_<n>q_<layers>l.jsonl)
SDK path (PennyLane 0.45.1, default.qubit): python classifier_pennylane.py   (CI job l300-extras, not yet observed)
"""
import json
from pathlib import Path

import numpy as np

import circuit_model as cm

HERE = Path(__file__).resolve().parent
SHOT_FLOOR = round(np.sqrt(2) / 2 / np.sqrt(1000), 4)   # std of a parameter-shift gradient from 1000 shots per term


def make_dataset(seed=3, n=60, n_train=40):
    """Two overlapping Gaussian blobs, features already in [0, pi]-ish radians for angle encoding."""
    rng = np.random.default_rng(seed)
    x = np.vstack([rng.normal([1.0, 2.0], 0.45, (n // 2, 2)), rng.normal([2.1, 1.0], 0.45, (n // 2, 2))])
    y = np.where(np.arange(n) < n // 2, 1, -1)
    perm = rng.permutation(n)
    x, y = x[perm], y[perm]
    return x[:n_train], y[:n_train], x[n_train:], y[n_train:]   # train / test split: test is never trained on


def logistic_baseline(xtr, ytr, xte, yte, steps=500, lr=0.5):
    mu, sd = xtr.mean(0), xtr.std(0)
    z, zt, w, b = (xtr - mu) / sd, (xte - mu) / sd, np.zeros(2), 0.0
    for _ in range(steps):
        p = 1 / (1 + np.exp(-(z @ w + b)))
        w, b = w - lr * z.T @ (p - (ytr + 1) / 2) / len(z), b - lr * np.mean(p - (ytr + 1) / 2)
    return float(np.mean(np.sign(z @ w + b) == ytr)), float(np.mean(np.sign(zt @ w + b) == yte))


def init_weights(layers, n, rng):
    """Textbook default: every angle uniform in [0, 2 pi). Fine for 2 qubits..."""
    return rng.uniform(0, 2 * np.pi, (layers, n))


def train_quantum(xtr, ytr, xte, yte, n=2, layers=2, epochs=60, lr=0.2, seed=0, init=None, log_path=None):
    w, b, rows = (init or init_weights)(layers, n, np.random.default_rng(seed)), 0.0, []
    for epoch in range(epochs):
        f = cm.outputs(w, xtr) + b                                  # model: <Z0> + classical bias
        g = cm.gradient(w, xtr)                                      # parameter shift, exact here
        gw, gb = (2 * (f - ytr) * g).mean(axis=-1), float(np.mean(2 * (f - ytr)))
        rows.append({"epoch": epoch, "loss": round(float(np.mean((f - ytr) ** 2)), 4),
                     "train_acc": float(np.mean(np.sign(f) == ytr)), "grad_norm": round(float(np.linalg.norm(gw)), 4)})
        w, b = w - lr * gw, b - lr * gb
    if log_path:
        Path(log_path).parent.mkdir(exist_ok=True)
        Path(log_path).write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    acc = lambda x, y: float(np.mean(np.sign(cm.outputs(w, x) + b) == y))   # noqa: E731
    return acc(xtr, ytr), acc(xte, yte), (w, b)


def gradient_scan(n, layers, init=None, samples=20, readout="local"):
    """Median |d<O>/dw[0,0]| over random inits: the number that tells you whether training can move at all."""
    x, grads = np.array([[1.0, 2.0]]), []
    for s in range(samples):
        w = (init or init_weights)(layers, n, np.random.default_rng(s))
        e = np.zeros_like(w)
        e[0, 0] = np.pi / 2
        grads.append(float((cm.outputs(w + e, x, readout) - cm.outputs(w - e, x, readout))[0] / 2))
    return {"n": n, "layers": layers, "readout": readout, "median_abs_grad": round(float(np.median(np.abs(grads))), 4),
            "below_shot_floor": float(np.mean(np.abs(grads) < SHOT_FLOOR))}


if __name__ == "__main__":
    data = make_dataset()
    q = train_quantum(*data, log_path=HERE / "logs" / "train_2q_2l.jsonl")
    print(json.dumps({"model": "quantum 2q x 2 layers (5 params)", "train_acc": q[0], "test_acc": q[1]}))
    print(json.dumps({"model": "logistic regression (3 params)", "train_acc": logistic_baseline(*data)[0],
                      "test_acc": logistic_baseline(*data)[1]}))
    tests = [(train_quantum(*make_dataset(s))[1], logistic_baseline(*make_dataset(s))[1]) for s in range(5)]
    print("test accuracy over 5 dataset seeds (quantum, classical):", tests)
    print(f"shot-noise floor for one gradient at 1000 shots: {SHOT_FLOOR}")
    for n, layers in ((2, 2), (6, 12), (10, 20)):                     # the fault: scale up with random init
        print(json.dumps(gradient_scan(n, layers)))
