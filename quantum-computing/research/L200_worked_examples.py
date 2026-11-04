"""Computes every number used in the L200 concept notes (content/concepts/L200/*.md).

Run from the domain folder:  python research/L200_worked_examples.py
Output is recorded in research/L200_worked_examples.out.txt. numpy only (imports the labs' numpy cross-checks).
"""
import importlib.util
import math
from pathlib import Path

import numpy as np

LABS = Path(__file__).resolve().parent.parent / "labs" / "L200"


def load(lab, module):
    import sys
    sys.path.insert(0, str(LABS / lab))
    spec = importlib.util.spec_from_file_location(f"{lab}_{module}", LABS / lab / f"{module}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sys.path.pop(0)
    return mod


bv = load("07-bernstein-vazirani", "crosscheck_numpy")
print("[07] secret 1011 ->", bv.bv_probabilities("1011"), "| no |-> ancilla ->", bv.bv_probabilities("1011", kickback=False))
print("[07] all 4-bit secrets found:", bv.all_secrets_found(4), "| classical queries for 1011 and 110101: 4 and 6")

gr = load("08-grover-search", "crosscheck_numpy")
theta = math.asin(math.sqrt(1 / 8))
print(f"[08] N=8 M=1 theta={theta:.4f} rad, optimal k={gr.optimal_iterations(1, 3)},",
      "P by k:", [gr.success(["101"], k) for k in range(5)])
print("[08] N=4 M=1 k=1:", gr.success(["11"], 1), "| N=8 M=2 k=1,2:", gr.success(["011", "100"], 1), gr.success(["011", "100"], 2))
print("[08] oracle diagonal for 011,100:", gr.oracle_gates_diagonal(["011", "100"]))

qf = load("09-qft-building-block", "crosscheck_numpy")
from qsim import statevector as sv  # noqa: E402  (path added by the cross-check modules)
state = sv.run(3, [sv.x(0), sv.x(2)] + qf.qft_ops(3))
print("[09] QFT|5> magnitude", round(float(abs(state[0])), 4), "phases (turns)", np.round(np.angle(state) / (2 * np.pi) % 1, 4).tolist())
print("[09] gate counts n=3: H 3, CP", sum(1 for op in sv.flatten(qf.qft_ops(3)) if op[2] and not np.allclose(op[0], sv.X)), ", SWAP 1;",
      "CP for n qubits = n(n-1)/2")
print("[09] max |QFT gates - DFT|:", qf.max_error(sv.unitary(3, qf.qft_ops(3)), qf.dft_matrix(3)))

pc = load("10-parameterized-circuits", "crosscheck_numpy")
z, x = pc.exact()
print("[10] fit exact <Z>", pc.fit_cos_sin(pc.THETAS, z), "| fit 400 shots", pc.fit_cos_sin(pc.THETAS, pc.sampled_z()),
      "| fit 25 shots", pc.fit_cos_sin(pc.THETAS, pc.sampled_z(shots=25)))
print("[10] shot-noise std of one <Z> estimate at theta=pi/2: 400 shots", round(1 / math.sqrt(400), 3), "25 shots", round(1 / math.sqrt(25), 3))

tr = load("11-transpile-to-device", "crosscheck_numpy")
print("[11]", tr.basis_rewrites())
print("[11] star pairs needing routing: line", tr.non_adjacent(tr.STAR, tr.COUPLING["line"]),
      "ring", tr.non_adjacent(tr.STAR, tr.COUPLING["ring"]), "| heavy-hex d=3 qubits", tr.heavy_hex_qubits(3))
