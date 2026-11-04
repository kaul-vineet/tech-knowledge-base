"""L500 checks: re-run every theorem check and recompute every problem-set number in content/L500.json.

Run from anywhere: python research/l500_checks.py  -> prints OK and exits 0, or lists problems and exits 1.
1. Each lab's check_*.py must exit 0 with ALL CHECKS OK, and every line of each theorem's checkOutput must appear in
   the fresh output (so the JSON cannot drift from what the code prints).
2. Every calculation problem has a numericAnswer that (a) appears in its solution and (b) equals the value
   recomputed here from the lab modules and the real Library Loans code - never from the JSON.
3. Structural rules from L500-SPEC.md: objectives, theorem/problem counts, case study, readings, rubric, note lengths.
"""
import json
import math
import pathlib
import re
import subprocess
import sys

TOPIC = pathlib.Path(__file__).resolve().parent.parent
L500 = TOPIC / "labs" / "L500"
sys.dont_write_bytecode = True
for lab in ("23-modularity-theory", "24-quality-attributes", "25-formal-reasoning"):
    sys.path.insert(0, str(L500 / lab))

import availability as av  # noqa: E402
import contracts as c  # noqa: E402
import model_check as mc  # noqa: E402
import modularity as m  # noqa: E402
import tradeoff as tr  # noqa: E402

CHECK_SCRIPTS = {"23-modularity-theory": "check_modularity.py", "24-quality-attributes": "check_quality.py",
                 "25-formal-reasoning": "check_formal.py"}
BLOOM = re.compile(r"^(Explain|Prove|Derive|Analy[sz]e|Evaluate|Critique|Compare|Justify|Specify|Assess)\b")
NOTE_WORDS = {23: (900, 1300), 24: (900, 1300), 25: (900, 1300), 26: (700, 1000), 27: (500, 800)}


# ---------- independent recomputations (from the lab modules and the real code, not from the JSON) ----------
def p23_3():
    ca, ce, nc, na = 3, 1, 4, 1
    i, a = ce / (ca + ce), na / nc
    return f"I = {i:.2f}, A = {a:.2f}, Dn = {abs(a + i - 1):.2f}"


def p23_4():
    nodes, edges, classes = m.module_graph(m.HEXAGONAL)
    before = m.martin_metrics(nodes, edges, classes)
    moved = [e for e in edges if not (e[0] in ("driving_cli", "driving_http") and e[1] == "domain")]
    moved += [("driving_cli", "ports"), ("driving_http", "ports")]
    cls = dict(classes)
    cls["domain"] = (classes["domain"][0] - 4, classes["domain"][1])
    cls["ports"] = (classes["ports"][0] + 4, classes["ports"][1])
    after = m.martin_metrics(nodes, moved, cls)
    mean = lambda rows: sum(r["Dn"] for r in rows.values()) / len(rows)  # noqa: E731
    return (f"domain I = {after['domain']['I']:.2f}, Dn = {after['domain']['Dn']:.2f}; "
            f"ports A = {after['ports']['A']:.2f}, Dn = {after['ports']['Dn']:.2f}; "
            f"mean Dn {mean(before):.3f} -> {mean(after):.3f}")


def p23_5():
    conv = sum(len(v) for v in m.change_impact(m.KWIC_CONVENTIONAL).values())
    hide = sum(len(v) for v in m.change_impact(m.KWIC_HIDING).values())
    n = len(m.KWIC_DECISIONS)
    return f"{conv} vs {hide} module changes ({conv / n:.1f} vs {hide / n:.1f} per decision)"


def p23_7():
    sizes = [2, 3, 4]
    n = sum(sizes)
    allowed = sum(sizes[i] * sizes[j] for i in range(3) for j in range(i + 1, 3))
    return f"{n * (n - 1)} possible edges, {allowed} allowed"


def p24_1():
    return (f"{av.downtime_minutes(0.9995, av.MINUTES_PER_30_DAYS):.1f} min per 30 days, "
            f"{av.downtime_minutes(0.9995) / 60:.2f} h per year")


def p24_2():
    a = av.series([0.9999, 0.995, 0.999, 0.9995])
    return f"{a:.3%}, {av.downtime_minutes(a, av.MINUTES_PER_30_DAYS):.1f} min per 30 days"


def p24_3():
    n = next(k for k in range(1, 10) if av.parallel([0.995] * k) >= 0.99999)
    return f"{n} replicas (API tier {av.parallel([0.995] * n) * 100:.7f}%); system {av.library_loans(n):.3%}"


def p24_4():
    return f"{av.k_of_n(2, 3, 0.999):.4%} (2-of-3) vs {av.k_of_n(1, 1, 0.999):.1%} (single)"


def p24_5():
    return (f"{av.series([0.999, av.parallel([0.995, 0.995])]):.4%} with the common cause vs "
            f"{av.parallel([0.995, 0.995]):.4%} assumed")


def p24_6():
    mttf, target = 720, 0.9995
    mttr = mttf * (1 - target) / target
    return f"{mttf / (mttf + 1):.3%}; MTTR <= {mttr:.3f} h ({mttr * 60:.1f} min)"


def p24_7():
    x, y = tr.SINGLE_SQLITE, tr.REPLICATED_POSTGRES
    return (f"w* = {tr.break_even(x, y):.3f}; at w = 0.6 PostgreSQL {tr.weighted_score(y, 0.6):.3f} "
            f"vs SQLite {tr.weighted_score(x, 0.6):.3f}")


def p25_4():
    class FourLimit:
        def allowed(self, active, overdue):
            return active < 4
    pre_b, post_b = c.substitution_violations(FourLimit())
    return f"post broken at {post_b} of {len(c.DOMAIN)} points, pre at {pre_b}"


def p25_5():
    _, cex, _, _ = mc.bfs(fixed=False)
    return f"{len(cex)} steps; {mc.reachable_states(False)} and {mc.reachable_states(True)} reachable states"


def p25_6():
    members = [tuple("ABCDEF"[:k]) for k in range(2, 7)]
    fixed = ", ".join(str(mc.reachable_states(True, ms)) for ms in members)
    buggy = ", ".join(str(mc.reachable_states(False, ms)) for ms in members)
    assert all(mc.reachable_states(True, ms) == (len(ms) + 2) * 2 ** (len(ms) - 1) for ms in members)
    return f"fixed {fixed}; buggy {buggy}"


PROBLEMS = {"P23-3": p23_3, "P23-4": p23_4, "P23-5": p23_5, "P23-7": p23_7, "P24-1": p24_1, "P24-2": p24_2,
            "P24-3": p24_3, "P24-4": p24_4, "P24-5": p24_5, "P24-6": p24_6, "P24-7": p24_7, "P25-4": p25_4,
            "P25-5": p25_5, "P25-6": p25_6}


# ---------- exam numbers (content/assessment/midterm.md, final.md) ----------
EXAM_GRAPH = (["app", "web", "cli", "svc", "port", "sqlite"],
              [("web", "svc"), ("cli", "svc"), ("svc", "port"), ("sqlite", "port"), ("app", "web"), ("app", "cli"),
               ("app", "svc"), ("app", "sqlite")],
              {"app": (0, 0), "web": (1, 0), "cli": (1, 0), "svc": (3, 0), "port": (2, 2), "sqlite": (1, 0)})


def exam_numbers():
    nodes, edges, classes = EXAM_GRAPH
    rows = m.martin_metrics(nodes, edges, classes)
    svc, port = rows["svc"], rows["port"]
    level = m.longest_path_layering(nodes, edges)
    layering = "; ".join(", ".join(f"{n} {lv}" for n in nodes if level[n] == lv) for lv in sorted(set(level.values())))
    path = av.series([0.9999, av.parallel([0.999] * 3), 0.9995])
    shared = av.series([path, 0.9995])
    burn = 0.005 / (1 - 0.999)
    a_opt, b_opt = (0.6, 0.8), (0.9, 0.4)
    _, cex3, _, _ = mc.bfs(fixed=False, members=("A", "B", "C"))
    return {
        "midterm.md": [f"I = {svc['I']:.2f}, A = 0, Dn = {svc['Dn']:.2f}",
                       f"I = {port['I']:.0f}, A = {port['A']:.0f}, Dn = {port['Dn']:.0f}", layering],
        "final.md": [f"{path:.4%}", f"{shared:.4%}", f"{av.downtime_minutes(shared, av.MINUTES_PER_30_DAYS):.1f} min",
                     f"= {burn:.1f}", f"{burn * 1 / 720:.2%} of the budget", f"{240 * 0.0452:.1f} requests in flight",
                     f"= {math.ceil(240 / (75 * 0.8))} + 1 = {math.ceil(240 / (75 * 0.8)) + 1}",
                     f"= {tr.break_even(a_opt, b_opt):.3f}", f"= {tr.weighted_score(a_opt, 0.5):.2f}",
                     f"= {tr.weighted_score(b_opt, 0.5):.2f}", f"{mc.reachable_states(False, ('A', 'B', 'C'))} states",
                     f"{len(cex3)} steps"],
    }


def check_exams(problems):
    count = 0
    for name, needles in exam_numbers().items():
        text = (TOPIC / "content" / "assessment" / name).read_text(encoding="utf-8")
        for needle in needles:
            if needle in text:
                count += 1
                print(f"  OK  {name}: {needle}")
            else:
                problems.append(f"{name}: recomputed value {needle!r} not found in the model answers")
    return count


def run_theorem_checks(lessons, problems):
    outputs = {}
    for lab, script in CHECK_SCRIPTS.items():
        res = subprocess.run([sys.executable, "-B", script], cwd=L500 / lab, capture_output=True, text=True, encoding="utf-8")
        outputs[f"labs/L500/{lab}/{script}"] = res.stdout
        ok = res.returncode == 0 and "ALL CHECKS OK" in res.stdout
        print(f"  {'OK ' if ok else 'FAIL'} {lab}/{script} ({res.stdout.count('[OK]')} checks)")
        if not ok:
            problems.append(f"{lab}/{script} failed:\n{res.stdout}{res.stderr}")
    count = 0
    for lesson in lessons:
        for th in lesson.get("theorems", []):
            count += 1
            fresh = outputs.get(th["check"])
            if fresh is None:
                problems.append(f"{th['name']}: check path {th['check']} is not a known check script")
                continue
            missing = [line for line in th["checkOutput"].splitlines() if line.strip() and line not in fresh]
            if missing:
                problems.append(f"{th['name']}: checkOutput lines not in the fresh run: {missing[:2]}")
    return count


def check_problems(lessons, problems):
    recomputed = 0
    seen = set()
    for lesson in lessons:
        for p in lesson["problemSet"]:
            if p["type"] == "calculation" and "numericAnswer" not in p:
                problems.append(f"{p['id']}: calculation without numericAnswer")
            if "numericAnswer" not in p:
                continue
            if p["id"] not in PROBLEMS:
                problems.append(f"{p['id']}: no recomputation in PROBLEMS")
                continue
            seen.add(p["id"])
            value = PROBLEMS[p["id"]]()
            if value != p["numericAnswer"]:
                problems.append(f"{p['id']}: JSON says {p['numericAnswer']!r}, recomputed {value!r}")
            elif value not in p["solution"]:
                problems.append(f"{p['id']}: the recomputed answer does not appear in the solution text")
            else:
                recomputed += 1
                print(f"  OK  {p['id']}: {value}")
    for pid in sorted(set(PROBLEMS) - seen):
        problems.append(f"{pid}: recomputation has no problem in L500.json")
    return recomputed


def check_structure(lessons, problems):
    numbers = [lesson["number"] for lesson in lessons]
    if numbers != [23, 24, 25, 26, 27]:
        problems.append(f"lesson numbers {numbers}")
    required = ["id", "number", "level", "title", "category", "description", "outcome", "estimatedTime", "prerequisites",
                "glossary", "conceptNote", "conceptSummary", "sources", "seeAlso", "next", "platforms", "validation",
                "learningObjectives", "problemSet", "rubric"]
    for lesson in lessons:
        n = lesson["number"]
        problems += [f"lesson {n}: missing {k}" for k in required if k not in lesson]
        if lesson.get("level") != "L500":
            problems.append(f"lesson {n}: level {lesson.get('level')}")
        objectives = lesson.get("learningObjectives", [])
        if not 3 <= len(objectives) <= 5 or not all(BLOOM.match(o) for o in objectives):
            problems.append(f"lesson {n}: learningObjectives must be 3-5 and start with a Bloom verb")
        if not 6 <= len(lesson["problemSet"]) <= 10:
            problems.append(f"lesson {n}: {len(lesson['problemSet'])} problems (want 6-10)")
        for p in lesson["problemSet"]:
            if p["type"] not in {"derivation", "proof", "calculation", "short-answer", "essay"} or p["difficulty"] not in (1, 2, 3) \
                    or not isinstance(p["marks"], int) or len(p["solution"]) < 40:
                problems.append(f"{p['id']}: bad type/difficulty/marks/solution")
        if n <= 25 and not 2 <= len(lesson.get("theorems", [])) <= 4:
            problems.append(f"lesson {n}: needs 2-4 theorems")
        for th in lesson.get("theorems", []):
            if not all(th.get(k) for k in ("name", "statement", "proof", "check", "checkOutput")):
                problems.append(f"lesson {n}: theorem with an empty field")
            elif not (TOPIC / th["check"]).exists():
                problems.append(f"lesson {n}: {th['check']} does not exist")
        if n == 26:
            cs = lesson.get("caseStudy", {})
            if not all(cs.get(k) for k in ("case", "stakeholders", "questions", "frameworks", "modelAnswer")):
                problems.append("lesson 26: incomplete caseStudy")
        if n == 27:
            readings = lesson.get("readings", [])
            if len(readings) != 2 or any(len(r["guidingQuestions"]) != 5 or not r["responsePrompt"] for r in readings):
                problems.append("lesson 27: need 2 readings with 5 guiding questions and a response prompt")
        for r in lesson["rubric"]:
            if not all(k in r for k in ("criterion", "excellent", "adequate", "inadequate", "weight")):
                problems.append(f"lesson {n}: rubric row missing a field")
        if sum(r["weight"] for r in lesson["rubric"]) != 100:
            problems.append(f"lesson {n}: rubric weights do not sum to 100")
        note = TOPIC / lesson["conceptNote"]
        if not note.exists():
            problems.append(f"lesson {n}: concept note {lesson['conceptNote']} missing")
        else:
            words = len(note.read_text(encoding="utf-8").split())
            lo, hi = NOTE_WORDS[n]
            print(f"  {'OK ' if lo <= words <= hi else 'FAIL'} concept note {n}: {words} words (want {lo}-{hi})")
            if not lo <= words <= hi:
                problems.append(f"lesson {n}: concept note has {words} words")


def main():
    lessons = json.loads((TOPIC / "content" / "L500.json").read_text(encoding="utf-8"))
    problems = []
    print("theorem checks:")
    n_theorems = run_theorem_checks(lessons, problems)
    print("problem-set numbers:")
    n_numbers = check_problems(lessons, problems)
    print("exam numbers:")
    n_exam = check_exams(problems)
    print("structure:")
    check_structure(lessons, problems)
    print(f"theorems checked: {n_theorems}; problem numbers recomputed: {n_numbers}; exam numbers: {n_exam}; "
          f"problems: {sum(len(lesson['problemSet']) for lesson in lessons)}")
    for p in problems:
        print("PROBLEM", p)
    print("OK" if not problems else f"FAILED ({len(problems)} problems)")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
