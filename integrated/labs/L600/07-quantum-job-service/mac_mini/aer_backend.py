"""Experiment 1 - a real Qiskit Aer backend behind the project's existing Backend interface (backends.Backend).

Mac mini (zsh), in the lab venv:   pip install qiskit==2.6.1 qiskit-aer==0.18.2
  python mac_mini/aer_backend.py            conformance of AerBackend + agreement with the numpy backend +
                                            the 240-job load test with 'slow-clean' served by Aer
  python mac_mini/aer_backend.py --here     no Qiskit needed: runs the SAME conformance checks against the numpy
                                            backend (proves the checks), prints 'aer: skipped'

AerBackend changes only where probabilities and samples come from; admission (fail_rate, outages, slots), latency,
calibration versions and history stay in backends.Backend, so the scheduler, leases and ledger cannot tell them apart.
Noise model = the same three channels as quantum L300 #12 (noise_lab.noisy_steps), attached to gate names:
  after h/x : depolarizing(p1, 1) then amplitude damping(damp)
  after cx  : depolarizing(p2, 2) then amplitude damping(damp) on both qubits
  measure   : ReadoutError [[1 - p01, p01], [p10, 1 - p10]]   (row = true bit, as dm.readout_matrix)
exact_probs: Aer density matrix (save_probabilities, gate noise) x the readout assignment matrix (exact maths, the same
in both backends). execute: Aer samples WITH readout error, seed_simulator derived from the same (seed, chunk, version,
circuit, backend) tuple as the numpy backend, so a re-executed attempt reproduces its counts (lease/fencing contract).
"""
import argparse
import importlib.util
import sys
import zlib

import numpy as np

import _mac
import backends as bk
from _kb import dm

INSTALL = "pip install qiskit==2.6.1 qiskit-aer==0.18.2"
EXACT_TVD_MAX = 1e-6          # two exact computations of the same channel: only float error may differ


def have_aer():
    return all(importlib.util.find_spec(m) for m in ("qiskit", "qiskit_aer"))


def noise_model(cal):
    from qiskit_aer.noise import NoiseModel, ReadoutError, amplitude_damping_error, depolarizing_error
    damp = amplitude_damping_error(cal["damp"])
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(depolarizing_error(cal["p1"], 1).compose(damp), ["h", "x"])
    nm.add_all_qubit_quantum_error(depolarizing_error(cal["p2"], 2).compose(damp.tensor(damp)), ["cx"])
    nm.add_all_qubit_readout_error(ReadoutError([[1 - cal["p01"], cal["p01"]], [cal["p10"], 1 - cal["p10"]]]))
    return nm


def circuit(n, ops, measure):
    from qiskit import QuantumCircuit
    import qiskit_aer  # noqa: F401  (registers QuantumCircuit.save_probabilities)
    qc = QuantumCircuit(n, n if measure else 0)
    for gate, qs in ops:
        getattr(qc, gate)(*qs)        # canonical ops: ("h", (q,)), ("x", (q,)), ("cx", (c, t))
    if measure:
        qc.measure(range(n), range(n))
    else:
        qc.save_probabilities()
    return qc


class AerBackend(bk.Backend):
    """Same dataclass fields as backends.Backend; only exact_probs / execute go to Qiskit Aer."""

    def _sim(self, cal, method):
        from qiskit_aer import AerSimulator
        return AerSimulator(method=method, noise_model=noise_model(cal))  # h, x, cx are native: transpile keeps them

    def exact_probs(self, n, ops, version):
        key = (n, ops, version)
        if key not in self._exact:
            from qiskit import transpile
            c = self.history[version]
            sim = self._sim(c, "density_matrix")
            res = sim.run(transpile(circuit(n, ops, False), sim, optimization_level=0)).result()
            p = np.asarray(res.data(0)["probabilities"], float)
            self._exact[key] = dm.readout_matrix(c["p01"], c["p10"], n) @ p
        return self._exact[key]

    def execute(self, n, ops, version, shots, seed, chunk):
        from qiskit import transpile
        seq = np.random.SeedSequence([seed, chunk, version, zlib.crc32(repr(ops).encode()), zlib.crc32(self.name.encode())])
        sim = self._sim(self.history[version], "density_matrix")
        qc = transpile(circuit(n, ops, True), sim, optimization_level=0)
        counts = sim.run(qc, shots=shots, seed_simulator=int(seq.generate_state(1)[0])).result().get_counts()
        return {k.replace(" ", ""): int(v) for k, v in counts.items()}


def like(b, cls):
    """A copy of backend b (same name, calibration, latency, slots, faults) as another implementation."""
    return cls(b.name, dict(b.cal), b.latency_s, b.slots, b.fail_rate, b.slow_rate, b.slow_factor, b.seed)


GHZ3 = (("h", (0,)), ("cx", (0, 1)), ("cx", (1, 2)))


def conformance(backend, reference=None, shots=4000):
    """The interface contract the job service relies on. Returns {check: bool}."""
    n, ops, v = 3, GHZ3, backend.version
    a = backend.execute(n, ops, v, shots, seed=5, chunk=0)
    out = {"counts_sum_to_shots": sum(a.values()) == shots,
           "keys_are_n_bit_strings": all(len(k) == n and set(k) <= {"0", "1"} for k in a),
           "same_attempt_same_counts": a == backend.execute(n, ops, v, shots, seed=5, chunk=0),
           "next_chunk_new_samples": a != backend.execute(n, ops, v, shots, seed=5, chunk=1)}
    p = backend.exact_probs(n, ops, v)
    out["exact_probs_normalised"] = abs(float(np.sum(p)) - 1) < 1e-9 and float(np.min(p)) >= 0
    emp = np.zeros(2 ** n)
    for k, c in a.items():
        emp[int(k, 2)] += c / shots
    out["samples_match_exact_tvd<0.03"] = 0.5 * float(np.abs(emp - p).sum()) < 0.03
    old = p.copy()
    backend.recalibrate({**backend.cal, "p2": backend.cal["p2"] * 2})
    out["old_version_unchanged_after_recalibration"] = bool(np.allclose(backend.exact_probs(n, ops, v), old))
    out["new_version_differs"] = not np.allclose(backend.exact_probs(n, ops, backend.version), old)
    if reference is not None:
        q = reference.exact_probs(n, ops, reference.version)
        out["exact_tvd_vs_numpy"] = round(0.5 * float(np.abs(old - q).sum()), 9)
        out["agrees_with_numpy_backend"] = out["exact_tvd_vs_numpy"] <= EXACT_TVD_MAX
    return out


def load_test_with_aer():
    """The project's 240-job load test with 'slow-clean' served by Aer (everything else unchanged)."""
    import loadtest
    original = loadtest.bk.fleet

    def fleet(seed=7):
        f = original(seed)
        f[1] = like(f[1], AerBackend)
        return f
    loadtest.bk.fleet = fleet
    try:
        return loadtest.run()
    finally:
        loadtest.bk.fleet = original


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--here", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    base = bk.fleet(7)
    ok = True
    if not have_aer():
        res = conformance(like(base[0], bk.Backend))
        _mac.emit({"conformance": "numpy backends.Backend (proves the checks)", **res, "pass": all(res.values())}, a.out)
        _mac.emit({"aer": "skipped", "install": INSTALL, "pendingMac": True}, a.out)
        return 0 if a.here and all(res.values()) else 2
    import qiskit
    import qiskit_aer
    _mac.emit({"experiment": "07 Aer backend adapter", "qiskit": qiskit.__version__, "qiskit_aer": qiskit_aer.__version__,
               "at": _mac.stamp()}, a.out)
    for b in base:
        res = conformance(like(b, AerBackend), reference=like(b, bk.Backend))
        good = all(v for k, v in res.items() if k != "exact_tvd_vs_numpy")
        ok &= good
        _mac.emit({"conformance": f"AerBackend {b.name}", **res, "pass": good}, a.out)
    m = load_test_with_aer()
    lt_ok = m["shots_exact"] == m["jobs"] and m["contract_violations"] == 0 and m["p95_queue_s"] <= m["budget_p95_s"]
    ok &= lt_ok
    _mac.emit({"load_test": "240 jobs, slow-clean on Aer", **{k: m[k] for k in (
        "jobs", "completed", "shots_exact", "contract_violations", "cache_crossings", "rejected_commits", "p95_queue_s",
        "budget_p95_s", "ci95_coverage", "per_backend")}, "pass": lt_ok}, a.out)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
