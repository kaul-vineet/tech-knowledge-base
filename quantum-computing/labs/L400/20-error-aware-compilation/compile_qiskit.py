"""Lab 20 Qiskit path: the same circuit and the SAME error map in a qiskit Target; transpile at
optimization_level 0-3 (seed_transpiler fixed) and score each result with the lab's ESP and depth.
Run: python compile_qiskit.py   (CI job sdk-labs; not yet observed)

Level 3 uses noise-adaptive layout and VF2PostLayout, which read the per-instruction errors from the Target.
Basis: rz, sx, x, cx (as GenericBackendV2's default), so 1q gates are counted after translation.
"""
import json

from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Parameter
from qiskit.circuit.library import CXGate, Measure, RZGate, SXGate, XGate
from qiskit.transpiler import InstructionProperties, Target

import compile_lab as lab
import device as D


def target(dev):
    t = Target(num_qubits=dev["n"])
    t.add_instruction(CXGate(), {pair: InstructionProperties(error=e) for (a, b), e in dev["cx"].items()
                                 for pair in ((a, b), (b, a))})
    t.add_instruction(RZGate(Parameter("theta")), {(q,): InstructionProperties(error=0.0) for q in range(dev["n"])})
    for gate in (SXGate(), XGate()):
        t.add_instruction(gate, {(q,): InstructionProperties(error=dev["sq"][q]) for q in range(dev["n"])})
    t.add_instruction(Measure(), {(q,): InstructionProperties(error=dev["ro"][q]) for q in range(dev["n"])})
    return t


def circuit():
    qc = QuantumCircuit(lab.NQ)
    for name, qs, arg in lab.logical_ops():
        {"h": lambda: qc.h(*qs), "cx": lambda: qc.cx(*qs), "rz": lambda: qc.rz(arg, *qs), "rx": lambda: qc.rx(arg, *qs)}[name]()
    qc.measure_all()
    return qc


def score(tqc, t):
    esp = 1.0
    for inst in tqc.data:
        name = inst.operation.name
        if name in ("barrier",):
            continue
        qs = tuple(tqc.find_bit(q).index for q in inst.qubits)
        props = t[name].get(qs) if name in t.operation_names else None
        esp *= 1 - ((props.error or 0.0) if props else 0.0)
    return {"esp": round(esp, 4), "cx": tqc.count_ops().get("cx", 0), "depth": tqc.depth(lambda i: i.operation.name != "measure")}


def run(drifted=True):
    dev = D.make_device(drift=D.DRIFT if drifted else None)
    t = target(dev)
    return {level: score(transpile(circuit(), target=t, optimization_level=level, seed_transpiler=7), t) for level in range(4)}


if __name__ == "__main__":
    for level, m in run().items():
        print(json.dumps({"device": "drifted", "optimization_level": level, **m}))
