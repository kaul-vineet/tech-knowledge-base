"""Recompute every calculation answer and execute every code snippet in content/qbank/*.json (L100-L500)
and content/assessment/concept-inventory.json.

Run:  python research/qbank_checks.py        (numpy only; prints OK and exits 0 when everything matches)
- Calculation answers (and computed values in a few concept/scenario questions) are recomputed here,
  independently of tools/qbank_L*.py: own numpy Grover/QFT/Kraus code, or the labs' own models
  (noise_lab, mitigation_lab, the lab-17 orchestrator, the lab-19 distance chooser) - never typed-in numbers.
- Every code-reading snippet is executed (Python with labs/_shared on sys.path; OpenQASM via a tiny qsim
  interpreter) and its stdout must equal the keyed option. Debugging snippets must reproduce the symptom
  quoted in the question (or print the keyed option).
"""
import contextlib
import io
import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

TOPIC = Path(__file__).resolve().parent.parent
LABS = TOPIC / "labs"
sys.path.insert(0, str(LABS / "_shared"))
from qsim import statevector as sv  # noqa: E402

BANK = {lv: json.loads((TOPIC / "content" / "qbank" / f"{lv}.json").read_text(encoding="utf-8"))
        for lv in ("L100", "L200", "L300", "L400", "L500")}
BANK["concept-inventory"] = json.loads((TOPIC / "content" / "assessment" / "concept-inventory.json").read_text(encoding="utf-8"))
QS = {q["id"]: q for qs in BANK.values() for q in qs}


def lab(*parts):
    path = str(LABS.joinpath(*parts))
    if path not in sys.path:
        sys.path.insert(0, path)


# ---------------- independent helpers ----------------
H1 = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
X1 = np.array([[0, 1], [1, 0]])


def grover_dense(n, marked, k):
    """Matrix Grover: oracle = diag(+-1), diffusion = 2|s><s| - I (bitstrings in q(n-1)...q0 order)."""
    dim = 2 ** n
    s = np.full(dim, 1 / np.sqrt(dim))
    oracle = np.diag([-1.0 if format(i, f"0{n}b") in marked else 1.0 for i in range(dim)])
    diffusion = 2 * np.outer(s, s) - np.eye(dim)
    psi = s.copy()
    for _ in range(k):
        psi = diffusion @ (oracle @ psi)
    return round(float(sum(abs(psi[int(m, 2)]) ** 2 for m in marked)), 4)


def kraus_apply(rho, ops):
    return sum(k @ rho @ k.conj().T for k in ops)


def r(x, nd=4):
    return round(float(x), nd) + 0.0


def calc_checks():
    c = {}
    # ---------- L100 ----------
    c["qc-L100-003"] = lambda: f"{(2 ** 30) * 16 / 2 ** 30:.0f} GiB"
    c["qc-L100-004"] = lambda: str(int(math.log2(8 * 2 ** 30 / 16)))
    c["qc-L100-008"] = lambda: str(round(abs(0.8j) ** 2, 2))
    c["qc-L100-012"] = lambda: f"{np.round((H1 @ X1 @ np.array([1.0, 0.0])), 4).tolist()} - 50/50 odds, minus sign on |1>"
    c["qc-L100-016"] = lambda: str(round(0.25 / 0.01 ** 2))
    c["qc-L100-017"] = lambda: str(r(math.sqrt(0.2 * 0.8 / 400), 3))
    c["qc-L100-018"] = lambda: "{}-{}".format(*(round(2000 + s * 1.96 * math.sqrt(4000 * 0.25)) for s in (-1, 1)))
    c["qc-L100-019"] = lambda: next(o for o in QS["qc-L100-019"]["options"]
                                    if abs(int(o) - 500) > 1.96 * math.sqrt(1000 * 0.25))
    c["qc-L100-026"] = lambda: f"{r(0.5 * -0.5 - 0.5 * 0.5, 2)}, so it is entangled"
    c["qc-L100-040"] = lambda: "".join(reversed("110"))
    # ---------- L200 ----------
    c["qc-L200-006"] = lambda: str(6 + 1)
    c["qc-L200-009"] = lambda: str(grover_dense(3, {"101"}, 1))
    k16 = int(np.argmax([grover_dense(4, {"1011"}, k) for k in range(1, 8)])) + 1   # peak, not the formula
    c["qc-L200-010"] = lambda: f"k = {k16}, P = {grover_dense(4, {'1011'}, k16)}"
    c["qc-L200-011"] = lambda: str(grover_dense(3, {"101"}, 3))

    def same_curve():
        a = [grover_dense(4, {"1011"}, k) for k in range(6)]
        b = [grover_dense(5, {"10110", "00011"}, k) for k in range(6)]
        assert a == b, (a, b)
        return "Success depends only on M/N, and 2/32 = 1/16"
    c["qc-L200-012"] = same_curve
    c["qc-L200-019"] = lambda: str(math.comb(6, 2))

    def qft_peaks():
        state = np.zeros(8, dtype=complex)
        state[[1, 5]] = 1 / np.sqrt(2)
        dft = np.array([[np.exp(2j * np.pi * j * k / 8) for k in range(8)] for j in range(8)]) / np.sqrt(8)
        p = np.abs(dft @ state) ** 2
        return ", ".join(format(i, "03b") for i in range(8) if p[i] > 1e-9)
    c["qc-L200-022"] = qft_peaks

    def ry_values():
        t = np.pi / 3
        amp = np.array([[np.cos(t / 2), -np.sin(t / 2)], [np.sin(t / 2), np.cos(t / 2)]]) @ [1, 0]
        return f"<Z> = {r(amp[0] ** 2 - amp[1] ** 2)}, P(1) = {r(amp[1] ** 2)}"
    c["qc-L200-028"] = ry_values
    c["qc-L200-029"] = lambda: str(r(2 * math.asin(math.sqrt(0.75))))

    def extra_cx_line():
        path = [0, 1, 2, 3, 4]                       # move 0's state until it neighbours 4
        swaps = len(path) - 2
        return str(3 * swaps)
    c["qc-L200-038"] = extra_cx_line
    c["qc-L200-039"] = lambda: str(4 + len(sv.swap(0, 1)) * 2)

    def grover64():
        p = [grover_dense(6, {"101101"}, k) for k in range(10)]
        kopt = int(np.argmax(p))
        return f"P = {p[2]} at k = 2; k_opt = {kopt} gives {p[kopt]}"
    c["qc-L200-047"] = grover64

    # ---------- L300 ----------
    lab("L300", "12-noise-models")
    lab("L300", "13-error-mitigation")
    import mitigation_lab as ml
    import noise_lab as nl

    def bell_metrics():
        m = nl.metrics(2, nl.NOISE)
        return f"fidelity {m['fidelity']}, success {m['success']}"
    c["qc-L300-001"] = bell_metrics
    c["qc-L300-007"] = lambda: str(r(4 * math.sqrt(nl.metrics(2, nl.NOISE)["success"]
                                                  * (1 - nl.metrics(2, nl.NOISE)["success"]) / 2000)))

    def rich_weights():
        s = [1, 3, 5]
        v = np.vander(s, 3, increasing=True)          # solve for weights w with sum w_i s_i^k = [1, 0, 0]
        w = np.linalg.solve(v.T, [1.0, 0.0, 0.0])
        return ", ".join(f"{'+' if x > 0 else '-'}{abs(round(x * 8))}/8" for x in w)
    c["qc-L300-012"] = rich_weights

    def zne():
        y = [r(ml.exact_value(s)) for s in (1, 3, 5)]
        rich = np.polyval(np.polyfit([1, 3, 5], y, 2), 0)
        lin = np.polyval(np.polyfit([1, 3, 5], y, 1), 0)
        return f"Richardson {r(rich)}, linear {r(lin)}"
    c["qc-L300-013"] = zne
    c["qc-L300-014"] = lambda: str(r(np.linalg.norm(np.linalg.solve(np.vander([1, 3, 5], 3, increasing=True).T,
                                                                     [1.0, 0.0, 0.0])), 2))
    c["qc-L300-016"] = lambda: str(sum(5 if op[2] else 0 for op in ml.mirror_ops()))

    edges = [(0, 1), (0, 2), (0, 4), (1, 2), (2, 3), (3, 4)]
    cuts = np.array([sum(((z >> i) & 1) != ((z >> j) & 1) for i, j in edges) for z in range(32)])
    c["qc-L300-022"] = lambda: f"cut {cuts.max()}, {int((cuts == cuts.max()).sum())} strings"
    c["qc-L300-024"] = lambda: str(r(cuts.mean() / cuts.max()))

    pauli = {"I": np.eye(2), "Z": np.diag([1.0, -1.0]), "X": X1.astype(float)}
    terms = {"II": -1.05, "ZI": 0.39, "IZ": -0.39, "ZZ": -0.01, "XX": 0.18}
    ham = sum(cf * np.kron(pauli[k[0]], pauli[k[1]]) for k, cf in terms.items())

    def best_basis():
        d = np.diag(ham)
        return f"'{format(int(np.argmin(d)), '02b')}' with {r(d.min())}"
    c["qc-L300-032"] = best_basis
    c["qc-L300-033"] = lambda: f"{r(0.01 / 0.002, 3)} vs {r(0.01 / 0.2, 3)}"
    c["qc-L300-034"] = lambda: f"{2 * 400} vs 2"
    c["qc-L300-040"] = lambda: str(r(math.sqrt(2) / 2 / math.sqrt(4000)))
    c["qc-L300-042"] = lambda: f"{60 * 40 * (1 + 2 * 4):,}"

    # ---------- L400 ----------
    lab("L400", "17-hybrid-architecture")
    lab("L400", "19-resource-estimation")

    def batched_q10():
        import orchestrator as orch
        import solution_cache_key as fixed
        from backend import Costs, FakeClock, SimulatorBackend
        clock = FakeClock()
        backend = SimulatorBackend(clock, costs=Costs(queue_s=10.0))
        o = orch.Orchestrator(backend, clock, "batched", fixed.cache_key)
        orch.spsa_multistart(o, orch.WORKLOAD)
        return f"{round(clock.now, 2)} s"
    c["qc-L400-001"] = batched_q10

    def billed():
        import orchestrator as orch
        import solution_cache_key as fixed
        rows = [orch.run(m, key=fixed.cache_key) for m in ("sync", "batched")]
        assert rows[0]["billed_s"] == rows[1]["billed_s"]
        return f"{rows[0]['billed_s']} s for both"
    c["qc-L400-002"] = billed
    c["qc-L400-009"] = lambda: str(round(200 * math.log(0.01) / math.log(0.7)))
    c["qc-L400-012"] = lambda: str(r(math.sqrt(0.4 * 0.6 / 10), 2))

    def rsa():
        import estimate_lab as est
        import solution_distance as dist
        row = est.physical(est.rsa_logical(2048), choose=dist.choose_distance)
        assert row["distance"] == 27
        return f"{row['physical_qubits']:,}", f"{r(row['runtime_s'] / 3600, 1)} hours"
    c["qc-L400-017"] = lambda: rsa()[0]
    c["qc-L400-020"] = lambda: rsa()[1]

    def d50():
        import solution_distance as dist
        d = dist.choose_distance(1e-3, 50, 10_000)
        return f"d = {d}, {50 * 2 * d * d:,} physical"
    c["qc-L400-018"] = d50

    def t_rot():
        import counting
        return str(counting.t_per_rotation(1e-6))
    c["qc-L400-021"] = t_rot
    c["qc-L400-026"] = lambda: str(r(np.prod([0.99] * 12 + [0.98] * 5)))
    c["qc-L400-027"] = lambda: f"Detour: {r(np.prod([0.99] * 4))} vs {r(0.85)}"
    c["qc-L400-028"] = lambda: f"{math.factorial(8) // math.factorial(3):,}"
    c["qc-L400-035"] = lambda: ", ".join(k for k, x in [("archive (10 years)", 10), ("replication (7 years)", 7),
                                                        ("telemetry (5 years)", 5), ("chat (1 year)", 1)] if x + 3 > 9)
    c["qc-L400-037"] = lambda: f"{1184 + 32} / {1088 + 32} bytes"

    def ecc():
        lab("L400", "21-post-quantum-migration")
        lg = math.log2(256)
        return str(9 * 256 + 2 * math.ceil(lg) + 10)
    c["qc-L400-038"] = ecc
    c["qc-L400-044"] = lambda: str(r((6.8549 - 6.774) / (7.3525 - 6.774), 2))

    # ---------- L500 (lessons 23-27) ----------
    c["qc-L500-002"] = lambda: str(r(abs(np.vdot(np.array([math.sqrt(3), 1]) / 2, H1 @ [1.0, 0.0])) ** 2))
    c["qc-L500-005"] = lambda: str(r(math.cos(0.0 - math.pi / 6) ** 2, 2))

    def purity_a():
        psi = np.sqrt(0.9) * np.kron([1, 0], [1, 0]) + np.sqrt(0.1) * np.kron([0, 1], [0, 1])
        rho_a = np.einsum("abcb->ac", np.outer(psi, psi).reshape(2, 2, 2, 2))
        return str(r(np.trace(rho_a @ rho_a).real, 2))
    c["qc-L500-014"] = purity_a

    def grover256():
        target = {"10110101"}
        p = [grover_dense(8, target, k) for k in range(0, 20)]
        k = int(np.argmax(p))
        return f"k = {k}, P = {p[k]}"
    c["qc-L500-019"] = grover256

    def shor15():
        a, n = 7, 15
        r_, y = 1, a
        while y != 1:
            y, r_ = y * a % n, r_ + 1
        h = pow(a, r_ // 2, n)
        return f"r = {r_}; factors {math.gcd(h - 1, n)} and {math.gcd(h + 1, n)}"
    c["qc-L500-022"] = shor15
    c["qc-L500-026"] = lambda: f"r = {Fraction(192, 256).limit_denominator(15).denominator}"
    c["qc-L500-028"] = lambda: f"At risk: X + Y = {7 + 5} > 10, exposed for {7 + 5 - 10} years"

    def grover_million():
        theta = math.asin(1e-3)
        ks = range(600, 1000)
        best = max(ks, key=lambda k: math.sin((2 * k + 1) * theta) ** 2)
        assert best == math.floor(math.pi / (4 * theta))
        return str(best)
    c["qc-L500-038"] = grover_million
    c["qc-L500-042"] = lambda: str(r(np.prod(np.full(500, 1 - 0.002))))
    c["qc-CI-13"] = lambda: str(r(math.cos(math.pi / 3) ** 2, 2))
    c["qc-CI-15"] = lambda: f"{2 ** 30 * 16 // 2 ** 30} GiB"                      # 2^30 amplitudes x 16 bytes
    return c


# ---------------- snippet execution ----------------
def run_python(code):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(code, "<snippet>", "exec"), {"__name__": "__main__"})
    return buf.getvalue().strip()


def run_qasm(code):
    """Tiny OpenQASM 3 interpreter for h / x / cx on one register; returns ideal probabilities (Qiskit order)."""
    n, ops = None, []
    for line in code.splitlines():
        line = line.strip().rstrip(";")
        if m := re.fullmatch(r"qubit\[(\d+)\] q", line):
            n = int(m.group(1))
        elif m := re.fullmatch(r"(h|x) q\[(\d+)\]", line):
            ops.append(getattr(sv, m.group(1))(int(m.group(2))))
        elif m := re.fullmatch(r"cx q\[(\d+)\], q\[(\d+)\]", line):
            ops.append(sv.cx(int(m.group(1)), int(m.group(2))))
        elif line and not line.startswith(("OPENQASM", "include", "bit[", "c = measure")):
            raise ValueError(f"unsupported OpenQASM line: {line}")
    return str(sv.probabilities(sv.run(n, ops)))


def main():
    errors, n_calc, n_code = [], 0, 0
    checks = calc_checks()
    for qid, q in QS.items():
        keyed = q["options"][q["answer"]]
        if q["type"] == "calculation" and qid not in checks:
            errors.append(f"{qid}: calculation without a recomputation")
        if qid in checks:
            n_calc += 1
            got = checks[qid]()
            if got != keyed:
                errors.append(f"{qid}: recomputed {got!r} != keyed {keyed!r}")
            if sum(o == got for o in q["options"]) != 1:
                errors.append(f"{qid}: recomputed value appears {sum(o == got for o in q['options'])} times")
        if "code" in q:
            n_code += 1
            code = q["code"]
            if len(code.splitlines()) > 15:
                errors.append(f"{qid}: snippet longer than 15 lines")
            out = run_qasm(code) if code.lstrip().startswith("OPENQASM") else run_python(code)
            if q["type"] == "code-reading" and out != keyed:
                errors.append(f"{qid}: snippet printed {out!r}, keyed {keyed!r}")
            if q["type"] == "debugging" and out != keyed and out not in q["question"]:
                errors.append(f"{qid}: snippet printed {out!r}, symptom not in question")
            others = [o for i, o in enumerate(q["options"]) if i != q["answer"]]
            if q["type"] == "code-reading" and out in others:
                errors.append(f"{qid}: output also matches a distractor")
    unused = set(checks) - set(QS)
    if unused:
        errors.append(f"checks for unknown ids: {sorted(unused)}")
    for e in errors:
        print("FAIL", e)
    print(f"{len(QS)} questions; {n_calc} computed answers recomputed; {n_code} snippets executed")
    if errors:
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
