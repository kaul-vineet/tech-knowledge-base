"""Lab 19 QDK path: the same QAOA program through the Microsoft Quantum resource estimator (qdk.qre).
Run: python estimate_qdk.py   (CI job l400-qdk; needs labs/L400/requirements-qdk.txt; not yet observed)

API as documented for qdk.qre (learn.microsoft.com, 'How to install and use the Microsoft Quantum resource
estimator', updated 2026-07-31): an application, a GateBased architecture, an ISA query of SurfaceCode x
RoundBasedFactory and a max_error. Unlike estimate_lab.py it INCLUDES magic-state factories, so its physical
qubit count should be at or above our data-only lower bound. Set QDK_PYTHON_TELEMETRY=none to opt out of telemetry.
"""
import json
import os

import estimate_lab as lab
import solution_distance as sol
from counting import mc, qaoa_ops

os.environ.setdefault("QDK_PYTHON_TELEMETRY", "none")
N, P, ANGLES = 20, 1, (0.6, 0.4)


def qasm3(n=N, p=P):
    """Write the lab's QAOA ops as OpenQASM 3 text (no SDK needed to produce it)."""
    lines = ["OPENQASM 3.0;", 'include "stdgates.inc";', f"qubit[{n}] q;"]
    angle = {"rz": -ANGLES[0], "rx": 2 * ANGLES[1]}
    for g, qs in qaoa_ops(n, mc.regular_graph(n, 3, seed=1), p):
        args = ", ".join(f"q[{x}]" for x in qs)
        lines.append(f"{g}({angle[g]}) {args};" if g in angle else f"{g} {args};")
    return "\n".join(lines) + "\n"


def run_qdk():
    from qdk.qre import estimate
    from qdk.qre.application import OpenQASMApplication
    from qdk.qre.models import GateBased, RoundBasedFactory, SurfaceCode
    arch = GateBased(error_rate=lab.P_PHYS, gate_time=50, measurement_time=100)       # times in ns
    results = estimate(OpenQASMApplication(qasm3()), arch, isa_query=SurfaceCode.q() * RoundBasedFactory.q(),
                       max_error=lab.BUDGET)
    frame = results.as_frame()
    return {"qdk_min_physical_qubits": int(frame["qubits"].min()), "pareto_points": len(frame)}


def ours():
    row = lab.physical(lab.qaoa_logical(N, P), choose=sol.choose_distance)
    return {"ours_physical_qubits_data_only": row["physical_qubits"], "ours_distance": row["distance"]}


if __name__ == "__main__":
    print(json.dumps({**ours(), **run_qdk()}))
