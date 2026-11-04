"""Experiment 2 - how many qubits can each backend kind take on THIS machine before memory or time runs out?

python mac_mini/qubit_sweep.py --here      numpy only, small n (statevector 8-18, density matrix 2-6)
python mac_mini/qubit_sweep.py             numpy up to the time cap + the computed walls for this Mac's RAM
python mac_mini/qubit_sweep.py --aer       + Qiskit Aer statevector / density_matrix up to the computed walls
python mac_mini/qubit_sweep.py --ram 32    walls for a simulated 32 GB Mac (the runs still respect this machine)

Circuit: GHZ-n (h, then a cx chain) - the same family the job service runs (canon ops h / x / cx).
Memory maths (computed, mac_profile.py budget): a statevector holds 2^n amplitudes, a density matrix 4^n entries,
16 bytes each (complex128). The numpy density-matrix path the job service uses today (backends.exact_probs -> dm.run)
also builds a full 2^n x 2^n operator per gate and Kraus term, so its TIME grows ~8^n and hits a wall long before RAM.
The output decides the admission rule: a job wider than a backend kind's wall is refused at submit, never queued.
"""
import argparse
import importlib.util
import math
import sys
import time
import tracemalloc

import numpy as np

import _mac
from _kb import dm, noise, sv

NUMPY_SV_SAFETY = 8   # numpy sv.run keeps temporaries next to the state: only try n with 8 x 16 B x 2^n in budget
CAL = {"p1": 0.002, "p2": 0.02, "damp": 0.005, "p01": 0.02, "p10": 0.03}   # backends.fleet() 'flaky-mid'


def ghz(n):
    return [("h", (0,))] + [("cx", (q, q + 1)) for q in range(n - 1)]


def to_sv(ops):
    return [sv.h(qs[0]) if g == "h" else sv.cx(*qs) for g, qs in ops]


def measure(fn):
    tracemalloc.start()
    t0 = time.perf_counter()
    fn()
    secs = time.perf_counter() - t0
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return secs, peak


def numpy_sv(n):
    zero = np.zeros(2 ** n, dtype=complex)
    zero[0] = 1                         # sv.run(n, ops) without a state would build np.eye(2^n)
    return lambda: sv.run(n, to_sv(ghz(n)), zero)


def numpy_dm(n):
    return lambda: dm.run(n, noise.noisy_steps(to_sv(ghz(n)), CAL))


def aer(n, method, budget_mb):
    from qiskit import QuantumCircuit, transpile
    from qiskit_aer import AerSimulator
    qc = QuantumCircuit(n)
    qc.h(0)
    for q in range(n - 1):
        qc.cx(q, q + 1)
    qc.save_probabilities([0])   # forces the full simulation, returns 2 numbers (not a 2^n array to copy)
    sim = AerSimulator(method=method, max_memory_mb=int(budget_mb))
    tqc = transpile(qc, sim, optimization_level=0)
    return lambda: sim.run(tqc).result()


def walls(budget_gb):
    b = budget_gb * 1e9
    return {"statevector_c128": int(math.floor(math.log2(b / 16))),
            "density_matrix_c128": int(math.floor(math.log2(b / 16) / 2)),
            "maths": "16 B x 2^n <= budget; 16 B x 4^n <= budget"}


def sweep(name, make, ns, cap_s, out, per_entry):
    rows = []
    for n in ns:
        try:
            secs, peak = measure(make(n))
        except Exception as e:  # Aer refuses beyond max_memory_mb: that IS the wall, recorded, not hidden
            _mac.emit({"sweep": name, "n": n, "error": f"{type(e).__name__}: {str(e)[:160]}"}, out)
            break
        rows.append({"sweep": name, "n": n, "seconds": round(secs, 4), "peak_traced_B": peak,
                     "bytes_per_entry": round(peak / per_entry(n), 1)})
        _mac.emit(rows[-1], out)
        if secs > cap_s:
            _mac.emit({"sweep": name, "stopped": f"n = {n} took {secs:.1f} s > cap {cap_s} s (time wall)"}, out)
            break
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--here", action="store_true")
    ap.add_argument("--aer", action="store_true", help="also sweep Qiskit Aer (needs qiskit + qiskit-aer)")
    ap.add_argument("--ram", type=float, help="walls for a simulated RAM size (GiB)")
    ap.add_argument("--cap", type=float, default=600.0, help="stop a sweep after a point slower than this (s)")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    if a.here:
        sv_ns, dm_ns, cap = range(8, 19, 2), range(2, 7), 30.0
    else:
        sv_ns, dm_ns, cap = range(10, 31), range(2, 16), a.cap
    by_ram = {g: walls(_mac.mac_profile().recommend(_mac.mac_profile().ram_from_gib(g))["budget_gb"]) for g in (16, 24, 32, 64)}
    _mac.emit({"walls": "computed from mac_profile budgets", "by_ram_GB": by_ram}, a.out)
    this = _mac.profile(a.ram if a.ram else (16 if a.here else None))
    run_budget = this["budget_gb"] if a.here else min(this["budget_gb"], _mac.profile(None)["budget_gb"])
    w = walls(run_budget)
    sv_rows = sweep("numpy statevector", numpy_sv, [n for n in sv_ns if NUMPY_SV_SAFETY * 16 * 2 ** n < run_budget * 1e9], cap,
                    a.out, lambda n: 2 ** n)
    dm_rows = sweep("numpy density matrix (job service path)", numpy_dm, dm_ns, cap, a.out, lambda n: 4 ** n)
    if a.aer:
        if not all(importlib.util.find_spec(m) for m in ("qiskit", "qiskit_aer")):
            _mac.emit({"aer": "skipped", "install": "pip install qiskit==2.6.1 qiskit-aer==0.18.2"}, a.out)
        else:
            mb = run_budget * 1000
            sweep("aer statevector", lambda n: aer(n, "statevector", mb), range(20, w["statevector_c128"] + 2), cap,
                  a.out, lambda n: 2 ** n)
            sweep("aer density_matrix", lambda n: aer(n, "density_matrix", mb), range(4, w["density_matrix_c128"] + 2),
                  cap, a.out, lambda n: 4 ** n)
    last_dm = dm_rows[-1]["n"] if dm_rows else None
    _mac.emit({"decision": "admission limit per backend kind", "ram_gb": this["ram_gb"], "budget_gb": run_budget,
               "aer_statevector_wall": w["statevector_c128"], "aer_density_matrix_wall": w["density_matrix_c128"],
               "numpy_density_matrix_largest_run": last_dm,
               "numpy_dm_seconds_growth_last_step": round(dm_rows[-1]["seconds"] / dm_rows[-2]["seconds"], 1)
               if len(dm_rows) > 1 and dm_rows[-2]["seconds"] > 0 else None,
               "reading": "refuse jobs wider than the wall of the backend kind they would run on; the numpy "
                          "density-matrix path is bounded by time (~8x per qubit), Aer by RAM (4^n / 2^n x 16 B)",
               "mode": "here" if a.here else "mac"}, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
