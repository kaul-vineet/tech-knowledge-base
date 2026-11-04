"""Lab 16 SDK path: the same 2-qubit classifier in PennyLane 0.45.1 (import pennylane as qp, default.qubit).

Run:  python classifier_pennylane.py   (needs labs/L300/requirements-extras.txt; CI job l300-extras, not yet observed)
API from the PennyLane 0.45.1 docs: qp.AngleEmbedding(features, wires, rotation="Y"),
qp.BasicEntanglerLayers(weights, wires, rotation=qp.RY) (two wires: one CNOT per layer, no ring),
qp.expval(qp.Z(0)), qp.grad, qp.GradientDescentOptimizer, `from pennylane import numpy as pnp` for trainable arrays.
"""
import numpy as np
import pennylane as qp
from pennylane import numpy as pnp

import classifier_lab as lab

dev = qp.device("default.qubit", wires=2)


@qp.qnode(dev)
def circuit(weights, x):
    qp.AngleEmbedding(x, wires=range(2), rotation="Y")
    qp.BasicEntanglerLayers(weights, wires=range(2), rotation=qp.RY)
    return qp.expval(qp.Z(0))


def output(w, x):
    return float(circuit(pnp.array(w, requires_grad=True), pnp.array(x, requires_grad=False)))


def gradient(w, x):
    return np.asarray(qp.grad(circuit, argnums=0)(pnp.array(w, requires_grad=True), pnp.array(x, requires_grad=False)))


def train(epochs=60, lr=0.2, seed=0):
    xtr, ytr, xte, yte = lab.make_dataset()
    w = pnp.array(lab.init_weights(2, 2, np.random.default_rng(seed)), requires_grad=True)
    b = pnp.array(0.0, requires_grad=True)

    def cost(w, b):
        preds = qp.math.stack([circuit(w, pnp.array(x, requires_grad=False)) + b for x in xtr])
        return pnp.mean((preds - ytr) ** 2)

    opt = qp.GradientDescentOptimizer(stepsize=lr)
    for _ in range(epochs):
        w, b = opt.step(cost, w, b)
    acc = lambda xs, ys: float(np.mean([np.sign(output(w, x) + float(b)) == y for x, y in zip(xs, ys)]))   # noqa: E731
    return acc(xtr, ytr), acc(xte, yte)


if __name__ == "__main__":
    print("PennyLane output at w=[[0.3,-0.7],[1.1,0.2]], x=[1,2]:", round(output([[0.3, -0.7], [1.1, 0.2]], [1.0, 2.0]), 6))
    print("PennyLane train/test accuracy:", train(), "| numpy lab:", lab.train_quantum(*lab.make_dataset())[:2])
