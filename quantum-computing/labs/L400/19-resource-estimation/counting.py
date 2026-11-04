"""Gate-level counting helpers for lab 19: build the QAOA circuit as explicit ops, count it, and check the
textbook 7-T Toffoli. Used to VALIDATE the analytic formulas in estimate_lab.py at small n.
"""
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))
from qopt import maxcut as mc  # noqa: E402
from qsim import statevector as sv  # noqa: E402

T, TDG = sv.phase(np.pi / 4), sv.phase(-np.pi / 4)


def edge_colouring(edges):
    """Greedy proper edge colouring: edges with the same colour share no vertex, so they run in parallel."""
    colour = {}
    for e in edges:
        used = {c for f, c in colour.items() if set(f) & set(e)}
        colour[e] = min(set(range(len(edges) + 1)) - used)
    return colour


def qaoa_ops(n, edges, p):
    """Ops as (name, qubits). RZZ = CX . RZ . CX; mixer RX on every qubit; edges ordered by colour."""
    col = edge_colouring(edges)
    ops = [("h", (q,)) for q in range(n)]
    for _ in range(p):
        for e in sorted(edges, key=lambda e: col[e]):
            ops += [("cx", e), ("rz", (e[1],)), ("cx", e)]
        ops += [("rx", (q,)) for q in range(n)]
    return ops


def count(ops, n):
    """Gate counts and ASAP depth (each gate starts after the last gate on any of its qubits)."""
    level = [0] * n
    for _, qs in ops:
        start = max(level[q] for q in qs) + 1
        for q in qs:
            level[q] = start
    names = [g for g, _ in ops]
    return {"qubits": n, "cx": names.count("cx"), "rotations": names.count("rz") + names.count("rx"), "depth": max(level)}


def toffoli_7t():
    """Nielsen & Chuang Fig. 4.9 decomposition (controls 0, 1; target 2): 7 T/T-dagger gates, 6 CX."""
    return [sv.h(2), sv.cx(1, 2), (TDG, 2, ()), sv.cx(0, 2), (T, 2, ()), sv.cx(1, 2), (TDG, 2, ()), sv.cx(0, 2),
            (T, 1, ()), (T, 2, ()), sv.h(2), sv.cx(0, 1), (T, 0, ()), (TDG, 1, ()), sv.cx(0, 1)]


def toffoli_ok():
    ops = toffoli_7t()
    t_count = sum(1 for g, _, _ in ops if g is T or g is TDG)
    exact = sv.unitary(3, [(sv.X, 2, (0, 1))])
    return t_count, bool(np.allclose(sv.unitary(3, ops), exact))


def t_per_rotation(eps):
    """Ross & Selinger (2016): typical T-count 3 log2(1/eps) for one z-rotation to accuracy eps."""
    return math.ceil(3 * math.log2(1 / eps))


__all__ = ["mc", "edge_colouring", "qaoa_ops", "count", "toffoli_ok", "t_per_rotation"]
