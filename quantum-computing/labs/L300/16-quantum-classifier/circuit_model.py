"""Helper for lab 16: a batched numpy simulator for the classifier circuit (all data points at once).

Circuit for n qubits and L layers (PennyLane names in brackets):
  encoding  RY(x[q % 2]) on qubit q                       [qp.AngleEmbedding(x, wires, rotation="Y")]
  layer l   RY(w[l, q]) on every qubit, then CNOT chain    [qp.BasicEntanglerLayers(w, wires, rotation=qp.RY)*]
  readout   <Z0> ("local") or <Z0 Z1 ... Z(n-1)> ("global")
*BasicEntanglerLayers closes the chain into a ring for n > 2; this helper uses an open chain (q -> q+1).
Gradients use the parameter-shift rule: d<O>/dw = (<O>(w + pi/2) - <O>(w - pi/2)) / 2, exact for RY gates.
"""
import numpy as np


def _ry_batch(states, angles, q, n):
    """RY(angle_b) on qubit q for every row b (angles: one per row, or a scalar)."""
    b = states.shape[0]
    s = states.reshape(b, 2 ** (n - 1 - q), 2, 2 ** q)
    c = np.broadcast_to(np.cos(np.asarray(angles) / 2), (b,))[:, None, None]
    si = np.broadcast_to(np.sin(np.asarray(angles) / 2), (b,))[:, None, None]
    lo, hi = s[:, :, 0, :], s[:, :, 1, :]
    return np.stack([c * lo - si * hi, si * lo + c * hi], axis=2).reshape(b, -1)


def _cx(states, c, t, n):
    idx = np.arange(2 ** n)
    src = np.where((idx >> c) & 1, idx ^ (1 << t), idx)
    return states[:, src]


def outputs(w, x, readout="local"):
    """Model output in [-1, 1] for every row of x (shape (B, 2)); w has shape (L, n)."""
    layers, n = w.shape
    states = np.zeros((len(x), 2 ** n))
    states[:, 0] = 1.0
    for q in range(n):
        states = _ry_batch(states, x[:, q % 2], q, n)                 # angle encoding (data re-used on wide models)
    for l in range(layers):
        for q in range(n):
            states = _ry_batch(states, w[l, q], q, n)
        for q in range(n - 1):
            states = _cx(states, q, q + 1, n)
    idx = np.arange(2 ** n)
    qubits = [0] if readout == "local" else range(n)
    z = np.prod([1 - 2 * ((idx >> q) & 1) for q in qubits], axis=0)
    return (states ** 2) @ z                                          # real amplitudes: |a|^2 = a^2


def gradient(w, x, readout="local"):
    """Parameter-shift gradient of the outputs: array (L, n, B)."""
    g = np.zeros(w.shape + (len(x),))
    for idx in np.ndindex(w.shape):
        shift = np.zeros_like(w)
        shift[idx] = np.pi / 2
        g[idx] = (outputs(w + shift, x, readout) - outputs(w - shift, x, readout)) / 2
    return g
