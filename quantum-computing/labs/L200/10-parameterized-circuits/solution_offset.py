"""Build-task solution for lab 10: add an offset parameter phi, bind it, recover it from the fit.

Run: python solution_offset.py
<Z> = cos(theta + phi) = cos(phi) cos(theta) - sin(phi) sin(theta), so the fit gives
a = cos(phi), b = -sin(phi) and phi = atan2(-b, a). numpy part runs anywhere; the Qiskit part needs qiskit.
"""
import math

import numpy as np

import crosscheck_numpy as cc


def recover_phi(thetas, z_values):
    design = np.column_stack([np.cos(thetas), np.sin(thetas), np.ones_like(thetas)])
    (a, b, _), *_ = np.linalg.lstsq(design, z_values, rcond=None)   # unrounded fit coefficients
    return round(math.atan2(-b, a), 3)


def offset_numpy(phi, shots=None, seed=7):
    shifted = cc.THETAS + phi
    z = cc.exact(thetas=shifted)[0] if shots is None else cc.sampled_z(thetas=shifted, shots=shots, seed=seed)
    return recover_phi(cc.THETAS, z)


def offset_qiskit(phi_value):
    from qiskit import QuantumCircuit
    from qiskit.circuit import Parameter

    import param_lab
    theta, phi = Parameter("theta"), Parameter("phi")
    qc = QuantumCircuit(1)
    qc.ry(theta + phi, 0)                              # ParameterExpression: sum of two symbols
    partly_bound = qc.assign_parameters({phi: phi_value})   # bind phi only; theta stays free
    z, _ = param_lab.exact_expectations(partly_bound)
    return partly_bound.num_parameters, recover_phi(param_lab.THETAS, np.asarray(z))


if __name__ == "__main__":
    print("exact, phi = 0.3:", offset_numpy(0.3))
    print("400 shots, phi = 0.3:", offset_numpy(0.3, shots=400))
