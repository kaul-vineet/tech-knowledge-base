"""Lab 12 SDK path: the same seeded noise model in Qiskit Aer (qiskit 2.6.1, qiskit-aer 0.18.2).

Run:  python noise_aer.py      (needs requirements; runs in CI job sdk-labs, not yet observed)
Builds a NoiseModel with depolarizing_error, amplitude_damping_error and ReadoutError (Aer noise docs) and
samples with Aer's SamplerV2. Prints the same metrics as noise_lab.py so the two can be compared line by line.
"""
import json

from qiskit import QuantumCircuit
from qiskit_aer.noise import NoiseModel, ReadoutError, amplitude_damping_error, depolarizing_error
from qiskit_aer.primitives import SamplerV2

import noise_lab as lab


def aer_noise_model(noise):
    damp = amplitude_damping_error(noise["damp"])
    model = NoiseModel()
    # error1.compose(error2) applies error1 first: depolarizing, then damping (same order as noise_lab.noisy_steps)
    model.add_all_qubit_quantum_error(depolarizing_error(noise["p1"], 1).compose(damp), ["h"])
    model.add_all_qubit_quantum_error(depolarizing_error(noise["p2"], 2).compose(damp.tensor(damp)), ["cx"])
    p01, p10 = noise["p01"], noise["p10"]
    model.add_all_qubit_readout_error(ReadoutError([[1 - p01, p01], [p10, 1 - p10]]))   # rows: true 0, true 1
    return model


def ghz(n):
    qc = QuantumCircuit(n)
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    qc.measure_all()
    return qc


def aer_counts(n, noise, shots=20000, seed=7):
    sampler = SamplerV2(seed=seed, options={"backend_options": {"noise_model": aer_noise_model(noise)}})
    return sampler.run([ghz(n)], shots=shots).result()[0].data.meas.get_counts()


def aer_success(n, noise, shots=20000, seed=7):
    c = aer_counts(n, noise, shots, seed)
    return round((c.get("0" * n, 0) + c.get("1" * n, 0)) / shots, 4)


if __name__ == "__main__":
    print("Aer noisy Bell counts (2000 shots):", aer_counts(2, lab.NOISE, shots=2000))
    for n in (2, 3, 4):
        for p2 in (0.0, 0.02, 0.1):
            noise = {**lab.NOISE, "p2": p2}
            print(json.dumps({"n": n, "p2": p2, "aer_success": aer_success(n, noise),
                              "numpy_success": lab.metrics(n, noise)["success"]}))
