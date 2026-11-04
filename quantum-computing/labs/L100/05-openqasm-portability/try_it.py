"""Try-it checks for lab 05. Run: python try_it.py

Both edits are applied to reference_bell_qasm3.qasm in memory (the file is not changed) and read with the
independent parser. The Qiskit part runs only when qiskit + qiskit-qasm3-import are installed (CI).
"""
import importlib.util
from pathlib import Path

import crosscheck_qasm_numpy as cc

HAVE_QISKIT = all(importlib.util.find_spec(m) for m in ("qiskit", "qiskit_qasm3_import"))
REFERENCE = Path(__file__).resolve().parent / "reference_bell_qasm3.qasm"   # works from any working directory


def edited_text(kind):
    text = REFERENCE.read_text(encoding="utf-8")
    if kind == "swap_control":       # try 1: one token changes the circuit
        return text.replace("cx q[0], q[1];", "cx q[1], q[0];")
    if kind == "add_s_gate":         # try 2: valid stdgates.inc gate outside the tiny parser's subset
        return text.replace("h q[0];", "h q[0];\ns q[0];")
    raise ValueError(kind)


def parser_result(kind):
    try:
        return cc.probabilities(edited_text(kind))
    except ValueError as e:
        return f"ValueError: {e}"


def qiskit_probabilities(kind):
    from qiskit import qasm3
    from qiskit.quantum_info import Statevector
    qc = qasm3.loads(edited_text(kind))
    qc.remove_final_measurements()
    return {k: round(float(v), 12) for k, v in Statevector(qc).probabilities_dict().items() if v > 1e-12}


if __name__ == "__main__":
    for kind in ("swap_control", "add_s_gate"):
        print(f"{kind:12s} parser {parser_result(kind)}")
        if HAVE_QISKIT:
            print(f"{kind:12s} qiskit {qiskit_probabilities(kind)}")
