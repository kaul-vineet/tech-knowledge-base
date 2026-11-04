"""Independent numpy check for lab 11 (no quantum SDK). Run: python crosscheck_numpy.py

What a transpiler must respect, checked without one:
1. basis rewrites keep the unitary (H = RZ(pi/2) SX RZ(pi/2) up to global phase; X = SX SX),
2. a SWAP costs three CX,
3. which CX pairs of a circuit are NOT edges of a coupling map (those need routing).
"""
import itertools
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))
from qsim import statevector as sv  # noqa: E402

N = 5
COUPLING = {   # undirected edge lists, same shapes as CouplingMap.from_line / from_ring / from_full
    "all-to-all": set(itertools.combinations(range(N), 2)),
    "ring": {(i, i + 1) for i in range(N - 1)} | {(0, N - 1)},
    "line": {(i, i + 1) for i in range(N - 1)},
}
STAR = [(0, t) for t in range(1, N)]


def heavy_hex_qubits(d):
    return (5 * d * d - 2 * d - 1) // 2      # CouplingMap.from_heavy_hex docs: n = (5d^2 - 2d - 1) / 2


def non_adjacent(pairs, edges):
    return [p for p in pairs if tuple(sorted(p)) not in edges]


def basis_rewrites():
    h_from_basis = sv.rz(np.pi / 2) @ sv.SX @ sv.rz(np.pi / 2)
    swap = np.eye(4)[[0, 2, 1, 3]]
    return {"H == RZ.SX.RZ (global phase)": sv.equal_up_to_global_phase(h_from_basis, sv.H),
            "X == SX.SX": bool(np.allclose(sv.SX @ sv.SX, sv.X)),
            "SWAP == 3 CX": bool(np.allclose(sv.unitary(2, sv.swap(0, 1)), swap))}


def ghz_probabilities(pairs):
    return sv.probabilities(sv.run(N, [sv.h(0)] + [sv.cx(c, t) for c, t in pairs]))


if __name__ == "__main__":
    print(basis_rewrites())
    for name, edges in COUPLING.items():
        print(f"star CX pairs not on the {name} map: {non_adjacent(STAR, edges)}")
    print("heavy-hex distance 3 has", heavy_hex_qubits(3), "qubits")
    print("star GHZ probabilities:", ghz_probabilities(STAR))
