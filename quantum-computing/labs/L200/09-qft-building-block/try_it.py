"""Try-it checks for lab 09. Run: python try_it.py

The numpy part runs anywhere; the SDK part runs only when qiskit is installed (CI).
"""
import importlib.util

import numpy as np

import crosscheck_numpy as cc
from qsim import statevector as sv

HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None
N = 3


def no_swaps_numpy():
    """Try 1: qft_circuit(3, swaps=False)."""
    u = sv.unitary(N, cc.qft_ops(N, swaps=False))
    return {"max_error_vs_dft": round(cc.max_error(u, cc.dft_matrix(N)), 4),
            "after_bit_reversing_rows": round(cc.max_error(cc.bit_reverse_rows(u, N), cc.dft_matrix(N)), 12)}


def negated_angles_numpy():
    """Try 2: use -np.pi / 2 ** (j - k) in qc.cp."""
    u = sv.unitary(N, cc.qft_ops(N, sign=-1))
    return {"max_error_vs_dft": round(cc.max_error(u, cc.dft_matrix(N)), 4),
            "max_error_vs_np_fft_fft": round(cc.max_error(u, np.fft.fft(np.eye(2 ** N), axis=0, norm="ortho")), 12)}


def sdk_versions():
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator

    import qft_lab
    neg = QuantumCircuit(N)
    for j in reversed(range(N)):
        neg.h(j)
        for k in reversed(range(j)):
            neg.cp(-np.pi / 2 ** (j - k), k, j)
    for i in range(N // 2):
        neg.swap(i, N - 1 - i)
    no_swaps = Operator(qft_lab.qft_circuit(N, swaps=False)).data
    return {"no_swaps_equals_dft": bool(np.allclose(no_swaps, qft_lab.dft_matrix(N))),
            "no_swaps_bit_reversed_equals_dft": bool(np.allclose(cc.bit_reverse_rows(no_swaps, N), qft_lab.dft_matrix(N))),
            "negated_equals_np_fft_fft": bool(np.allclose(Operator(neg).data, np.fft.fft(np.eye(2 ** N), axis=0, norm="ortho")))}


if __name__ == "__main__":
    print(f"no_swaps        numpy {no_swaps_numpy()}")
    print(f"negated_angles  numpy {negated_angles_numpy()}")
    if HAVE_QISKIT:
        print(f"qiskit {sdk_versions()}")
