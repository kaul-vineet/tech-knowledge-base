"""Circuit canonicalisation: equivalent OpenQASM text -> one canonical form -> one cache key.

Front end: the quantum topic's L100 #5 reader (OpenQASM 2/3 subset: qubit/qreg, h, x, cx, final measure of all qubits).
Rules (each keeps the unitary; tests/test_seams.py checks that with the statevector simulator):
  1. registers and names are flattened to qubit indices (q[0], $0, a qreg 'r' all become 0, 1, ...)
  2. adjacent identical self-inverse gates on the same qubits cancel (h h, x x, cx cx with nothing in between)
  3. ops are grouped into ASAP moments and sorted inside a moment (gates on disjoint qubits commute)
"""
import hashlib

from _kb import qasm, sv

SELF_INVERSE = {"h", "x", "cx"}


def cancel_pairs(ops):
    out = []
    for gate, qs in ops:
        last = next((i for i in range(len(out) - 1, -1, -1) if set(out[i][1]) & set(qs)), None)
        if last is not None and gate in SELF_INVERSE and out[last] == (gate, tuple(qs)):
            del out[last]                                  # G G = I: nothing touched these qubits in between
        else:
            out.append((gate, tuple(qs)))
    return out


def moments(n, ops):
    depth, layered = [0] * n, []
    for gate, qs in ops:
        m = max(depth[q] for q in qs)
        for q in qs:
            depth[q] = m + 1
        layered.append((m, gate, qs))
    return [(g, qs) for _, g, qs in sorted(layered)]       # sort inside a moment; moments keep their order


def canonicalise(text):
    """-> (n, ops, canonical_text). Raises ValueError for statements outside the supported subset."""
    n, ops = qasm.parse(text)
    ops = moments(n, cancel_pairs(ops))
    body = ";".join(f"{g} {','.join(map(str, qs))}" for g, qs in ops)
    return n, tuple(ops), f"n={n};{body};measure all"


def circuit_hash(text):
    return hashlib.sha256(canonicalise(text)[2].encode("utf-8")).hexdigest()[:16]


def text_hash(text):
    """The naive key (fault 'text-key'): any whitespace, comment or register-name change is a new circuit."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def to_sv(ops):
    return [sv.cx(*qs) if g == "cx" else (sv.h if g == "h" else sv.x)(qs[0]) for g, qs in ops]


def gate_counts(ops):
    return sum(len(qs) == 1 for _, qs in ops), sum(len(qs) == 2 for _, qs in ops)
