"""Lab 10 - parameterized circuits: Parameter objects, binding, sweeping an angle, fitting <Z>.

Run:  python param_lab.py
Needs: qiskit (Parameter, StatevectorEstimator, StatevectorSampler, SparsePauliOp) and numpy.
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.primitives import StatevectorEstimator, StatevectorSampler
from qiskit.quantum_info import SparsePauliOp

THETAS = np.linspace(0, 2 * np.pi, 21)


def ansatz():
    theta = Parameter("theta")
    qc = QuantumCircuit(1)
    qc.ry(theta, 0)                     # template: the angle stays a symbol until values are bound
    return qc, theta


def exact_expectations(qc, thetas=THETAS):
    observables = [[SparsePauliOp("Z")], [SparsePauliOp("X")]]   # shape (2, 1) broadcasts with (21,)
    pub = (qc, observables, thetas.reshape(-1, 1))               # one PUB = circuit + observables + sweep
    return StatevectorEstimator().run([pub]).result()[0].data.evs   # exact, shape (2, 21)


def sampled_z(qc, thetas=THETAS, shots=400, seed=7):
    measured = qc.copy()
    measured.measure_all()
    bits = StatevectorSampler(seed=seed).run([(measured, thetas.reshape(-1, 1))], shots=shots).result()[0].data.meas
    counts = [bits.get_counts(i) for i in range(len(thetas))]     # one counts dict per bound angle
    return np.array([(c.get("0", 0) - c.get("1", 0)) / shots for c in counts])   # <Z> = (n0 - n1) / shots


def fit_cos_sin(thetas, values):
    """Least squares for a*cos(theta) + b*sin(theta) + c: the expected shape of a 1-qubit rotation."""
    a = np.column_stack([np.cos(thetas), np.sin(thetas), np.ones_like(thetas)])
    coef, *_ = np.linalg.lstsq(a, values, rcond=None)
    return [round(float(c), 3) + 0.0 for c in coef]


if __name__ == "__main__":
    qc, theta = ansatz()
    print("free parameters:", list(qc.parameters))
    bound = qc.assign_parameters({theta: np.pi / 3})   # binding: a concrete copy; qc keeps its symbol
    print("after binding pi/3:", bound.num_parameters, "free;", qc.num_parameters, "free in the template")
    z, x = exact_expectations(qc)
    print("exact <Z> at theta = 0, pi/2, pi:", np.round(z[[0, 5, 10]], 4).tolist())
    print("fit exact <Z> [a, b, c]:", fit_cos_sin(THETAS, z))
    print("fit exact <X> [a, b, c]:", fit_cos_sin(THETAS, x))
    print("fit sampled <Z>, 400 shots, seed 7:", fit_cos_sin(THETAS, sampled_z(qc)))
