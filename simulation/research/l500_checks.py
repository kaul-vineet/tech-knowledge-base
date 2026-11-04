"""L500 checks: python research/l500_checks.py   (from the simulation/ folder; numpy + stdlib; prints OK, exits 0)

1. Re-runs every theorem check / codeCheck script and compares its stdout byte for byte with checkOutput in
   content/L500.json (Linux reference; on other OSes only the exit code is required).
2. Every number quoted in a proof or case text must appear in that script's real output (QUOTED).
3. Recomputes every numeric problem-set answer (PROBLEMS) and exam model-answer number (EXAMS) and requires the
   formatted value in the solution / exam text.
4. Structure: L500-SPEC field rules, rubric weights, concept-note word counts, seeAlso titles exist.
"""
import json
import math
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

TOPIC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOPIC / "labs" / "L500" / "25-rng-monte-carlo"))
from stats_util import chi2_sf  # noqa: E402

LESSONS = json.loads((TOPIC / "content" / "L500.json").read_text(encoding="utf-8"))
BY_NUM = {l["number"]: l for l in LESSONS}
errors = []


def check(cond, msg):
    if not cond:
        errors.append(msg)


# ---------- 1. re-run every check script ----------
outputs = {}
for l in LESSONS:
    for t in l.get("theorems", []) + ([l["codeCheck"]] if "codeCheck" in l else []):
        p = TOPIC / t["check"]
        r = subprocess.run([sys.executable, p.name], cwd=p.parent, capture_output=True, text=True, encoding="utf-8")
        check(r.returncode == 0, f"{t['check']}: exit {r.returncode}: {r.stderr[-300:]}")
        out = r.stdout.rstrip("\n")
        outputs[t["check"]] = out
        if sys.platform.startswith("linux"):
            check(out == t["checkOutput"], f"{t['check']}: output differs from checkOutput")

# ---------- 2. numbers quoted in the prose must come from the real output ----------
QUOTED = {
    "labs/L500/23-probability/t1_wlln.py": ["0.0427", "0.2500"],
    "labs/L500/23-probability/t2_clt.py": ["0.9631"],
    "labs/L500/23-probability/t3_poisson.py": ["0.5025", "0.1375", "0.1353"],
    "labs/L500/23-probability/t4_birth_death.py": ["3.919", "4.000", "0.2909", "[0.2439 0.4634 0.2927]"],
    "labs/L500/24-numerics/t1_euler_order.py": ["3.95", "4.00", "0.990", "2.420e-01"],
    "labs/L500/24-numerics/t2_rk4_order.py": ["-3.028e-07", "-3.094e-07", "15.59", "15.96", "3.996", "8/8"],
    "labs/L500/24-numerics/t3_stability.py": ["2.673e+33", "6.368e-04", "1.923e-05", "-2.7853", "1.729e+04", "952", "1053"],
    "labs/L500/24-numerics/t4_floating_point.py": ["1.40e-07", "h = 1e-07", "0.0; stable", "-> 0.5"],
    "labs/L500/25-rng-monte-carlo/t1_lcg_period.py": ["4096/4096", "3600/3600", "6561/6561", "0 of 99998", "planes used: 15"],
    "labs/L500/25-rng-monte-carlo/t2_gof_tests.py": ["99.06", "0.958", "0.814", "151465.4"],
    "labs/L500/25-rng-monte-carlo/t3_mc_variance_is.py": ["4.525e-09", "3.167e-05", "6,999x", "-0.500"],
    "labs/L500/25-rng-monte-carlo/t4_antithetic.py": ["-0.9677", "30.9x", "30.1x", "0.53x"],
    "labs/L500/26-ethics/aggregate_vs_individual.py": ["0.0000", "40.0%", "39.7%", "SD 0.090", "34%"],
    "labs/L500/27-readings/branching_process.py": ["0.6842 +/- 0.0064", "0.6863", "True"],
}
for path, needles in QUOTED.items():
    for n in needles:
        check(n in outputs.get(path, ""), f"{path}: quoted value {n!r} not in real output")
prose = json.dumps(LESSONS, ensure_ascii=False)
for n in ("0.0427", "0.9631", "0.5025", "3.919", "15.59", "2.7e33", "6.4e-4", "1.9e-5", "1.4e-7", "99.06", "151,465", "4.525e-09", "30.1x", "40.0%", "39.7%", "0.6842 +/- 0.0064"):
    check(n in prose, f"quoted value {n!r} expected in L500.json prose")


# ---------- 3. problem-set numbers ----------
def tail(z):
    return 0.5 * math.erfc(z / math.sqrt(2))


def gamma_tail(n, t):  # P(S_n > t) for a sum of n Exp(1) = P(N(t) < n)
    return sum(math.exp(-t + k * math.log(t) - math.lgamma(k + 1)) for k in range(n))


def stationary(P):
    P = [[Fraction(x).limit_denominator(100) for x in row] for row in P]
    n = len(P)
    A = [[P[j][i] - (1 if i == j else 0) for j in range(n)] for i in range(n - 1)] + [[Fraction(1)] * n]
    b = [Fraction(0)] * (n - 1) + [Fraction(1)]
    for c in range(n):  # Gauss-Jordan in exact arithmetic
        piv = next(r for r in range(c, n) if A[r][c] != 0)
        A[c], A[piv], b[c], b[piv] = A[piv], A[c], b[piv], b[c]
        for r in range(n):
            if r != c and A[r][c] != 0:
                f = A[r][c] / A[c][c]
                A[r] = [x - f * y for x, y in zip(A[r], A[c])]
                b[r] -= f * b[c]
    return [b[i] / A[i][i] for i in range(n)]


def extinction(m):
    q = 0.0
    for _ in range(5000):
        q = math.exp(m * (q - 1))
    return q


def mult_order(a, m):
    k = 1
    while pow(a, k, m) != 1:
        k *= 2  # the group mod 2^31 has order 2^30, so the order is a power of two
    return k


MU = math.e - 1
S2 = (math.e**2 - 1) / 2 - MU**2
RHO = (math.e - MU**2) / S2
pi3 = stationary([[0.5, 0.4, 0.1], [0.2, 0.6, 0.2], [0.1, 0.3, 0.6]])
PROBLEMS = {
    "23-P2": [f"{math.ceil(1 / (0.05 * 0.1**2)):,}", f"{(1.96 / 0.1) ** 2:.2f}", f"n = {math.ceil((1.96 / 0.1) ** 2)}"],
    "23-P3": [f"{math.exp(-2):.4f}", f"{5 / 3:.3f}", f"{math.exp(-3) * 9 / 2:.4f}"],
    "23-P5": [f"{pi3[0].numerator}/{pi3[0].denominator}, {pi3[1].numerator}/{pi3[1].denominator}, {pi3[2].numerator}/{pi3[2].denominator}",
              " ".join(f"{float(x):.4f}" for x in pi3).replace(" ", ", ")],
    "23-P6": [f"{0.2 * 0.8**5 / (1 - 0.8**6):.5f}"],
    "23-P7": [f"{0.9 / 0.1:.0f} customers", f"{1 / (1 - 0.9):.0f} min", f"{0.81 / 0.1:.1f}", f"{0.9**5:.4f}", f"{(1 / 0.1) / (1 / 0.2):.2f}"],
    "23-P8": [f"{tail(3.0):.5f}", f"{gamma_tail(100, 130):.5f}", f"{tail(1.0):.4f}", f"{gamma_tail(100, 110):.4f}"],
    "24-P3": [f"{0.5 * math.e**2 - 2:.3f}", f"{0.1 * (0.5 * math.e**2 - 2) / 2 * (math.e**2 - 1):.4f}"],
    "24-P4": [f"{2 / 50:.2f}", f"{2.7853 / 50:.5f}"],
    "24-P6": [f"{round(2 / (2 / 1000)):,} steps", "1.923e-05"],
    "24-P7": [f"{53 * math.log10(2):.2f}", f"{2 * math.sqrt(2**-53):.3e}", f"{2 * math.e * math.sqrt(2**-53):.2e}"],
    "25-P1": [f"{mult_order(65539, 2**31):,}", f"{(1664525 - 1) // 4}"],
    "25-P4": [f"{sum((c - 100) ** 2 for c in [112, 95, 88, 104, 99, 91, 118, 97, 100, 96]) / 100:.2f}",
              f"p = {chi2_sf(7.60, 9):.3f}"],
    "25-P5": [f"{math.ceil(1.96**2 * S2 / 1e-6):,}"],
    "25-P6": [f"{math.exp(16) * tail(8.0) - tail(4.0) ** 2:.3e}", f"{tail(4.0) * (1 - tail(4.0)):.3e}"],
    "25-P7": [f"{1 / (1 + RHO):.1f}x", f"{math.ceil(1.96**2 * S2 * (1 + RHO) / 2 / 1e-6):,} pairs",
              f"{2 * math.ceil(1.96**2 * S2 * (1 + RHO) / 2 / 1e-6):,} evaluations"],
    "26-P2": [f"{round((1 - 0.964) * 718_276):,}"],
    "26-P4": [f"{26_000 / 26:,.0f}"],
    "27-P2": [f"q = {extinction(1.2):.4f}", f"q = {extinction(1.5):.4f}", f"q = {extinction(2.0):.4f}",
              f"{1.96 * math.sqrt(extinction(1.2) * (1 - extinction(1.2)) / 20_000):.4f}"],
}
assert abs(tail(8.0) * math.exp(16) - np.exp(16) * 0.5 * math.erfc(8 / math.sqrt(2))) < 1e-15
problems = {p["id"]: p for l in LESSONS for p in l["problemSet"]}
for pid, values in PROBLEMS.items():
    sol = problems[pid]["solution"]
    for v in values:
        check(v in sol, f"{pid}: computed {v!r} not found in the solution")
# exam model answers (content/assessment/*.md): every number must be the recomputed value
P4 = tail(4.0)
IS_VAR = math.exp(16) * tail(8.0) - P4**2
EXAMS = {
    "midterm.md": [f"{1 / (1 - 0.9):.0f} min", f"{1 / (1 - 0.95):.0f} min", f"{1.47 * 0.05 / 0.1:.3f} m", f"{9.8 * 3 * 0.1 / 2:.2f}",
                   f"{2 / 1000:.3f}", f"{round(2 / 0.002):,} steps", f"{1 / (1 - 0.5):.2f}x", f"{1 / (1 - 0.9**2):.2f}x", f"{1.36 / math.sqrt(200):.3f}"],
    "final.md": [f"{1 / (400 * 0.2**2):.4f}", f"{math.exp(-2 * 0.5):.4f}", f"{0.2420 / 4:.4f}", f"{6.990e-06 / 4**4:.2e}",
                 f"{IS_VAR:.3e}", f"{round((1 - P4) / (0.01 * P4)):,}", f"{math.ceil(IS_VAR / (0.01 * P4**2))}", "151,465"],
}
for fname, values in EXAMS.items():
    text = (TOPIC / "content" / "assessment" / fname).read_text(encoding="utf-8")
    for v in values:
        check(v in text, f"{fname}: recomputed {v!r} not found")
calc_ids = {pid for pid, p in problems.items() if p["type"] == "calculation"}
check(calc_ids <= set(PROBLEMS), f"calculation problems without a recomputation: {sorted(calc_ids - set(PROBLEMS))}")

# ---------- 4. structure ----------
earlier_titles = {}
for lv in ("L100", "L200", "L300", "L400", "L500"):
    for l in json.loads((TOPIC / "content" / f"{lv}.json").read_text(encoding="utf-8")):
        earlier_titles[l["number"]] = l["title"]
WORDS = {23: (900, 1300), 24: (900, 1300), 25: (900, 1300), 26: (700, 1000), 27: (500, 800)}
BLOOM = re.compile(r"^(Derive|Prove|Explain|Evaluate|Critique|Analyze|Summarize|Apply|Compare|Verify)\b")
for l in LESSONS:
    n = l["number"]
    for k in ("id", "number", "level", "title", "category", "description", "outcome", "estimatedTime", "prerequisites", "glossary",
              "conceptNote", "conceptSummary", "sources", "seeAlso", "next", "platforms", "validation", "learningObjectives", "problemSet", "rubric"):
        check(k in l, f"lesson {n}: missing {k}")
    check(l["level"] == "L500" and 23 <= n <= 27, f"lesson {n}: level/number")
    check(3 <= len(l["learningObjectives"]) <= 5, f"lesson {n}: {len(l['learningObjectives'])} objectives")
    for o in l["learningObjectives"]:
        check(BLOOM.match(o), f"lesson {n}: objective without a Bloom verb: {o[:40]}")
    check(6 <= len(l["problemSet"]) <= 10, f"lesson {n}: {len(l['problemSet'])} problems")
    for p in l["problemSet"]:
        check(p["type"] in {"derivation", "proof", "calculation", "short-answer", "essay"} and p["difficulty"] in (1, 2, 3)
              and isinstance(p["marks"], int) and len(p["solution"]) > 80, f"{p['id']}: bad problem fields")
    check(sum(r["weight"] for r in l["rubric"]) == 100, f"lesson {n}: rubric weights != 100")
    if n <= 25:
        check(2 <= len(l["theorems"]) <= 4, f"lesson {n}: theorem count")
        for t in l["theorems"]:
            check(all(t.get(k) for k in ("name", "statement", "proof", "check", "checkOutput")), f"lesson {n}: theorem fields")
    if n == 26:
        cs = l["caseStudy"]
        check(all(cs.get(k) for k in ("case", "stakeholders", "questions", "frameworks", "modelAnswer")), "lesson 26: caseStudy fields")
    if n == 27:
        check(len(l["readings"]) == 2 and all(len(r["guidingQuestions"]) == 5 and r["url"] and r["responsePrompt"] for r in l["readings"]),
              "lesson 27: readings")
    words = len((TOPIC / l["conceptNote"]).read_text(encoding="utf-8").split())
    lo, hi = WORDS[n]
    check(lo <= words <= hi, f"lesson {n}: concept note {words} words (want {lo}-{hi})")
    for s in l["seeAlso"]:
        m = re.match(r"simulation L\d00 #(\d+) (.+?):", s)
        check(m and earlier_titles.get(int(m.group(1)), "").startswith(m.group(2)[:30]), f"lesson {n}: seeAlso title mismatch: {s[:60]}")

for e in errors:
    print("ERROR", e)
if errors:
    sys.exit(1)
print(f"re-ran {len(outputs)} check scripts (output identical), {sum(len(v) for v in QUOTED.values())} quoted values traced, "
      f"{sum(len(v) for v in PROBLEMS.values())} problem-set numbers recomputed across {len(PROBLEMS)} problems, "
      f"{sum(len(v) for v in EXAMS.values())} exam numbers recomputed")
print("OK")
