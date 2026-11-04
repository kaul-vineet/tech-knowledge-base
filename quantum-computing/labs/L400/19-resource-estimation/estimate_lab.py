"""Lab 19 - resource estimation: from problem size to logical and physical qubits, depth, CX and T counts.

Run:  python estimate_lab.py     (numpy/stdlib only; prints JSON lines)
1. Logical counts for QAOA MaxCut on 3-regular graphs (formulas, validated against counted circuits for n <= 12).
2. Shor/RSA logical counts from Gidney & Ekera (2021, arXiv:1905.09749) abstract formulas.
3. Surface-code overhead: p_L(d) = 0.03 (p / 0.01)^((d+1)/2) per logical qubit per logical cycle (Fowler et al.
   2012 Eq. 11; the defaults of qdk.qre's SurfaceCode), about 2 d^2 physical qubits per logical qubit
   (d^2 data + d^2 - 1 measure). Data blocks only: no magic-state factories, no routing -> a LOWER bound.
4. A feasibility class per workload. The FAULT: choose_distance() below uses a fixed d = 3 ("17 physical per logical").
QDK path (qdk.qre estimator on the same QAOA program): python estimate_qdk.py   (CI job l400-qdk)
"""
import json
import math

from counting import t_per_rotation

P_PHYS, CYCLE_S, BUDGET = 1e-3, 1e-6, 0.01        # gate error, surface-code cycle (1 us), total failure budget
THRESHOLDS = {"sim_qubits": 30, "nisq_esp": 0.5, "max_physical": 1_000_000, "max_runtime_s": 86_400}


def qaoa_logical(n, p, colours=4, eps_total=1e-3):
    edges = 3 * n // 2
    rotations = p * (edges + n)
    t_rot = t_per_rotation(eps_total / rotations)                   # synthesis error shared by all rotations
    depth = 1 + p * (3 * colours + 1)                                # colour groups of RZZ run in parallel
    return {"workload": f"qaoa n={n} p={p}", "logical_qubits": n, "cx": 2 * edges * p, "rotations": rotations,
            "depth": depth, "t_count": rotations * t_rot,
            "logical_cycles": depth + p * (colours + 1) * t_rot}       # each rotation layer = t_rot T steps


def rsa_logical(bits):
    lg = math.log2(bits)
    toffoli = 0.3 * bits ** 3 + 0.0005 * bits ** 3 * lg
    out = {"workload": f"rsa-{bits}", "logical_qubits": math.ceil(3 * bits + 0.002 * bits * lg),
            "toffoli": round(toffoli), "t_count": 7 * round(toffoli),      # 7 T per Toffoli (counting.toffoli_ok)
            "depth": round(500 * bits ** 2 + bits ** 2 * lg)}              # measurement depth
    out["logical_cycles"] = out["depth"]
    return out


def logical_error(d, p=P_PHYS, a=0.03, p_th=0.01):
    return a * (p / p_th) ** ((d + 1) / 2)


def choose_distance(p, logical_qubits, cycles, budget=BUDGET):
    """NAIVE: one fixed code distance for every workload ('a logical qubit is 17 physical qubits')."""
    return 3


def physical(est, p=P_PHYS, choose=choose_distance):
    cycles = est["logical_cycles"]
    d = choose(p, est["logical_qubits"], cycles)
    fail = min(1.0, est["logical_qubits"] * cycles * logical_error(d, p))
    return {**est, "distance": d, "physical_qubits": est["logical_qubits"] * 2 * d * d,
            "runtime_s": float(f"{cycles * d * CYCLE_S:.4g}"), "p_fail": float(f"{fail:.3g}")}


def classify(est):
    """Code decides: run where the estimate says it can run."""
    esp = (1 - P_PHYS) ** est.get("cx", math.inf)
    if est["logical_qubits"] <= THRESHOLDS["sim_qubits"]:
        return "simulate"
    if esp >= THRESHOLDS["nisq_esp"]:
        return "nisq-candidate"
    if est["physical_qubits"] <= THRESHOLDS["max_physical"] and est["runtime_s"] <= THRESHOLDS["max_runtime_s"]:
        return "fault-tolerant-feasible"
    return "infeasible (assumptions above)"


WORKLOADS = [qaoa_logical(20, 1), qaoa_logical(100, 1), qaoa_logical(100, 4), qaoa_logical(1000, 10),
             rsa_logical(1024), rsa_logical(2048)]

if __name__ == "__main__":
    for est in WORKLOADS:
        row = physical(est)
        print(json.dumps({**row, "class": classify(row)}))
