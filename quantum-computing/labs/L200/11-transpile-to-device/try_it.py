"""Try-it checks for lab 11. Run: python try_it.py

The numpy/pure-Python part runs anywhere; the SDK part runs only when qiskit is installed (CI).
"""
import importlib.util

import numpy as np

import crosscheck_numpy as cc
from qsim import statevector as sv

HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None


def ring_vs_line_local():
    """Try 1: add a 'ring' backend (CouplingMap.from_ring(5)). Which star CX pairs still need routing?"""
    return {name: len(cc.non_adjacent(cc.STAR, cc.COUPLING[name])) for name in ("all-to-all", "ring", "line")}


def h_in_basis_local():
    """Try 2: transpile a lone H gate. Which basis gates appear, and is the result still H?"""
    built = sv.rz(np.pi / 2) @ sv.SX @ sv.rz(np.pi / 2)
    k = np.flatnonzero(np.abs(sv.H) > 1e-9)[0]
    turns = np.angle(built.flat[k] / sv.H.flat[k]) / (2 * np.pi)
    return {"gates": ["rz", "sx", "rz"], "equals_H_up_to_phase": sv.equal_up_to_global_phase(built, sv.H),
            "global_phase_turns": round(float(turns), 4)}


def sdk_results():
    from collections import Counter

    from qiskit import QuantumCircuit
    from qiskit.providers.fake_provider import GenericBackendV2
    from qiskit.quantum_info import Operator
    from qiskit.transpiler import CouplingMap, generate_preset_pass_manager

    import transpile_lab
    star = transpile_lab.ghz_star()
    counts = {}
    for name, cmap in (("ring", CouplingMap.from_ring(5)), ("line", CouplingMap.from_line(5))):
        backend = GenericBackendV2(5, coupling_map=cmap, seed=42)
        counts[name] = transpile_lab.two_qubit_count(transpile_lab.transpile_for(star, backend, 0))
    h = QuantumCircuit(1)
    h.h(0)
    pm = generate_preset_pass_manager(optimization_level=0, basis_gates=["id", "rz", "sx", "x", "cx"])
    th = pm.run(h)                     # loose constraint: GenericBackendV2's default basis, no layout
    return {"level0_2q": counts, "h_ops": dict(Counter(i.operation.name for i in th.data)),
            "h_equiv": Operator(th).equiv(Operator(h))}


if __name__ == "__main__":
    print(f"ring_vs_line  local {ring_vs_line_local()}")
    print(f"h_in_basis    local {h_in_basis_local()}")
    if HAVE_QISKIT:
        print(f"qiskit {sdk_results()}")
