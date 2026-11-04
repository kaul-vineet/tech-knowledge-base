"""Independent numpy statevector simulator for the L200 cross-checks.

Convention = Qiskit's: qubit 0 is the least-significant bit of the basis index, and bitstrings
are printed with qubit n-1 first (so '011' means q0=1, q1=1, q2=0).
An operation is a tuple (matrix_2x2, target, controls); helpers below build the common ones.
"""
import numpy as np

H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.diag([1, -1]).astype(complex)
SX = 0.5 * np.array([[1 + 1j, 1 - 1j], [1 - 1j, 1 + 1j]])


def rz(t):
    return np.diag([np.exp(-0.5j * t), np.exp(0.5j * t)])


def ry(t):
    c, s = np.cos(t / 2), np.sin(t / 2)
    return np.array([[c, -s], [s, c]], dtype=complex)


def rx(t):
    c, s = np.cos(t / 2), np.sin(t / 2)
    return np.array([[c, -1j * s], [-1j * s, c]], dtype=complex)


def phase(lam):
    return np.diag([1, np.exp(1j * lam)])


def h(q):
    return (H, q, ())


def x(q):
    return (X, q, ())


def cx(c, t):
    return (X, t, (c,))


def cp(lam, c, t):
    return (phase(lam), t, (c,))


def mcz(controls, t):
    return (Z, t, tuple(controls))


def swap(a, b):
    return [cx(a, b), cx(b, a), cx(a, b)]


def apply(state, op):
    """Apply one (matrix, target, controls) op: the 2x2 matrix acts where all controls are 1."""
    gate, target, controls = op
    idx = np.arange(len(state))
    mask = (idx >> target) & 1 == 0
    for c in controls:
        mask &= (idx >> c) & 1 == 1
    i0 = idx[mask]
    i1 = i0 | (1 << target)
    out = state.copy()
    a, b = state[i0], state[i1]
    out[i0] = gate[0, 0] * a + gate[0, 1] * b
    out[i1] = gate[1, 0] * a + gate[1, 1] * b
    return out


def flatten(ops):
    for op in ops:
        if isinstance(op, list):
            yield from flatten(op)
        else:
            yield op


def run(n, ops, state=None):
    state = np.eye(2 ** n, dtype=complex)[0] if state is None else np.asarray(state, dtype=complex)
    for op in flatten(ops):
        state = apply(state, op)
    return state


def unitary(n, ops):
    """Column j = circuit applied to basis state |j>."""
    return np.column_stack([run(n, ops, col) for col in np.eye(2 ** n, dtype=complex)])


def probabilities(state, decimals=12):
    n = int(np.log2(len(state)))
    p = np.abs(state) ** 2
    return {format(i, f"0{n}b"): round(float(v), decimals) for i, v in enumerate(p) if v > 1e-12}


def equal_up_to_global_phase(a, b, atol=1e-9):
    a, b = np.asarray(a), np.asarray(b)
    k = np.flatnonzero(np.abs(b) > atol)[0]
    ratio = a.flat[k] / b.flat[k]
    return bool(np.isclose(abs(ratio), 1, atol=atol) and np.allclose(a, ratio * b, atol=atol))
