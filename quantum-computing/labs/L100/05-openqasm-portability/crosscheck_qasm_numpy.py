"""Independent cross-check for lab 05: a tiny OpenQASM reader + numpy statevector.

It understands only a small subset (qubit/qreg declarations, h, x, cx, barrier,
end-of-circuit measure). That is the point: any tool can read the neutral text
format, not just the SDK that wrote it. Unknown statements raise ValueError.
Bit order matches Qiskit: qubit 0 is the rightmost character of a bitstring.
"""
import re
import sys
from pathlib import Path

import numpy as np

GATES_1Q = {
    "h": np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2),
    "x": np.array([[0, 1], [1, 0]], dtype=complex),
}
IGNORED = ("OPENQASM", "include", "bit", "creg", "barrier", "measure")


def _statements(text):
    text = re.sub(r"//[^\n]*", "", text)
    return [s.strip() for s in text.split(";") if s.strip()]


def parse(text):
    """Return (num_qubits, [(gate, [qubit indices])])."""
    offsets, n, ops = {}, 0, []
    for s in _statements(text):
        m = re.fullmatch(r"qubit\[(\d+)\]\s+(\w+)", s) or re.fullmatch(r"qreg\s+(\w+)\[(\d+)\]", s)
        if m:
            size, name = (m.group(1), m.group(2)) if s.startswith("qubit") else (m.group(2), m.group(1))
            offsets[name], n = n, n + int(size)
            continue
        if s.startswith(IGNORED) or "= measure" in s:
            continue
        m = re.fullmatch(r"(\w+)\s+(.+)", s)
        gate = m.group(1).lower() if m else None
        if gate not in ("h", "x", "cx"):
            raise ValueError(f"unsupported statement: {s!r}")
        qubits = []
        for arg in m.group(2).split(","):
            arg = arg.strip()
            phys = re.fullmatch(r"\$(\d+)", arg)               # OpenQASM 3 physical qubit, e.g. $0
            ref = re.fullmatch(r"(\w+)\[(\d+)\]", arg)
            if phys:
                qubits.append(int(phys.group(1)))
                n = max(n, int(phys.group(1)) + 1)
            elif ref:
                qubits.append(offsets[ref.group(1)] + int(ref.group(2)))
            else:
                raise ValueError(f"unsupported operand: {arg!r}")
        ops.append((gate, qubits))
    return n, ops


def probabilities(text):
    n, ops = parse(text)
    state = np.zeros(2**n, dtype=complex)
    state[0] = 1
    for gate, qs in ops:
        new = np.zeros_like(state)
        for i, amp in enumerate(state):
            if amp == 0:
                continue
            if gate == "cx":
                c, t = qs
                new[i ^ (1 << t) if (i >> c) & 1 else i] += amp
            else:
                q = qs[0]
                bit = (i >> q) & 1
                for out_bit in (0, 1):                    # row out_bit, column bit of the 2x2 gate
                    j = (i & ~(1 << q)) | (out_bit << q)
                    new[j] += GATES_1Q[gate][out_bit, bit] * amp
        state = new
    probs = np.abs(state) ** 2
    return {format(i, f"0{n}b"): round(float(p), 12) for i, p in enumerate(probs) if p > 1e-12}


if __name__ == "__main__":
    here = Path(__file__).resolve().parent              # defaults resolve next to this file on any OS
    paths = [Path(p) for p in sys.argv[1:]] or [here / "reference_bell_qasm3.qasm", here / "reference_bell_qasm2.qasm"]
    for path in paths:
        print(f"{path.name}: {probabilities(path.read_text(encoding='utf-8'))}")
