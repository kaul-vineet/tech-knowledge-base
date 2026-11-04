"""Validate content/L500.json (lessons 23-27) and recompute every number in its problem sets.

Run:  python research/l500_checks.py          (numpy only; prints OK and exits 0 when everything matches)
1. Structure (kb/L500-SPEC.md): fields, 3-5 Bloom-verb objectives, 2-4 theorems (23-25), 6-10 problems, rubric weights = 100,
   case study (26), two readings with 5 guiding questions (27), concept-note word counts, seeAlso titles that exist exactly.
2. Theorems: re-runs every `check` (labs/L500/<lab>/theorems.py::<id>); its output must equal `checkOutput` and appear
   in the lab README's expected output. 4. Exams: numbers in content/assessment/midterm.md and final.md are recomputed.
3. Problem sets: every calculation problem (and the numeric parts of some others) is recomputed here, independently of the
   lesson text; each recomputed string must appear in the written solution.
"""
import importlib.util
import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

TOPIC = Path(__file__).resolve().parent.parent
LESSONS = json.loads((TOPIC / "content" / "L500.json").read_text(encoding="utf-8"))
EARLIER = {l["number"]: l for lv in ("L100", "L200", "L300", "L400")
           for l in json.loads((TOPIC / "content" / f"{lv}.json").read_text(encoding="utf-8"))}
BLOOM = ("explain", "derive", "prove", "analyze", "analyse", "evaluate", "critique", "compare", "justify", "interpret")
PROBLEM_TYPES = {"derivation", "proof", "calculation", "short-answer", "essay"}
WORDS = {23: (900, 1300), 24: (900, 1300), 25: (900, 1300), 26: (700, 1000), 27: (500, 800)}
LESSON_FIELDS = ("id", "number", "level", "title", "category", "description", "outcome", "estimatedTime", "prerequisites",
                 "glossary", "conceptNote", "conceptSummary", "sources", "seeAlso", "next", "platforms", "validation",
                 "learningObjectives", "problemSet", "rubric")

H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
X = np.array([[0, 1], [1, 0]])
Y = np.array([[0, -1j], [1j, 0]])
Z = np.diag([1, -1])
I2 = np.eye(2)
CX = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])        # control = left factor (textbook order)
KET = {"00": np.array([1, 0, 0, 0]), "01": np.array([0, 1, 0, 0]), "10": np.array([0, 0, 1, 0]), "11": np.array([0, 0, 0, 1])}
BELL = {"Φ+": (KET["00"] + KET["11"]) / np.sqrt(2), "Φ-": (KET["00"] - KET["11"]) / np.sqrt(2),
        "Ψ+": (KET["01"] + KET["10"]) / np.sqrt(2), "Ψ-": (KET["01"] - KET["10"]) / np.sqrt(2)}


def f4(x):
    return f"{round(float(x), 4) + 0.0:.4f}"


def grover_p(n_items, m, k):
    t = math.asin(math.sqrt(m / n_items))
    return math.sin((2 * k + 1) * t) ** 2


def grover_k(n_items, m):
    return math.floor(math.pi / (4 * math.asin(math.sqrt(m / n_items))))


def qpe_p(phi, t, m):
    big_t = 2 ** t
    return abs(sum(np.exp(2j * np.pi * k * (phi - m / big_t)) for k in range(big_t))) ** 2 / big_t ** 2


def load_lab(lab_file):
    path = TOPIC / lab_file
    spec = importlib.util.spec_from_file_location(f"l500_{path.parent.name.replace('-', '_')}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def problem_checks():
    c = {}
    psi, phi = np.array([1, 1j]) / np.sqrt(2), np.array([1, 1]) / np.sqrt(2)
    ip = np.vdot(psi, phi)
    c["qc-L500-23-P1"] = lambda: [f"{ip.real:.1f} - {-ip.imag:.1f}i", f"= {abs(ip) ** 2:.1f}"]

    def p3():
        v = np.kron(np.array([1, 1]) / np.sqrt(2), np.array([np.sqrt(3) / 2, 0.5]))
        return ["(" + ", ".join(f4(x) for x in v) + ")", f"P(11) = (1/(2√2))^2 = {v[3] ** 2:.3f}",
                f"{v[2] ** 2:.3f} + {v[3] ** 2:.3f} = {v[2] ** 2 + v[3] ** 2:.1f}"]
    c["qc-L500-23-P3"] = p3
    c["qc-L500-23-P5"] = lambda: [f"cos^2(π/8) = {f4(math.cos(math.pi / 8) ** 2)}", f"cos(π/4) = {f4(math.cos(math.pi / 4))}",
                                  f"cos^2(π/4) = {math.cos(math.pi / 4) ** 2:.1f}"]

    def p6():
        ry = np.array([[math.cos(math.pi / 6), -math.sin(math.pi / 6)], [math.sin(math.pi / 6), math.cos(math.pi / 6)]])
        v = ry @ [1, 0]
        return [f"({f4(v[0])}, {v[1]:.1f})", f"P(1) = sin^2(π/6) = {v[1] ** 2:.2f}", f"P(0) = {v[0] ** 2:.2f}",
                f"<Z> = P(0) - P(1) = {v[0] ** 2 - v[1] ** 2:.1f}"]
    c["qc-L500-23-P6"] = p6

    def p7():
        u = np.kron(H, I2) @ CX
        out = []
        for name in ("Φ+", "Φ-", "Ψ+", "Ψ-"):
            w = u @ BELL[name]
            (label,) = [k for k, e in KET.items() if abs(abs(np.vdot(e, w)) - 1) < 1e-12]
            out.append(f"{name} -> |{label}>")
        return [", ".join(out)]
    c["qc-L500-23-P7"] = p7

    def p8():
        b = BELL["Φ+"]
        val = {n: np.vdot(b, o @ b).real for n, o in
               (("Z⊗Z", np.kron(Z, Z)), ("X⊗X", np.kron(X, X)), ("Y⊗Y", np.kron(Y, Y)), ("Z⊗I", np.kron(Z, I2)))}
        return [", ".join(f"<{n}> = {round(v) + 0}" for n, v in val.items())]
    c["qc-L500-23-P8"] = p8
    c["qc-L500-23-P9"] = lambda: [f"norm √2 = {f4(np.linalg.norm(np.array([[1, 1], [0, 1]]) @ [0, 1]))}",
                                  f"sum to {np.linalg.norm(np.array([[1, 1], [0, 1]]) @ [0, 1]) ** 2:.1f}"]

    plus = np.array([1, 1]) / np.sqrt(2)
    c["qc-L500-24-P1"] = lambda: [f"1/√2 = {f4(np.vdot([1, 0], plus).real)}", f"squared {np.vdot([1, 0], plus).real ** 2:.1f}"]

    def p24_3():
        cc, ss = math.cos(math.pi / 8), math.sin(math.pi / 8)
        z = np.array([cc, -ss])
        xz = X @ z
        return ["0.25 each", f"P(1) = cos^2(π/8) = {f4(abs(xz[1]) ** 2)}", f"P(1) = sin^2(π/8) = {f4(ss ** 2)}"]
    c["qc-L500-24-P3"] = p24_3

    def p24_4():
        phi_plus = BELL["Φ+"]
        assert abs(abs(np.vdot(BELL["Ψ+"], np.kron(X, I2) @ phi_plus)) - 1) < 1e-12
        assert abs(abs(np.vdot(BELL["Φ-"], np.kron(Z, I2) @ phi_plus)) - 1) < 1e-12
        assert np.allclose(np.kron(Z @ X, I2) @ phi_plus, BELL["Ψ-"])
        return ["(ZX ⊗ I)|Φ+> = (|01> - |10>)/√2 = |Ψ->"]
    c["qc-L500-24-P4"] = p24_4

    def p24_5():
        f = {(0, 0): 0, (0, 1): 1, (1, 0): 1, (1, 1): 0}
        a0 = sum((-1) ** v for v in f.values()) / 4
        return [f"P(00) = {abs(a0) ** 2:.0f}", f"2^9 + 1 = {2 ** 9 + 1}"]
    c["qc-L500-24-P5"] = p24_5

    def p24_6():
        lam = np.array([0.8, 0.2])
        return [f"Purity = 0.64 + 0.04 = {np.sum(lam ** 2):.2f}", f"= {f4(-np.sum(lam * np.log2(lam)))} bits"]
    c["qc-L500-24-P6"] = p24_6

    def p24_7():
        rho = 0.5 * np.outer([1, 0], [1, 0]) + 0.5 * np.outer(plus, plus)
        vals, vecs = np.linalg.eigh(rho)
        top = vecs[:, 1] * np.sign(vecs[0, 1])
        assert np.allclose(top, [math.cos(math.pi / 8), math.sin(math.pi / 8)])
        return [f"= {f4(vals[1])} and {f4(vals[0])}", f"purity = {f4(vals[1])}^2 + {f4(vals[0])}^2 = {np.sum(vals ** 2):.2f}"]
    c["qc-L500-24-P7"] = p24_7

    def p24_8():
        cc, ss = math.cos(math.pi / 6), math.sin(math.pi / 6)
        return [f"(c^3 + s^3)^2 = {f4((cc ** 3 + ss ** 3) ** 2)}", f"c^4 + s^4 = {f4(cc ** 4 + ss ** 4)}"]
    c["qc-L500-24-P8"] = p24_8

    def p25_1():
        k = grover_k(1024, 1)
        return [f"θ = asin(1/32) = {math.asin(1 / 32):.5f}", f"= {k},", f"P_{k} = sin^2({2 * k + 1}θ) = {f4(grover_p(1024, 1, k))}",
                f"P_26 = {f4(grover_p(1024, 1, 26))}", f"P_50 = {f4(grover_p(1024, 1, 50))}"]
    c["qc-L500-25-P1"] = p25_1

    def p25_2():
        k = grover_k(1024, 4)
        return [f"= {k} (half", f"P_{k} = {f4(grover_p(1024, 4, k))}", f"P_25 = {f4(grover_p(1024, 4, 25))}"]
    c["qc-L500-25-P2"] = p25_2

    def p25_5():
        p = [qpe_p(1 / 3, 3, m) for m in range(8)]
        order = np.argsort(p)[::-1]
        return [f"m = {order[0]} ({order[0]}/8 = {order[0] / 8}) with P = {f4(p[order[0]])}", f"m = {order[1]} ({order[1] / 8}) with P = {f4(p[order[1]])}",
                f"4/π^2 = {f4(4 / math.pi ** 2)}"]
    c["qc-L500-25-P5"] = p25_5

    def p25_6():
        powers = [pow(2, k, 21) for k in range(1, 7)]
        r = powers.index(1) + 1
        h = pow(2, r // 2, 21)
        return [", ".join(map(str, powers)) + f", so r = {r}", f"gcd({h} - 1, 21) = {math.gcd(h - 1, 21)} and gcd({h} + 1, 21) = {math.gcd(h + 1, 21)}"]
    c["qc-L500-25-P6"] = p25_6

    def p25_7():
        cf = Fraction(427, 512).limit_denominator(21)
        lab = load_lab("labs/L500/25-algorithms-and-complexity/theorems.py")
        dist = lab.order_finding_distribution(2, 21, 9)
        p_ok = sum(p for m, p in enumerate(dist) if lab.recovered_order(m, 9, 2, 21) == 6)
        return [f"limit_denominator(21) = {cf}", f"2^{cf.denominator} mod 21 = {pow(2, cf.denominator, 21)}", f"P = {f4(p_ok)}"]
    c["qc-L500-25-P7"] = p25_7
    c["qc-L500-25-P8"] = lambda: [f"= {2 ** 40 * 16:,} bytes = {2 ** 40 * 16 // 2 ** 40} TiB ({2 ** 40 * 16 / 1e12:.1f} TB)"]
    c["qc-L500-25-P10"] = lambda: [f"= {f4(sum(math.comb(15, k) * (2 / 3) ** k * (1 / 3) ** (15 - k) for k in range(8)))}"]

    c["qc-L500-26-P1"] = lambda: [f"X + Y = {10 + 6} > Z = 12", f"16 - 12 = {16 - 12} years", f"X + Y = {10 + 2}"]
    c["qc-L500-26-P2"] = lambda: [f"2026 + 25 = {2026 + 25}", f"2051 - 2040 = {2026 + 25 - 2040} years"]

    def p26_6():
        hours = 10_000 * 365.25 * 24
        return [f"= {hours:,.0f} hours", f"/ 15 = {hours / 15:,.0f}", f"15 hours = {15 * 3600:,} s", f"which is {15 * 3600 // 200} times"]
    c["qc-L500-26-P6"] = p26_6

    def p27_1():
        k = grover_k(10 ** 6, 1)
        return [f"N/2 = {10 ** 6 // 2:,}", f"= {k} iterations", f"({grover_p(10 ** 6, 1, k):.8f})", f"about {round(500_000 / k)}"]
    c["qc-L500-27-P1"] = p27_1
    c["qc-L500-27-P3"] = lambda: [f"(1 - 0.001)^1000 = {f4((1 - 1e-3) ** 1000)}", f"(1 - 0.001)^100 = {f4((1 - 1e-3) ** 100)}",
                                  f"(1 - 0.0001)^1000 = {f4((1 - 1e-4) ** 1000)}"]
    return c


def exam_checks():
    """Numbers quoted in the assessment pack's model answers, recomputed here."""
    p_same = math.cos(math.pi / 8) ** 2
    grover8 = [f"{grover_p(8, 1, 1):.5f}"] + [f4(grover_p(8, 1, k)) for k in (2, 3)]
    qpe = [qpe_p(1 / 3, 3, m) for m in range(8)]
    lab19 = TOPIC / "labs" / "L400" / "19-resource-estimation"
    sys.path.insert(0, str(lab19))
    import estimate_lab
    import solution_distance
    rsa = estimate_lab.physical(estimate_lab.rsa_logical(2048), choose=solution_distance.choose_distance)
    sys.path.remove(str(lab19))
    return {
        "content/assessment/midterm.md": [
            f"cos^2(π/8) = {f4(p_same)}", f"2000 × {f4(p_same)} ≈ {round(2000 * p_same)}",
            f"≈ {round(1.96 * math.sqrt(2000 * p_same * (1 - p_same)))}, range about {round(2000 * p_same - 31)}-{round(2000 * p_same + 31)}",
            f"P_1 = {grover8[0]}, P_2 = {grover8[1]}, P_3 = {grover8[2]}", f"floor(π/(4θ)) = {grover_k(8, 1)}",
            f"norm {f4(math.sqrt(2))}", f"sqrt(0.25/1000) ≈ {math.sqrt(0.25 / 1000):.3f}", "below 2^-9",
        ],
        "content/assessment/final.md": [
            f"k = floor(π/(4θ)) = {grover_k(1024, 1)}, P_25 = {f4(grover_p(1024, 1, 25))}", f"M = 4: k = {grover_k(1024, 4)}",
            f"m = {int(np.argmax(qpe))} (estimate {int(np.argmax(qpe)) / 8}) with P = {f4(max(qpe))}",
            f"2ε(1 - ε) = {2 * 0.02 * 0.98:.4f}", f"/ 15 = {10_000 * 365.25 * 24 / 15:,.0f}",
            f"({rsa['logical_qubits']} in the L400 #19 model)",
            f"about {round(rsa['physical_qubits'] / 1e6)} million physical qubits and {round(rsa['runtime_s'] / 3600)} hours",
            f"X + Y = {25 + 5} years",
        ],
    }


def check_structure(errors):
    numbers = [l["number"] for l in LESSONS]
    if numbers != [23, 24, 25, 26, 27]:
        errors.append(f"lesson numbers {numbers}")
    ids = set()
    for lesson in LESSONS:
        n = lesson["number"]
        for key in LESSON_FIELDS:
            if not lesson.get(key) and lesson.get(key) != []:
                errors.append(f"#{n}: missing {key}")
        if lesson.get("level") != "L500":
            errors.append(f"#{n}: level {lesson.get('level')}")
        objectives = lesson.get("learningObjectives", [])
        if not 3 <= len(objectives) <= 5:
            errors.append(f"#{n}: {len(objectives)} learning objectives")
        for o in objectives:
            if not o.split()[0].lower().rstrip(",") in BLOOM:
                errors.append(f"#{n}: objective does not start with a Bloom verb: {o[:50]}")
        theorems = lesson.get("theorems", [])
        if n <= 25 and not 2 <= len(theorems) <= 4:
            errors.append(f"#{n}: {len(theorems)} theorems")
        for t in theorems:
            for key in ("name", "statement", "proof", "check", "checkOutput"):
                if not t.get(key):
                    errors.append(f"#{n} {t.get('name')}: missing {key}")
        problems = lesson.get("problemSet", [])
        if not 6 <= len(problems) <= 10:
            errors.append(f"#{n}: {len(problems)} problems")
        for p in problems:
            if p["id"] in ids:
                errors.append(f"duplicate problem id {p['id']}")
            ids.add(p["id"])
            if p.get("type") not in PROBLEM_TYPES or p.get("difficulty") not in (1, 2, 3) or not isinstance(p.get("marks"), int):
                errors.append(f"{p['id']}: bad type/difficulty/marks")
            if len(p.get("solution", "")) < 80:
                errors.append(f"{p['id']}: solution too short")
        rubric = lesson.get("rubric", [])
        if sum(r["weight"] for r in rubric) != 100 or any(set(r) != {"criterion", "excellent", "adequate", "inadequate", "weight"} for r in rubric):
            errors.append(f"#{n}: rubric fields or weights (sum {sum(r['weight'] for r in rubric)})")
        if n == 26:
            case = lesson.get("caseStudy", {})
            for key in ("case", "stakeholders", "questions", "frameworks", "modelAnswer"):
                if not case.get(key):
                    errors.append(f"#26 caseStudy missing {key}")
        if n == 27:
            readings = lesson.get("readings", [])
            if len(readings) != 2:
                errors.append(f"#27: {len(readings)} readings")
            for r in readings:
                if len(r.get("guidingQuestions", [])) != 5 or not all(r.get(k) for k in ("citation", "url", "why", "responsePrompt")):
                    errors.append(f"#27 reading {r.get('citation', '?')[:30]}: fields / 5 guiding questions")
        note = TOPIC / lesson["conceptNote"]
        if not note.exists():
            errors.append(f"#{n}: concept note {lesson['conceptNote']} missing")
        else:
            words = len(note.read_text(encoding="utf-8").split())
            lo, hi = WORDS[n]
            if not lo <= words <= hi:
                errors.append(f"#{n}: concept note has {words} words (want {lo}-{hi})")
        for s in lesson.get("seeAlso", []):
            m = re.match(r"quantum-computing (L\d00|Capstone|Setup) #(\d+) (.*)$", s)
            if not m or int(m.group(2)) not in EARLIER or not m.group(3).startswith(EARLIER[int(m.group(2))]["title"] + ":"):
                errors.append(f"#{n}: seeAlso title not exact: {s[:70]}")
            elif EARLIER[int(m.group(2))]["level"] != m.group(1):
                errors.append(f"#{n}: seeAlso level mismatch: {s[:50]}")
        for src in lesson.get("sources", []):
            if not src.get("url", "").startswith("https://"):
                errors.append(f"#{n}: source without https url: {src}")


def main():
    errors = []
    check_structure(errors)
    n_theorems = 0
    for lesson in LESSONS:
        for t in lesson.get("theorems", []):
            lab_file, tid = t["check"].split("::")
            module = load_lab(lab_file)
            fresh = "\n".join(module.run([tid]))
            n_theorems += 1
            if fresh != t["checkOutput"]:
                errors.append(f"{tid}: fresh check output differs from checkOutput")
            readme = (TOPIC / lab_file).parent / "README.md"
            if not readme.exists() or fresh not in readme.read_text(encoding="utf-8"):
                errors.append(f"{tid}: output not pasted in {readme.relative_to(TOPIC)}")
    checks = problem_checks()
    problems = {p["id"]: p for lesson in LESSONS for p in lesson["problemSet"]}
    n_values = 0
    for pid, p in problems.items():
        if p["type"] == "calculation" and pid not in checks:
            errors.append(f"{pid}: calculation problem without a recomputation")
    for pid, fn in checks.items():
        if pid not in problems:
            errors.append(f"check for unknown problem {pid}")
            continue
        for value in fn():
            n_values += 1
            if value not in problems[pid]["solution"]:
                errors.append(f"{pid}: recomputed '{value}' not found in the solution")
    n_exam = 0
    for rel, values in exam_checks().items():
        text = (TOPIC / rel).read_text(encoding="utf-8")
        for value in values:
            n_exam += 1
            if value not in text:
                errors.append(f"{rel}: recomputed '{value}' not found")
    for e in errors:
        print("FAIL", e)
    print(f"{len(LESSONS)} lessons; {n_theorems} theorem checks re-run; {len(problems)} problems, "
          f"{len(checks)} recomputed ({n_values} values); {n_exam} exam values recomputed")
    if errors:
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
