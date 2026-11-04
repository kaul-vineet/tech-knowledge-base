"""Shor's algorithm in context for lab 21: reuse lesson 19's estimator for RSA and add the ECC formula.

RSA: Gidney & Ekera 2021 (arXiv:1905.09749) logical counts, via labs/L400/19-resource-estimation.
ECC: Roetteler et al. 2017 (arXiv:1706.06752): at most 9n + 2 ceil(log2 n) + 10 logical qubits and
448 n^3 log2 n + 4090 n^3 Toffoli gates for an n-bit prime-field curve.
"""
import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "19-resource-estimation"))   # append: local modules win
import estimate_lab as est  # noqa: E402
import solution_distance as dist  # noqa: E402

CITED = [  # published whole-machine estimates (factories, routing included), p = 1e-3, 1 us cycles
    {"source": "Gidney & Ekera 2019/2021", "target": "RSA-2048", "physical_qubits": 20_000_000, "runtime": "8 hours"},
    {"source": "Gidney 2025", "target": "RSA-2048", "physical_qubits": 1_000_000, "runtime": "under a week",
     "note": "'less than a million'"},
]


def ecc_logical(bits):
    lg = math.log2(bits)
    return {"workload": f"ecc-p{bits}", "logical_qubits": 9 * bits + 2 * math.ceil(lg) + 10,
            "toffoli": round(448 * bits ** 3 * lg + 4090 * bits ** 3)}


def our_model(target="rsa-2048"):
    row = est.physical(est.rsa_logical(2048), choose=dist.choose_distance)
    return {k: row[k] for k in ("workload", "logical_qubits", "distance", "physical_qubits", "runtime_s")}
