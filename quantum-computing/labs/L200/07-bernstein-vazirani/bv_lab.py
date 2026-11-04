"""Lab 07 - Bernstein-Vazirani as a pattern: find a hidden bit-string with ONE oracle query.

Run:  python bv_lab.py
Needs: qiskit (StatevectorSampler is built in; no Aer needed).
"""
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def bv_oracle(secret):
    """Query gate for f(x) = secret . x (mod 2): one CX from each '1' input qubit to the ancilla."""
    n = len(secret)
    qc = QuantumCircuit(n + 1, name="oracle")
    for qubit, bit in enumerate(reversed(secret)):   # bit order: string is q(n-1)...q0, so reverse it
        if bit == "1":
            qc.cx(qubit, n)                          # oracle construction: parity of the selected bits
    return qc


def bv_circuit(oracle):
    """Wrap ANY query gate in the Deutsch-Jozsa pattern: H, query once, H, measure."""
    n = oracle.num_qubits - 1
    qc = QuantumCircuit(n + 1, n)
    qc.x(n)
    qc.h(range(n + 1))                 # ancilla in |->: the oracle's flip becomes a phase (phase kickback)
    qc.compose(oracle, inplace=True)   # the ONE query
    qc.h(range(n))                     # interference turns the phase pattern back into the bit-string
    qc.measure(range(n), range(n))
    return qc


def run(qc, shots=100, seed=11):
    result = StatevectorSampler(seed=seed).run([qc], shots=shots).result()
    return getattr(result[0].data, qc.cregs[0].name).get_counts()   # register 'c'; read it, don't assume


def classical_queries(secret):
    """Classical baseline: query f on each unit vector e_i, one call per bit (n queries)."""
    n, calls, bits = len(secret), 0, []
    f = lambda x: sum(int(a) * int(b) for a, b in zip(secret, x)) % 2
    for i in range(n):
        calls += 1
        bits.append(str(f("".join("1" if j == i else "0" for j in range(n)))))
    return "".join(bits), calls


if __name__ == "__main__":
    for secret in ("1011", "110101"):
        qc = bv_circuit(bv_oracle(secret))
        found, calls = classical_queries(secret)
        print(f"secret {secret}: quantum counts {run(qc)} (1 query), classical {found} ({calls} queries)")
    print(bv_circuit(bv_oracle("1011")).draw(output="text"))
