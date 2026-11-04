"""Try-it checks for lab 06. Run: python try_it.py

numpy models both bit-order conventions locally; the SDK part runs only when qiskit and cirq
are installed (CI).
"""
import importlib.util

HAVE_SDKS = all(importlib.util.find_spec(m) for m in ("qiskit", "cirq"))


def keys_for_x(flipped, n, measure_order):
    """Bitstring each convention prints when X is applied to qubit `flipped` of n.

    Qiskit: qubit 0 rightmost. Cirq histogram over measure(*measure_order): first measured qubit leftmost.
    """
    bits = [1 if q == flipped else 0 for q in range(n)]
    qiskit = "".join(str(bits[q]) for q in reversed(range(n)))
    cirq_raw = "".join(str(bits[q]) for q in measure_order)
    return {"qiskit": qiskit, "cirq_raw": cirq_raw, "cirq_in_qiskit_order": cirq_raw[::-1]}


def try1_numpy():
    """Try 1: three qubits, X on qubit 0, measure(q0, q1, q2)."""
    return keys_for_x(0, 3, (0, 1, 2))


def try2_numpy():
    """Try 2: lab circuit x_on_q0 but measure(q1, q0) instead of measure(q0, q1)."""
    return keys_for_x(0, 2, (1, 0))


def sdk_try1(shots=100):
    import cirq
    from qiskit import QuantumCircuit
    from qiskit.primitives import StatevectorSampler
    qc = QuantumCircuit(3)
    qc.x(0)
    qc.measure_all()
    q = cirq.LineQubit.range(3)
    c = cirq.Circuit(cirq.X(q[0]), cirq.measure(*q, key="m"))
    hist = cirq.Simulator(seed=7).run(c, repetitions=shots).histogram(key="m")
    qk = StatevectorSampler(seed=7).run([qc], shots=shots).result()[0].data.meas.get_counts()
    return {"qiskit": next(iter(qk)), "cirq_raw": format(next(iter(hist)), "03b")}


def sdk_try2(shots=100):
    import cirq
    q0, q1 = cirq.NamedQubit("q0"), cirq.NamedQubit("q1")
    c = cirq.Circuit(cirq.X(q0), cirq.measure(q1, q0, key="m"))
    hist = cirq.Simulator(seed=7).run(c, repetitions=shots).histogram(key="m")
    return {"cirq_raw": format(next(iter(hist)), "02b")}


if __name__ == "__main__":
    print("try 1 numpy", try1_numpy())
    print("try 2 numpy", try2_numpy())
    if HAVE_SDKS:
        print("try 1 SDKs ", sdk_try1())
        print("try 2 cirq ", sdk_try2())
