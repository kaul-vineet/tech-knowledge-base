"""Experiment 1 - the Qiskit cross-check that the sandbox could not run: shor_qiskit.py on Qiskit + Aer (arm64 wheels).

Mac mini (zsh), inside the lab venv:
  pip install qiskit==2.6.1 qiskit-aer==0.18.2       # versions pinned by quantum-computing/documentation/README.md
  python mac_mini/qiskit_crosscheck.py
Sandbox / any machine without Qiskit:
  python mac_mini/qiskit_crosscheck.py --here         prints a 'skipped' line, exits 0 (nothing is claimed)

Checks, for N = 15 (a = 7), 21 (a = 2) and 35 (a = 2):
  C1 exact: Qiskit's Statevector counting distribution == shor_sim's numpy distribution (atol 1e-9) - the existing
     shor_qiskit.counting_probs(), unchanged
  C2 sampled: the same circuit + measurements on AerSimulator(method="statevector", seed_simulator=2026), SHOTS shots;
     total-variation distance to the numpy distribution <= TVD_MAX. Sampling noise alone gives a TVD that grows with
     the number of outcomes and shrinks as 1/sqrt(shots): N = 35 has ~130 likely outcomes, so 20k shots would already
     give ~0.026 by chance - hence 100k shots and 0.025 (recomputed in integrated/research/checks_02_mac.py)
and records versions, platform.machine() (expect 'arm64' on Apple silicon) and the wall time of each simulator.
Exit 0 only if every check that ran passed; 0 with status 'skipped' when Qiskit is missing in --here mode; 2 when it
is missing without --here (on the Mac that is an install problem, not a pass).
"""
import argparse
import importlib.util
import platform
import sys
import time

import numpy as np

import _mac

CASES = [(15, 7), (21, 2), (35, 2)]
SHOTS, SEED, TVD_MAX = 100000, 2026, 0.025   # sampling alone: TVD <= ~0.015 at 100k shots (checks_02_mac.py)
INSTALL = "pip install qiskit==2.6.1 qiskit-aer==0.18.2"


def tvd(p, q):
    p, q = np.asarray(p, float), np.asarray(q, float)
    return float(0.5 * np.abs(p / p.sum() - q / q.sum()).sum())


def counts_to_probs(counts, t):
    out = np.zeros(2 ** t)
    for bitstring, c in counts.items():
        out[int(bitstring.replace(" ", ""), 2)] += c
    return out


def aer_probs(modulus, a):
    from qiskit import ClassicalRegister, transpile
    from qiskit_aer import AerSimulator
    import shor_qiskit
    qc, t = shor_qiskit.circuit(modulus, a)
    creg = ClassicalRegister(t, "c")
    qc.add_register(creg)
    qc.measure(range(t), creg)            # qubit j -> clbit j: the bitstring reads like the numpy index
    sim = AerSimulator(method="statevector", seed_simulator=SEED)
    counts = sim.run(transpile(qc, sim), shots=SHOTS).result().get_counts()
    return counts_to_probs(counts, t)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--here", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    missing = [m for m in ("qiskit", "qiskit_aer") if importlib.util.find_spec(m) is None]
    if missing:
        _mac.emit({"experiment": "02 Qiskit cross-check", "status": "skipped", "missing": missing,
                   "install": INSTALL, "machine": platform.machine(), "pendingMac": True}, a.out)
        return 0 if a.here else 2
    import qiskit
    import qiskit_aer
    import shor_qiskit
    import shor_sim
    _mac.emit({"experiment": "02 Qiskit cross-check", "status": "ran", "qiskit": qiskit.__version__,
               "qiskit_aer": qiskit_aer.__version__, "machine": platform.machine(), "python": platform.python_version(),
               "at": _mac.stamp()}, a.out)
    ok = True
    for modulus, base in CASES:
        t0 = time.perf_counter()
        ref = shor_sim.run_order_finding(modulus, base)["probs"]
        t_np = time.perf_counter() - t0
        t0 = time.perf_counter()
        exact = shor_qiskit.counting_probs(modulus, base)
        t_qk = time.perf_counter() - t0
        t0 = time.perf_counter()
        sampled = aer_probs(modulus, base)
        t_aer = time.perf_counter() - t0
        c1 = bool(np.allclose(exact, ref, atol=1e-9))
        d = tvd(sampled, ref)
        ok &= c1 and d <= TVD_MAX
        _mac.emit({"N": modulus, "a": base, "C1_statevector_equal": c1, "C2_aer_tvd": round(d, 4), "tvd_max": TVD_MAX,
                   "shots": SHOTS, "seconds": {"numpy": round(t_np, 3), "qiskit_statevector": round(t_qk, 3),
                                               "aer_sampled": round(t_aer, 3)}, "pass": c1 and d <= TVD_MAX}, a.out)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
