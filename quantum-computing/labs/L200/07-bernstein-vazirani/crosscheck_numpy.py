"""Independent numpy check for lab 07 (no quantum SDK). Run: python crosscheck_numpy.py

Builds the same Bernstein-Vazirani circuit gate by gate on the shared numpy simulator
(labs/_shared/qsim, Qiskit bit order) and prints the exact outcome probabilities.
"""
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))
from qsim import statevector as sv  # noqa: E402


def oracle_ops(secret, reverse=True):
    n = len(secret)
    bits = reversed(secret) if reverse else secret
    return [sv.cx(q, n) for q, b in enumerate(bits) if b == "1"]


def bv_ops(oracle, n, kickback=True):
    prep = ([sv.x(n)] if kickback else []) + [sv.h(q) for q in range(n + 1)]
    return prep + oracle + [sv.h(q) for q in range(n)]


def input_probabilities(state, n):
    """Probabilities of the n input qubits (ancilla summed out), Qiskit bit order."""
    out = {}
    for key, p in sv.probabilities(state).items():
        out[key[1:]] = round(out.get(key[1:], 0) + p, 12)   # key[0] is the ancilla (highest qubit)
    return out


def bv_probabilities(secret, **kw):
    n = len(secret)
    return input_probabilities(sv.run(n + 1, bv_ops(oracle_ops(secret), n, **kw)), n)


def all_secrets_found(n):
    return all(bv_probabilities("".join(s)) == {"".join(s): 1.0} for s in itertools.product("01", repeat=n))


if __name__ == "__main__":
    for secret in ("1011", "110101"):
        print(f"secret {secret}: {bv_probabilities(secret)}")
    print("all 16 four-bit secrets recovered with probability 1:", all_secrets_found(4))
