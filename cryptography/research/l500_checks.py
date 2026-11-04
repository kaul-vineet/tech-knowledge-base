"""L500 validation: re-runs every theorem check and compares it with the checkOutput stored in content/L500.json,
recomputes every numeric problem-set answer from code, and checks the L500 structure rules (L500-SPEC.md).
Run: python research/l500_checks.py   -> prints OK and exits 0, or lists failures and exits 1."""
import json
import math
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True
TOPIC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOPIC / "labs" / "L500" / "23-number-theory"))
sys.path.insert(0, str(TOPIC / "labs" / "L500" / "24-probability"))

from nt_toys import crt, egcd, modinv  # noqa: E402
from prob_tools import collision_exact, collision_lower, collision_upper, min_entropy, shannon_entropy  # noqa: E402


def icbrt(x: int) -> int:
    lo, hi = 0, 1 << (x.bit_length() // 3 + 2)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        lo, hi = (mid, hi) if mid ** 3 <= x else (lo, mid - 1)
    return lo


def sci(x: float) -> str:
    e = math.floor(math.log10(x))
    return f"{x / 10 ** e:.2f}e{e}"


def p23_1():
    g, x, y = egcd(240, 46)
    return f"gcd {g}, x = {x}, y = {y}; 17^-1 mod 3120 = {modinv(17, 3120)}"


def p23_2():
    return f"x = {crt([2, 3, 2], [3, 5, 7])}"


def p23_3():
    return f"3^100 mod 7 = {pow(3, 100, 7)}"


def p23_5():
    n, e = 61 * 53, 17
    d = modinv(e, 60 * 52)
    c = pow(65, e, n)
    c2 = c * pow(2, e, n) % n
    return f"d = {d}, c = {c}, c' = {c2}, Dec(c') = {pow(c2, d, n)}"


def p23_6():
    a_pub, b_pub = pow(5, 6, 23), pow(5, 15, 23)
    assert pow(b_pub, 6, 23) == pow(a_pub, 15, 23)
    return f"A = {a_pub}, B = {b_pub}, K = {pow(b_pub, 6, 23)}"


def p23_7():
    c = 42 ** 3
    return f"c = {c}; integer cube root {icbrt(c)}"


def p23_8():
    work = 2 * Fraction(1, 2) ** 3
    return f"{work} of the work (about {int(1 / work)}x faster)"


def p24_1():
    q = next(q for q in range(1, 100) if collision_exact(q, 365) >= 0.5)
    return f"q = {q}, P = {collision_exact(q, 365):.4f}"


def p24_2():
    return f"about 2^{round(math.log2(collision_upper(2**32, 2**96)))}"


def p24_3():
    q = math.sqrt(2.0**65)
    return f"about {q / 1e9:.2f}e9 messages (2^{math.log2(q):.1f})"


def p24_4():
    return f"{2**32 / 1e4 / 86400:.2f} days"


def p24_6():
    pin = [0.1] + [0.9 / 9999] * 9999
    return f"H = {shannon_entropy(pin):.2f} bits, H_min = {min_entropy(pin):.2f} bits"


def p24_7():
    return f"about 2^{round(math.log2(collision_upper(2**40, 2**128)))}"


def p24_9():
    return (f"about 2^{round(math.log2(collision_upper(2**48, 2**192)))} "
            f"(vs about {collision_lower(2**48, 2**96):.2f} for 96-bit nonces)")


def p25_2():
    m1 = b"attack at dawn"
    x = bytes.fromhex("051112040d0f00151c454406161e")
    return f"m2 = '{bytes(a ^ b for a, b in zip(m1, x)).decode()}'"


def p25_4():
    return f"advantage {abs(7400 - 2600) / 10000:g}"


def p25_6():
    n, e, d = 3233, 17, 2753
    sig = pow(6, d, n) * pow(7, d, n) % n
    assert pow(sig, e, n) == 42
    return f"m = {pow(100, e, n)}; sigma(42) = {sig}"


def p25_7():
    a, b = math.isqrt(2**64), math.isqrt(2**256)
    return f"about 2^{a.bit_length() - 1} and about 2^{b.bit_length() - 1} operations; 2^{a.bit_length() - 1} stored elements"


def p25_8():
    return f"threshold {3329 // 4}, worst-case noise {32 * 2}"


def p27_2():
    return f"about {sci(2.0**100)} operations; ratio about 2^{int(math.log2(2**100 / 400))}"


def p27_3():
    h = math.log10(math.factorial(26))
    return f"H(K) = {h:.1f} decimal digits; unicity distance about {round(h / 0.7)} letters"


PROBLEMS = {f"{n[1:3]}-P{n[4:]}": fn for n, fn in list(globals().items()) if n.startswith("p2") and callable(fn)}


def sections(script: Path) -> dict:
    out = subprocess.run([sys.executable, "-B", script.name], cwd=script.parent, capture_output=True, text=True,
                         timeout=600)
    if out.returncode:
        raise RuntimeError(f"{script} exited {out.returncode}: {out.stderr.strip()[-300:]}")
    result, current = {}, None
    for line in out.stdout.splitlines():
        if line.startswith("[") and "]" in line:
            current = line[1:line.index("]")]
            result[current] = [line]
        elif current:
            result[current].append(line)
    return {k: "\n".join(v) for k, v in result.items()}


def words(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").split())


def main() -> int:
    lessons = json.loads((TOPIC / "content" / "L500.json").read_text(encoding="utf-8"))
    fails, n_th, n_calc = [], 0, 0
    seen = set()
    if [l["number"] for l in lessons] != [23, 24, 25, 26, 27]:
        fails.append("lessons must be numbered 23-27")
    for l in lessons:
        num = l["number"]
        for k in ("id", "level", "title", "category", "description", "outcome", "estimatedTime", "prerequisites",
                  "glossary", "conceptNote", "conceptSummary", "sources", "seeAlso", "next", "platforms", "validation",
                  "learningObjectives", "problemSet", "rubric"):
            if k not in l:
                fails.append(f"lesson {num}: missing {k}")
        if l.get("level") != "L500":
            fails.append(f"lesson {num}: level must be L500")
        if not 3 <= len(l.get("learningObjectives", [])) <= 5:
            fails.append(f"lesson {num}: need 3-5 learning objectives")
        if not 6 <= len(l.get("problemSet", [])) <= 10:
            fails.append(f"lesson {num}: need 6-10 problems")
        if abs(sum(r["weight"] for r in l.get("rubric", [])) - 100) > 0:
            fails.append(f"lesson {num}: rubric weights must sum to 100")
        lo, hi = (900, 1300) if num <= 25 else (700, 1000) if num == 26 else (500, 800)
        w = words(TOPIC / l["conceptNote"])
        if not lo <= w <= hi:
            fails.append(f"lesson {num}: concept note {w} words (want {lo}-{hi})")
        if num <= 25:
            if not 2 <= len(l.get("theorems", [])) <= 4:
                fails.append(f"lesson {num}: need 2-4 theorems")
            secs = sections(TOPIC / l["theorems"][0]["check"])
            for th in l["theorems"]:
                n_th += 1
                for k in ("name", "statement", "proof", "check", "checkOutput"):
                    if not th.get(k):
                        fails.append(f"{th.get('id')}: missing {k}")
                if secs.get(th["id"]) != th.get("checkOutput"):
                    fails.append(f"{th['id']}: check output differs from stored checkOutput:\n{secs.get(th['id'])}")
            if "demoOutput" in l:
                demo = "\n".join(v for k, v in secs.items() if k.startswith("D"))
                if demo != l["demoOutput"]:
                    fails.append(f"lesson {num}: demo output differs")
        if num == 26 and not all(l.get("caseStudy", {}).get(k) for k in ("case", "stakeholders", "questions", "frameworks", "modelAnswer")):
            fails.append("lesson 26: incomplete caseStudy")
        if num == 27:
            rd = l.get("readings", [])
            if len(rd) != 2 or any(len(r.get("guidingQuestions", [])) != 5 or not r.get("responsePrompt") or not r.get("url") for r in rd):
                fails.append("lesson 27: need 2 readings with url, 5 guiding questions and a response prompt")
        for p in l["problemSet"]:
            for k in ("id", "problem", "type", "difficulty", "solution", "marks"):
                if k not in p:
                    fails.append(f"{p.get('id')}: missing {k}")
            if p["type"] not in {"derivation", "proof", "calculation", "short-answer", "essay"}:
                fails.append(f"{p['id']}: bad type {p['type']}")
            if p["difficulty"] not in (1, 2, 3):
                fails.append(f"{p['id']}: bad difficulty")
            if p["type"] == "calculation" and "answer" not in p:
                fails.append(f"{p['id']}: calculation without an answer field")
            if "answer" in p:
                fn = PROBLEMS.get(p["id"])
                if fn is None:
                    fails.append(f"{p['id']}: no recompute function")
                    continue
                got = fn()
                seen.add(p["id"])
                n_calc += 1
                if got != p["answer"]:
                    fails.append(f"{p['id']}: computed {got!r}, stored {p['answer']!r}")
                if p["answer"] not in p["solution"]:
                    fails.append(f"{p['id']}: answer not stated in the worked solution")
    for pid in sorted(set(PROBLEMS) - seen):
        fails.append(f"{pid}: recompute function without a problem")
    print(f"theorem checks re-run and matched: {n_th}; numeric problem answers recomputed: {n_calc}")
    for f in fails:
        print("FAIL", f)
    if fails:
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
