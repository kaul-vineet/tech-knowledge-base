"""Try-it checks for lab 10. Run: python try_it.py

The numpy part runs anywhere; the SDK part runs only when qiskit is installed (CI).
"""
import importlib.util

import crosscheck_numpy as cc
from qsim import statevector as sv

HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None


def rx_instead_of_ry_numpy():
    """Try 1: qc.rx(theta, 0) instead of qc.ry(theta, 0)."""
    z, x = cc.exact(gate=sv.rx)
    return {"fit_Z": cc.fit_cos_sin(cc.THETAS, z), "fit_X": cc.fit_cos_sin(cc.THETAS, x)}


def fewer_shots_numpy():
    """Try 2: sampled_z(qc, shots=25) instead of 400."""
    out = {}
    for shots in (25, 400):
        fit = cc.fit_cos_sin(cc.THETAS, cc.sampled_z(shots=shots))
        out[shots] = {"fit": fit, "worst_error": round(max(abs(fit[0] - 1), abs(fit[1]), abs(fit[2])), 3)}
    return out


def sdk_results():
    from qiskit import QuantumCircuit
    from qiskit.circuit import Parameter

    import param_lab
    theta = Parameter("theta")
    qc = QuantumCircuit(1)
    qc.rx(theta, 0)
    z, x = param_lab.exact_expectations(qc)
    ry, _ = param_lab.ansatz()
    errors = {}
    for shots in (25, 400):
        fit = param_lab.fit_cos_sin(param_lab.THETAS, param_lab.sampled_z(ry, shots=shots))
        errors[shots] = round(max(abs(fit[0] - 1), abs(fit[1]), abs(fit[2])), 3)
    return {"fit_Z": param_lab.fit_cos_sin(param_lab.THETAS, z), "fit_X": param_lab.fit_cos_sin(param_lab.THETAS, x),
            "worst_error_by_shots": errors}


if __name__ == "__main__":
    print(f"rx_instead_of_ry numpy {rx_instead_of_ry_numpy()}")
    print(f"fewer_shots      numpy {fewer_shots_numpy()}")
    if HAVE_QISKIT:
        print(f"qiskit {sdk_results()}")
