"""Lab 01 - check the quantum toolchain and run a 1-qubit circuit on the local simulator.

Run:  python check_env.py
No cloud account, token or network access is used: Qiskit's reference StatevectorSampler runs on your CPU.
"""
import sys
from importlib import metadata

# Version pinning: SDK APIs change between releases (see labs/L100/requirements.txt).
PINNED = {
    "qiskit": "2.6.1",               # includes the reference primitives (StatevectorSampler) used by every lab
    "qiskit-qasm3-import": "0.6.0",  # needed by qiskit.qasm3.loads (lesson 5)
    "cirq": "1.7.0",                 # optional until lesson 6
    "qiskit-aer": "0.18.2",          # optional equivalent (noise models, speed); reduced-maintenance mode
}
OPTIONAL = {"qiskit-aer"}
BASIS = ["rz", "sx", "x", "cx"]      # a typical hardware gate set (GenericBackendV2's default, lesson 11)


def installed_versions():
    """Return {package: installed version or None}."""
    found = {}
    for name in PINNED:
        try:
            found[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            found[name] = None
    return found


def run_one_qubit(shots=100, seed=7):
    """Build |0> -> X -> measure, transpile it to BASIS and sample it with StatevectorSampler."""
    from qiskit import QuantumCircuit, transpile
    from qiskit.primitives import StatevectorSampler

    qc = QuantumCircuit(1)          # circuit: 1 qubit, starts in |0>
    qc.x(0)            # gate: X = NOT, |0> becomes |1>
    qc.measure_all()   # adds a classical register named "meas"

    compiled = transpile(qc, basis_gates=BASIS)       # transpile: rewrite into gates the target supports
    sampler = StatevectorSampler(seed=seed)           # simulator: holds all 2^n amplitudes in your CPU's memory
    result = sampler.run([compiled], shots=shots).result()   # shots: run + measure `shots` times
    return result[0].data.meas.get_counts()


if __name__ == "__main__":
    print(f"python {sys.version.split()[0]}")
    if sys.version_info < (3, 11):
        sys.exit("Python 3.11+ is required by cirq (lesson 6) and qiskit-aer")
    for name, version in installed_versions().items():
        flag = "OK" if version == PINNED[name] else f"expected {PINNED[name]}"
        if name in OPTIONAL:
            flag += " (optional)"
        print(f"{name:20s} {version or 'missing':10s} {flag}")
    counts = run_one_qubit()
    print("counts:", counts)   # expected: {'1': 100}
