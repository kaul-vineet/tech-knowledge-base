"""Recompute every number in L600 #03 (lesson, concept note, qbank) from the lab code; validate the JSON parts.

python integrated/research/checks_03.py      -> prints OK, exit 0 (about 2-3 minutes: it re-runs the experiments)
"""
import contextlib
import io
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # kb/integrated
KB = ROOT.parent
LAB = ROOT / "labs" / "L600" / "03-agent-driven-simulation"
sys.path.insert(0, str(LAB))

import _kb  # noqa: E402
import claims  # noqa: E402
import model  # noqa: E402
import pipeline  # noqa: E402
import registry  # noqa: E402
import run_project  # noqa: E402
import stats  # noqa: E402

FAILS = []


def check(label, ok):
    if not ok:
        FAILS.append(label)


def near(a, b, tol):
    return abs(a - b) <= tol


lesson = json.loads((ROOT / "content" / "parts" / "03.json").read_text(encoding="utf-8"))
bank = json.loads((ROOT / "content" / "qbank" / "parts" / "03.json").read_text(encoding="utf-8"))
note = (ROOT / "content" / "concepts" / "L600" / "03-agent-driven-simulation.md").read_text(encoding="utf-8")

# --- lesson structure ------------------------------------------------------------------------------------------
REQUIRED = ["id", "number", "level", "title", "category", "description", "outcome", "environment", "estimatedTime",
            "overview", "prerequisites", "designBrief", "architecture", "milestones", "rubric", "fitnessFunctions",
            "decisionRecords", "glossary", "steps", "code", "codeLanguage", "codeWalkthrough", "projectFiles",
            "expectedResults", "testCases", "tryIt", "troubleshooting", "learningTools", "inRealSystems", "useWhen",
            "simulatorVsReal", "caution", "checkpoint", "checkYourself", "sources", "next", "validation", "conceptNote",
            "conceptSummary", "platforms", "combines", "buildsOn", "seams", "failureLab", "buildTask", "scalingLimits"]
check("lesson fields", all(k in lesson for k in REQUIRED))
check("level/number", lesson["level"] == "L600" and lesson["number"] == 3 and lesson["category"] == "Integrated project")
check("code is run_project.py", lesson["code"] == (LAB / "run_project.py").read_text(encoding="utf-8"))
check("main file <= ~150 lines", len(lesson["code"].splitlines()) <= 150)
check("milestones 4-6", 4 <= len(lesson["milestones"]) <= 6)
check("seams 3-5", 3 <= len(lesson["seams"]) <= 5)
check("buildsOn 4-8", 4 <= len(lesson["buildsOn"]) <= 8)
check("ADRs 2-4", 2 <= len(lesson["decisionRecords"]) <= 4)
check("walkthrough 5-7", 5 <= len(lesson["codeWalkthrough"]) <= 7)
check("tryIt x2", len(lesson["tryIt"]) == 2)
check("learningTools <= 3", len(lesson["learningTools"]) <= 3)
check("scalingLimits 2-3", 2 <= len(lesson["scalingLimits"]) <= 3)
check("steps mac+windows", all("mac" in s and "windows" in s for s in lesson["steps"]))
for path in lesson["decisionRecords"] + [lesson["architecture"]["diagram"], lesson["buildTask"]["solution"]]:
    check(f"exists {path}", (ROOT / path).exists())
for s in lesson["seams"]:
    check(f"seam test {s['test']}", (ROOT / s["test"]).exists())
for b in lesson["buildsOn"]:
    titles = {x["number"]: x["title"] for lv in ("L100", "L200", "L300", "L400")
              for x in json.loads((KB / b["topic"] / "content" / f"{lv}.json").read_text(encoding="utf-8"))}
    check(f"buildsOn title {b['topic']} #{b['lesson']}", titles.get(b["lesson"]) == b["title"])
words = len(note.split())
check(f"concept note words {words}", 800 <= words <= 1000)
for adr in lesson["decisionRecords"]:
    text = (ROOT / adr).read_text(encoding="utf-8")
    check(f"Nygard sections {adr}", all(h in text for h in ("## Status", "## Context", "## Decision", "## Consequences")))

# --- closed-form numbers --------------------------------------------------------------------------------------------
wq = lambda lam, mu: lam / (mu * (mu - lam))
check("Wq 4.0 / 3.048", near(wq(0.8, 1.0), 4.0, 1e-12) and near(wq(0.8, 1.05), 3.048, 5e-4))
check("steady diff -0.952", round(wq(0.8, 1.05) - wq(0.8, 1.0), 3) == -0.952)
check("steady pct -23.8", round(100 * (wq(0.8, 1.05) / wq(0.8, 1.0) - 1), 1) == -23.8)
check("textbook 32.3 at lam 0.97", round(wq(0.97, 1.0), 1) == 32.3)
check("rho 0.947 / 0.895", round(0.9 / 0.95, 3) == 0.947 and round(0.85 / 0.95, 3) == 0.895)
check("sobol 384,000", 64 * (4 + 2) * 1000 == 384_000 and 10 * (4 + 1) * 1000 == 50_000)
check("experiment 220,000; session 270,000", 55 * 2 * 2000 == 220_000 and 220_000 + 50_000 == 270_000)
check("+-0.2 cost 420,000; CRN 40,000", 105 * 2 * 2000 == 420_000 and 10 * 2 * 2000 == 40_000)
check("n 47 / 105 from 0.645", math.ceil(10 * (0.645 / 0.3) ** 2) == 47 and math.ceil(10 * (0.645 / 0.2) ** 2) == 105)
check("t(0.975, 2) 4.303", round(stats.t_quantile(0.975, 2), 3) == 4.303)
check("t(0.975, 9) 2.262", round(stats.t_quantile(0.975, 9), 3) == 2.262)
check("warmup.t975(2) 3.85", round(_kb.load("warmup").t975(2), 2) == 3.85)
check("warm-up 200 > 169", model.DEFAULTS["warmup"] == 200)

# --- re-run the experiments ---------------------------------------------------------------------------------------
v_rows, same = run_project.verify_model()
check("M1 values", same and [(r["sim"], r["half_width"]) for r in v_rows] == [(0.992, 0.038), (3.894, 0.229), (8.491, 0.817)])

AB = {"baseline": {"lam": 0.8, "mu": 1.0}, "candidate": {"lam": 0.8, "mu": 1.05}, "replications": 3, "seed": 13}
pl = pipeline.Pipeline(registry.Registry(), pipeline.SimBudget(300_000), half_width=0.3)
r = pl.submit("run_experiment", AB)
check("55 reps", r["replications"] == 55 and r["verdict"] == "significant decrease")
check("means 4.04 / 3.14", (round(r["baseline"]["mean"], 2), round(r["candidate"]["mean"], 2)) == (4.04, 3.14))
check("diff -0.895 +- 0.293", r["difference"]["mean"] == -0.895 and r["difference"]["half_width"] == 0.293)
check("pct -22", round(r["percent_change"]) == -22)
check("arm half-widths 0.23 / 0.19", (round(r["baseline"]["ci_half_width"], 2), round(r["candidate"]["ci_half_width"], 2)) == (0.23, 0.19))
check("ledger 3 -> 10 -> 47 -> 55", [a for _, a in pl.budget.ledger] == [12_000, 28_000, 148_000, 32_000])
check("steady diff inside CI", r["difference"]["ci_low"] <= -0.952 <= r["difference"]["ci_high"])

pl3 = pipeline.Pipeline(registry.Registry(), pipeline.SimBudget(300_000), half_width=0.3, policy=pipeline.naive_policy)
r3 = pl3.submit("run_experiment", AB)
f3 = {k: v["value"] for k, v in pl3.registry.records[-1]["facts"].items()}
check("3-rep means 4.28 / 2.58 (-40%)", (round(f3["baseline_mean"], 2), round(f3["candidate_mean"], 2), round(f3["percent_change"])) == (4.28, 2.58, -40))
check("3-rep CI -3.436 .. 0.019", (round(f3["difference_low"], 3), round(f3["difference_high"], 3)) == (-3.436, 0.019))
check("3-rep hw 1.728 / diff -1.709", round(f3["difference_half_width"], 3) == 1.728 and round(f3["difference"], 3) == -1.709)
check("3-rep arm hw 2.07 / 1.05 overlap", (round(f3["baseline_half_width"], 2), round(f3["candidate_half_width"], 2)) == (2.07, 1.05)
      and f3["baseline_mean"] - f3["baseline_half_width"] <= f3["candidate_mean"] + f3["candidate_half_width"])
check("3-rep inconclusive", f3["verdict"] == "inconclusive")

pls = pipeline.Pipeline(registry.Registry(), pipeline.SimBudget(300_000))
check("sobol refused", "384,000" in pls.submit("run_screening", {"method": "sobol", "size": 64, "seed": 13})["errors"][0])
m = pls.submit("run_screening", {"method": "morris", "size": 10, "seed": 13})
mf = {k: v["value"] for k, v in pls.registry.records[-1]["facts"].items()}  # unrounded (the tool result is rounded to 3)
check("morris 1.72/1.53/0.74/0.54", [round(mf[f"mu_star_{k}"], 2) for k in ("mu", "lam", "warmup", "backlog")] == [1.72, 1.53, 0.74, 0.54])

crn = __import__("runpy").run_path(str(LAB / "try_it" / "crn.py"))["paired"]()
check("CRN 10 / -1.022 / 0.266 / 0.963", (crn[0], round(crn[1], 3), round(crn[2], 3), round(crn[3], 3)) == (10, -1.022, 0.266, 0.963))
plt = pipeline.Pipeline(registry.Registry(), pipeline.SimBudget(250_000), half_width=0.2)
rt = plt.submit("run_experiment", AB)
check("+-0.2: 10, required 105, hw 0.645", (rt["replications"], rt["required_replications"], rt["difference"]["half_width"], rt["budget_limited"]) == (10, 105, 0.645, True))

reg = registry.Registry()
with contextlib.redirect_stdout(io.StringIO()):
    spl, out = run_project.session(None, False, reg)
rows, published = claims.review(out["summary"], reg)
check("4 sentences, 1 rejected (32.3)", len(rows) == 4 and [x["sentence"] for x in rows if not x["ok"]] == ["At lam 0.97 the mean wait would be about 32.3 min."])
check("7/7 traced", claims.traced_runs(published, reg) == (7, 7))
check("160 runs reproduce", len(reg.runs()) == 160 and all(registry.reproduce(x) for x in reg.runs()))
check("spent 270,000, 5 calls", spl.budget.spent == 270_000 and out["calls"] == 5)
check("model version", model.VERSION == "3384b3898c59")
reg3 = registry.Registry()
with contextlib.redirect_stdout(io.StringIO()):
    _, out3 = run_project.session("few-reps", False, reg3)
check("failure-lab claim text", "cut the mean wait from 4.28 to 2.58 min (-40%), a significant improvement with 3 replications" in out3["summary"])
check("failure-lab rejection", any("claims significance" in x["reason"] for x in claims.review(out3["summary"], reg3)[0]))

# --- qbank ---------------------------------------------------------------------------------------------------------
check("qbank >= 30", len(bank) >= 30)
types = [q["type"] for q in bank]
check("calc >= 5", types.count("calculation") >= 5)
check("debugging >= 5", types.count("debugging") >= 5)
check("code-reading >= 4", types.count("code-reading") >= 4)
seam_qs = [q for q in bank if "seam" in q["source"].lower() or "contract" in q["question"].lower() or "schema" in q["question"].lower()]
check(f"seam questions >= 6 ({len(seam_qs)})", len(seam_qs) >= 6)
pos = [q["answer"] for q in bank]
check("answer balance 20-30%", all(0.2 <= pos.count(a) / len(bank) <= 0.3 for a in range(4)))
check("longest-correct <= 45%", sum(max(range(4), key=lambda i: len(q["options"][i])) == q["answer"] for q in bank) / len(bank) <= 0.45)
for q in bank:
    check(f"{q['id']} shape", q["level"] == "L600" and q["lesson"] == 3 and len(q["options"]) == 4
          and len(set(q["options"])) == 4 and 0 <= q["answer"] <= 3 and len(q["explanation"]) >= 30)
    check(f"{q['id']} no all/none", not any(re.search(r"\b(all|none) of the (above|options)\b", o, re.I) for o in q["options"]))
    if q["type"] == "code-reading":
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exec(q["code"], {})
        check(f"{q['id']} executed output", buf.getvalue().strip() == q["options"][q["answer"]])
calc = {q["id"]: q["options"][q["answer"]] for q in bank if q["type"] == "calculation"}
expected = {"int03-L600-008": f"{64 * 6 * 1000:,}",
            "int03-L600-009": str(math.ceil(10 * (0.645 / 0.3) ** 2)),
            "int03-L600-010": str(math.ceil(10 * (0.645 / 0.2) ** 2)),
            "int03-L600-011": f"{wq(0.8, 1.05) - wq(0.8, 1.0):.3f} min",
            "int03-L600-012": f"{55 * 2 * 2000:,} customers",
            "int03-L600-013": f"{0.85 / 0.95:.3f} - it {'passes' if 0.85 / 0.95 <= 0.9 else 'is rejected'}"}
for qid, want in expected.items():
    check(f"{qid} calc answer {calc.get(qid)!r} vs {want!r}", calc.get(qid) == want)

if FAILS:
    print("FAILED:", *FAILS, sep="\n  ")
    sys.exit(1)
print("OK")
