"""Build-task solution for lab 19: choose the code distance from the error budget, and refuse above threshold.

Run: python solution_distance.py
Smallest odd d >= 3 with  logical_qubits x logical_cycles x p_L(d) <= budget,  p_L(d) = 0.03 (p/0.01)^((d+1)/2).
Above the 1 % threshold a larger code is WORSE, so no distance exists: raise instead of returning a number.
"""
import json

import estimate_lab as lab


def choose_distance(p, logical_qubits, cycles, budget=lab.BUDGET, p_th=0.01, d_max=101):
    if p >= p_th:
        raise ValueError(f"physical error {p} is not below the threshold {p_th}: no code distance helps")
    for d in range(3, d_max + 1, 2):
        if logical_qubits * cycles * lab.logical_error(d, p, p_th=p_th) <= budget:
            return d
    raise ValueError(f"no distance <= {d_max} meets budget {budget}")


if __name__ == "__main__":
    for est in lab.WORKLOADS:
        row = lab.physical(est, choose=choose_distance)
        print(json.dumps({k: row[k] for k in ("workload", "logical_qubits", "t_count", "logical_cycles", "distance",
                                              "physical_qubits", "runtime_s", "p_fail")} | {"class": lab.classify(row)}))
