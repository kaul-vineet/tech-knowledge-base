"""L500 checks: re-run every theorem check and recompute every numeric answer in content/L500.json.

    python research/l500_checks.py      -> prints OK and exits 0

1. Each theorem's `check` command is executed in-process; its output must equal the recorded `checkOutput`.
2. Each calculation problem has a function below; every number it returns must appear in the written solution
   (likewise every numeric model answer in content/assessment/midterm.md and final.md).
3. Structure: lessons 23-27, 3-5 learning objectives, 2-4 theorems (23-25), 6-10 problems, rubric, case study (26),
   readings (27), concept-note word counts.
"""
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

TOPIC = Path(__file__).resolve().parent.parent
LABS = TOPIC / "labs" / "L500"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    spec.loader.exec_module(mod)
    return mod


lm = load("tiny_lm", LABS / "23-language-model-foundations" / "tiny_lm.py")
st = load("eval_stats", LABS / "24-evaluation-statistics" / "eval_stats.py")
dp = load("decision_planning", LABS / "25-decision-planning" / "decision_planning.py")
np = lm.np


def f4(x):
    return f"{x:.4f}"


# ---------------------------------------------------------------- lesson 23
def l23_p2():
    z = [2.0, 1.0, 0.0]
    p1, p05 = lm.softmax(z, 1.0), lm.softmax(z, 0.5)
    return [*map(f4, p1), *map(f4, p05), f4(lm.entropy(p1)), f4(lm.entropy(p05))]


def l23_p4():
    toks = lm.tokenize(lm.CORPUS)
    m = lm.Bigram(toks, lm.build_vocab(toks))
    sent = "the agent calls the tool .".split()
    prob = math.prod(m.P[m.vocab[a], m.vocab[b]] for a, b in zip(sent, sent[1:]))
    return [f"{prob:.6f}", f4(prob ** (-1 / 5))]


def l23_p5():
    toks = lm.tokenize(lm.CORPUS)
    m = lm.Bigram(toks, lm.build_vocab(toks))
    row = m.P[m.vocab["the"]]
    q = lm.truncate(row, "top_p", p=0.7)
    kept = sorted((q[i] for i in np.flatnonzero(q)), reverse=True)
    return [f4(row[q > 0].sum()), *map(f4, kept)]


def l23_p7():
    ce_a = -math.log(0.25)
    ce_b = (99 * -math.log(0.9) + -math.log(1e-6)) / 100
    ce_c = -math.log(0.9)
    return [f4(ce_a), f4(math.exp(ce_a)), f4(ce_b), f4(math.exp(ce_b)), f4(math.exp(ce_c))]


def l23_p8():
    d = 64
    return [f4(math.sqrt(d)), f4(1 / math.sqrt(d)), f4(math.sqrt(2 * d))]


# ---------------------------------------------------------------- lesson 24
def l24_p1():
    w, wd = st.wilson(47, 50), st.wald(47, 50)
    return [f4(w[0]), f4(w[1]), f4(wd[0]), f4(wd[1])]


def l24_p3():
    n = st.sample_size(0.95, 0.90)
    c, size, power = st.exact_power(n, 0.95, 0.90)
    n01 = st.sample_size(0.95, 0.90, alpha=0.01)
    return [str(n), str(c), f4(size), f4(power), str(n01)]


def l24_p4():
    stat, p = st.mcnemar_chi2(12, 4)
    return [f4(st.mcnemar_exact(12, 4)), f4(stat), f4(p), f4(st.two_proportion_p(250, 242, 300))]


def l24_p6():
    return [f4(st.fwer_independent(0.05, 12)), f"{0.05 / 12:.6f}", f4(st.fwer_independent(0.05 / 12, 12))]


def l24_p8():
    w = st.wilson(19, 20)
    c, size, power = st.exact_power(20, 0.95, 0.85)
    return [f4(w[0]), f4(w[1]), str(c), f4(size), f4(power)]


# ---------------------------------------------------------------- lesson 25
def l25_p1():
    return [f4(dp.expected_attempts(0.6, 4)), f4(0.4 ** 4), f4(1 / 0.6)]


def l25_p3():
    auto = dp.expected_utility([(0.96, 3.0), (0.04, -60.0)])
    review = dp.expected_utility([(1.0, 3.0 - 2.0)])
    return [f"{auto:.2f}", f"{review:.2f}", f4(2 / 63)]


def l25_p4():
    V, policy, _ = dp.value_iteration(dp.make_mdp(0.03))
    closed = (0.77 * 9 - 0.20 * 1 - 0.03 * 51) / (1 - 0.95 * 0.20)
    assert abs(V["open"] - closed) < 1e-6 and policy["open"] == "auto"
    return [f4(closed)]


def l25_p6():
    h = {"start": 4, "lookup_order": 6, "search_kb": 2, "check_policy": 1, "draft_reply": 0}
    true = {n: dp.astar(n, "draft_reply", lambda m: dp.PLAN[m], lambda m: 0)[0] for n in dp.PLAN}
    admissible = all(h[n] <= true[n] for n in dp.PLAN)
    consistent = all(h[n] <= c + h[m] for n in dp.PLAN for m, c in dp.PLAN[n])
    cost, path, _ = dp.astar("start", "draft_reply", lambda m: dp.PLAN[m], h.get)
    return [f"admissible: {admissible}", f"consistent: {consistent}", f"cost {cost}"]


def l25_p7():
    ps = [0.8 * 0.4**i for i in range(20)]
    k = dp.best_budget(ps, 2.0, 30.0)
    return [f"k* = {k}", f4(dp.retry_cost_seq(ps[:k], 2.0, 30.0)), f4(dp.retry_cost_seq(ps[:1], 2.0, 30.0)),
            f4(dp.retry_cost_seq(ps, 2.0, 30.0))]


# ---------------------------------------------------------------- lesson 26
def l26_p3():
    n, err, harm, review = 10_000, 0.02, 200.0, 1.50
    errors = n * err
    none = errors * harm
    full = n * review + errors * (1 - 0.9) * harm
    targeted = 0.3 * n * review + (errors - 0.9 * 0.8 * errors) * harm
    biased = 0.3 * n * review + (errors - 0.5 * 0.8 * errors) * harm
    return [f"{none:,.0f}", f"{full:,.0f}", f"{targeted:,.0f}", f"{biased:,.0f}"]


def l26_p4():
    paid, should = 1630.36, 979.48  # totals stated in the decision (paras 34 and 40)
    damages = round(paid - should, 2)
    return [f"{damages:,.2f}", f"{damages + 36.14 + 125:,.2f}"]


# ---------------------------------------------------------------- lesson 27
def l27_p1():
    d_model, h, n = 512, 8, 100
    d_k = d_model // h
    return [str(d_k), f4(1 / math.sqrt(d_k)), f"{n * n * d_model:,}", f"{n * d_model * d_model:,}", f"{d_model / n:.2f}"]


def l27_p3():
    a, b = st.wilson(3, 50), st.wilson(7, 50)
    return [f4(a[0]), f4(a[1]), f4(b[0]), f4(b[1]), f4(st.two_proportion_p(3, 7, 50))]


def exam_numbers():
    """Every numeric model answer in the exams, recomputed."""
    p1, p2 = lm.softmax([3, 1, 1, 0], 1.0), lm.softmax([3, 1, 1, 0], 2.0)
    stat, p_chi = st.mcnemar_chi2(9, 2)
    n = st.sample_size(0.92, 0.87)
    c, size, power = st.exact_power(n, 0.92, 0.87)
    V, policy, _ = dp.value_iteration(dp.make_mdp(0.04))
    assert policy["open"] == "auto"
    toks = lm.tokenize(lm.CORPUS)
    add1 = lm.Bigram(toks, lm.build_vocab(toks), k=1.0)
    midterm = [*map(f4, p1), *map(f4, p2), f4(lm.entropy(p1)), f4(lm.entropy(p2)),
               *map(f4, st.wilson(45, 50)), *map(f4, st.wald(45, 50)),
               f4(st.mcnemar_exact(9, 2)), f4(stat), f4(p_chi), f4(st.two_proportion_p(180, 173, 200)),
               f4(dp.expected_attempts(0.8, 3)), f4(0.2 ** 3), f4(st.wilson(20, 20)[0]), f4(st.exact_power(20, 0.95, 0.90)[2]),
               str(st.sample_size(0.95, 0.90))]
    final = [str(n), str(c), f4(size), f4(power), f4((7 - 5 * 0.81) / 60), f4(V["open"]),
             f4(add1.perplexity(toks)), f4(add1.perplexity(lm.tokenize(lm.HELD_OUT))), f4(1 / math.sqrt(128)), f4(math.sqrt(128)),
             f4(st.fwer_independent(0.05, 8)), f"{0.05 / 8:.5f}", f4(st.wilson(3, 50)[0]), f4(st.wilson(3, 50)[1]),
             f4((7 - 4 * 0.81) / 60)]
    return {"content/assessment/midterm.md": midterm, "content/assessment/final.md": final}


PROBLEM_CHECKS = {f.__name__.replace("_", "-"): f for f in [
    l23_p2, l23_p4, l23_p5, l23_p7, l23_p8,
    l24_p1, l24_p3, l24_p4, l24_p6, l24_p8,
    l25_p1, l25_p3, l25_p4, l25_p6, l25_p7,
    l26_p3, l26_p4, l27_p1, l27_p3]}

MODULES = {"tiny_lm.py": lm, "eval_stats.py": st, "decision_planning.py": dp}
NOTE_WORDS = {23: (900, 1300), 24: (900, 1300), 25: (900, 1300), 26: (700, 1000), 27: (500, 800)}


def run_check(command):
    path, _, name = command.split()
    return "\n".join(MODULES[Path(path).name].CHECKS[name]())


def main():
    errors = []
    lessons = json.loads((TOPIC / "content" / "L500.json").read_text(encoding="utf-8"))
    nums = [l["number"] for l in lessons]
    if nums != [23, 24, 25, 26, 27]:
        errors.append(f"lesson numbers {nums}")
    n_theorems = n_calc = 0
    for l in lessons:
        num = l["number"]
        if l.get("level") != "L500":
            errors.append(f"{num}: level {l.get('level')}")
        if not 3 <= len(l.get("learningObjectives", [])) <= 5:
            errors.append(f"{num}: {len(l.get('learningObjectives', []))} learning objectives")
        if not 6 <= len(l.get("problemSet", [])) <= 10:
            errors.append(f"{num}: {len(l.get('problemSet', []))} problems")
        if not l.get("rubric"):
            errors.append(f"{num}: no rubric")
        if num <= 25:
            if not 2 <= len(l.get("theorems", [])) <= 4:
                errors.append(f"{num}: {len(l.get('theorems', []))} theorems")
            for t in l["theorems"]:
                n_theorems += 1
                path = TOPIC / t["check"].split()[0]
                if not path.exists():
                    errors.append(f"{num} {t['name']}: missing {path}")
                    continue
                got = run_check(t["check"])
                if got != t["checkOutput"]:
                    errors.append(f"{num} {t['name']}: checkOutput differs from a fresh run:\n{got}")
        if num == 26 and not all(k in l.get("caseStudy", {}) for k in ("case", "stakeholders", "questions", "frameworks", "modelAnswer")):
            errors.append("26: caseStudy incomplete")
        if num == 27:
            rs = l.get("readings", [])
            if len(rs) != 2 or any(len(r["guidingQuestions"]) != 5 for r in rs):
                errors.append("27: need 2 readings with 5 guiding questions each")
        for p in l["problemSet"]:
            if p["type"] not in {"derivation", "proof", "calculation", "short-answer", "essay"} or p["difficulty"] not in (1, 2, 3):
                errors.append(f"{p['id']}: bad type/difficulty")
            if p["type"] == "calculation":
                n_calc += 1
                fn = PROBLEM_CHECKS.get(p["id"])
                if fn is None:
                    errors.append(f"{p['id']}: calculation without a check function")
                    continue
                for value in fn():
                    if value not in p["solution"]:
                        errors.append(f"{p['id']}: recomputed '{value}' not found in the solution")
        note = TOPIC / l["conceptNote"]
        words = len(re.findall(r"\S+", note.read_text(encoding="utf-8"))) if note.exists() else 0
        lo, hi = NOTE_WORDS[num]
        if not lo <= words <= hi:
            errors.append(f"{num}: concept note {words} words (want {lo}-{hi})")
    n_exam = 0
    for rel, values in exam_numbers().items():
        text = (TOPIC / rel).read_text(encoding="utf-8")
        for value in values:
            n_exam += 1
            if value not in text:
                errors.append(f"{rel}: recomputed '{value}' not found")
    for e in errors:
        print("ERROR", e)
    print(f"re-ran {n_theorems} theorem checks; recomputed {n_calc} calculation problems and {n_exam} exam numbers; {len(lessons)} lessons")
    if errors:
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
