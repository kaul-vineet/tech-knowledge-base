"""L600 #05 checks: recompute every number used in the lesson, concept note and question bank; execute every
code-reading snippet; validate the question bank's structure. Prints OK and exits 0, or lists failures and exits 1.
python integrated/research/checks_05.py
"""
import collections
import contextlib
import io
import json
import math
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # kb/integrated
LAB = ROOT / "labs" / "L600" / "05-observatory-scheduler"
sys.path.insert(0, str(LAB))

import numpy as np  # noqa: E402

import _kb  # noqa: E402
import agent_plan  # noqa: E402
import scheduler  # noqa: E402
import sky  # noqa: E402
import validator  # noqa: E402
import weather  # noqa: E402

FAIL = []
LESSON = json.loads((ROOT / "content" / "parts" / "05.json").read_text(encoding="utf-8"))
QB = json.loads((ROOT / "content" / "qbank" / "parts" / "05.json").read_text(encoding="utf-8"))
NOTE = (ROOT / "content" / "concepts" / "L600" / "05-observatory-scheduler.md").read_text(encoding="utf-8")
README = (LAB / "README.md").read_text(encoding="utf-8")
TEXT = json.dumps(LESSON, ensure_ascii=False) + NOTE + README + json.dumps(QB, ensure_ascii=False)
for f in (LAB / "decisions").glob("*.md"):
    TEXT += f.read_text(encoding="utf-8")


def ok(name, cond, detail=""):
    if not cond:
        FAIL.append(f"{name}: {detail}")


def stated(name, value):
    """A recomputed value must appear verbatim in the lesson/note/README/ADRs/qbank text."""
    ok(name, value in TEXT, f"{value!r} not found in lesson text")


# ---- the night, the plans, the promises
r = scheduler.build(seed=2026)
reqs, slots = r["reqs"], r["slots"]
ok("slots", len(slots) == 64, len(slots))
stated("first UTC", slots[0].utc.iso())
stated("dark window", f"{slots[0].local:%H:%M}–{slots[-1].local:%H:%M}")
feasible = [q.name for q, row in zip(reqs, r["ok"]) if row.any()]
ok("feasible 7", len(feasible) == 7, feasible)
ok("infeasible set", set(q.name for q in reqs) - set(feasible) == {"Fomalhaut", "Polaris", "Canopus", "Arcturus"})
gv, lv = r["greedy_value"], r["local_value"]
for v in (f"{gv:.3f}", f"{lv:.3f}"):
    stated("plan value", v)
ok("greedy plan", [x["target"] for x in r["greedy_rows"]] == ["Deneb", "Aldebaran", "Capella", "Betelgeuse"])
ok("local plan", [x["target"] for x in r["local_rows"]] == ["Vega", "Deneb", "Aldebaran", "Betelgeuse", "Sirius"])
ok("deneb at slot 6", r["local"][1][0] == 6, r["local"])
h = scheduler.plan_hash(r["local_rows"])
stated("hash", h)
ok("same plan for seeds 1,2,3", all(scheduler.plan_hash(scheduler.as_rows(scheduler.local_search(reqs, r["ok"], r["x"], s),
                                                                          reqs, slots, r["x"])) == h for s in (1, 2, 3)))
worst_x = max(x["max_airmass"] for x in r["greedy_rows"] + r["local_rows"])
stated("max airmass", f"{worst_x:.3f}")
for x in r["local_rows"]:
    stated("promise", f"{x['p_complete']}")
ok("vega window", bool((r["x"][0][:7] <= 2.0).all() and r["x"][0][7] > 2.0), r["x"][0][:9])
fom = next(q for q in reqs if q.name == "Fomalhaut")
win = [s for s in slots if float(sky.airmass(sky.alt_deg(fom, s.utc))) <= 2.0]
ok("Fomalhaut Moon-blocked in its window", win and max(sky.moon_sep_deg(fom, s.utc) for s in win) < 30.0)
pol = next(q for q in reqs if q.name == "Polaris")
ok("Polaris airmass > 2 all night", min(float(sky.airmass(sky.alt_deg(pol, s.utc))) for s in slots) > 2.0)
ok("Polaris altitude ~28.5", abs(np.mean([sky.alt_deg(pol, s.utc) for s in slots]) - 28.5) < 1.0)
arc = next(q for q in reqs if q.name == "Arcturus")
ok("Arcturus rises only near dawn", sky.alt_deg(arc, slots[-1].utc) > 0 and sky.alt_deg(arc, slots[40].utc) < 0)
stated("Canopus max alt", f"{90 - abs(sky.SITE['lat_deg'] - (-52.6957)):.2f}")

# ---- weather
pi = weather.pi_clear()
stated("pi", f"{pi:.3f}")
for n in (6, 12, 18):
    stated(f"p{n}", f"{weather.p_complete(n):.3f}")
stated("p6 4dp", f"{weather.p_complete(6):.4f}")
clear = weather.clear_matrix(1000, len(slots), 7)
wb = lambda key: [(s, n, reqs[i].priority) for s, n, i in r[key]]  # noqa: E731
g, lo = weather.realised(wb("greedy"), clear), weather.realised(wb("local"), clear)
(gm, gh), (lm, lh), (dm, dh) = weather.summary(g), weather.summary(lo), weather.summary(lo - g)
for v in (f"{gm:.3f} ± {gh:.3f}", f"{lm:.3f} ± {lh:.3f}", f"{dm:.3f} ± {dh:.3f}", f"{lm / gm:.3f}"[:4],
          f"{gm:.3f}+/-{gh:.3f}", f"{100 * (g > lo).mean():.1f} %"):
    stated("mc", v)
ok("ff2", lm >= 1.15 * gm and dm - dh > 0)
stated("margin pct", f"{100 * (lv / gv - 1):.1f}")
z = max(abs(clear[:, s:s + n].all(1).mean() - weather.p_complete(n)) / math.sqrt(weather.p_complete(n) * (1 - weather.p_complete(n)) / 1000)
        for s, n, _ in r["local"])
stated("worst z", f"{z:.2f}")
ok("analytic inside CI", abs(lm - lv) <= lh and abs(gm - gv) <= gh)

# ---- time seam, routes, fault
route = max(abs(sky.alt_deg(q, s.utc) - validator.alt_deg_lst(q, s.utc)) for q in reqs for s in slots)
stated("route diff", f"{route:.4f}")
ts = _kb.timescales
stated("WC06", f"{(ts.gast_hours(ts.WC06_JD_UT1, ts.WC06_JD_TT) - ts.WC06_GST_H) * 3600:.3f}"[1:])
ok("offset 330", (sky.sky_instant(slots[0], "local-as-utc").dt - slots[0].utc.dt).total_seconds() == 330 * 60)
f = scheduler.build(seed=2026, fault="local-as-utc")
fv = validator.validate(validator.rows_from_blocks(f["greedy"], f["reqs"], f["slots"]))
ok("fault betelgeuse", any("Betelgeuse: altitude -16.4 deg" in v for v in fv), fv)
stated("fault max airmass", f"{max(x['max_airmass'] for x in f['greedy_rows'] + f['local_rows']):.3f}")

# ---- agent
server, url = _kb.fake_model_server.start_in_thread()
try:
    text = agent_plan.ask(agent_plan.plan_prompt(reqs, slots), url)
    facts = agent_plan.explain_facts(r)
    expl = agent_plan.ask(agent_plan.explain_prompt(facts), url)
finally:
    server.shutdown()
    server.server_close()
verdict = agent_plan.decide(text, r["local"], reqs, slots)
ok("4 reasons", len(verdict["reasons"]) == 4, verdict)
for frag in ("-16.4 deg", "airmass 2.62", "airmass 6.50", "2026-11-20T02:20"):
    ok("reason " + frag, any(frag in v for v in verdict["reasons"]))
    stated("reason text", frag)
ok("explanation gate", agent_plan.checked_explanation(expl, facts, reqs)[0])
stated("explanation", expl[:60])

# ---- try it values
c8 = weather.clear_matrix(1000, len(slots), 7, a=0.08)
g8, l8 = weather.realised(wb("greedy"), c8), weather.realised(wb("local"), c8)
for v in (f"greedy {g8.mean():.3f} local {l8.mean():.3f} ratio {l8.mean() / g8.mean():.3f}", f"p={weather.p_complete(18, a=0.08):.3f}",
          f"greedy wins {(g8 > l8).mean():.3f}", f"pi_clear={weather.pi_clear(0.08):.3f}"):
    stated("try1", v)
old = sky.MAX_AIRMASS
sky.MAX_AIRMASS = 1.5
r15 = scheduler.build()
sky.MAX_AIRMASS = old
ok("try2", sum(bool(row.any()) for row in r15["ok"]) == 4 and abs(r15["local_value"] - r15["greedy_value"]) < 1e-12)
stated("try2 value", f"{r15['local_value']:.3f}")

# ---- question bank: calculations recomputed, code-reading executed, structure
IST = timezone(timedelta(hours=5, minutes=30))
CALC = {
    "calc_pi": f"{pi:.3f}",
    "calc_p6": f"{weather.p_complete(6):.3f}",
    "calc_ev": f"{3 * weather.p_complete(6) + 4 * weather.p_complete(12):.3f}",
    "calc_utc": datetime(2026, 11, 19, 18, 50, tzinfo=IST).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "calc_canopus": f"{90 - abs(28.46 - (-52.6957)):.2f} deg",
    "calc_ha": f"{3.0 * 15 - 79.1723:+.2f} deg".replace("+", "+"),
    "calc_ff2": f"{gm * 1.15:.3f}",
}
DISTRACTORS = {"calc_p6": f"{pi ** 6:.3f}", "calc_ev": "7.000", "calc_ff2": f"{gm + 0.15:.3f}"}
for q in QB:
    key = q.get("check")
    right = q["options"][q["answer"]]
    if q["type"] == "calculation":
        want = CALC[key]
        ok(q["id"], right == want or right.endswith("= " + want), f"{right!r} != {want!r}")
        if key in DISTRACTORS:
            ok(q["id"] + " distractor", DISTRACTORS[key] in q["options"], DISTRACTORS[key])
    if q["type"] == "code-reading":
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exec(q["code"], {})
        ok(q["id"], buf.getvalue().strip() == right, f"{buf.getvalue().strip()!r} != {right!r}")
TYPES = {"concept", "calculation", "code-reading", "debugging", "scenario", "design"}
ids, seen, pos, tags = set(), set(), collections.Counter(), collections.Counter()
longest = 0
for q in QB:
    ok(q["id"] + " fields", all(k in q for k in ("id", "level", "lesson", "type", "difficulty", "question", "options",
                                                   "answer", "explanation", "source")))
    ok(q["id"] + " level", q["level"] == "L600" and q["lesson"] == 5)
    ok(q["id"] + " type", q["type"] in TYPES)
    ok(q["id"] + " options", len(q["options"]) == 4 and len({o.lower() for o in q["options"]}) == 4)
    ok(q["id"] + " banned", not any(re.search(r"\b(all|none) of the (above|options)\b", o, re.I) for o in q["options"]))
    ok(q["id"] + " explanation", len(q["explanation"]) >= 30)
    ok(q["id"] + " unique id", q["id"] not in ids)
    k = re.sub(r"\W+", " ", (q["question"] + q.get("code", "")).lower())
    ok(q["id"] + " duplicate", k not in seen)
    ids.add(q["id"]); seen.add(k)
    pos[q["answer"]] += 1
    tags.update(q.get("tags", []))
    longest += max(range(4), key=lambda i: len(q["options"][i])) == q["answer"]
n = len(QB)
ok("qbank size", n >= 30, n)
ok("answer balance", all(0.20 <= pos[a] / n <= 0.30 for a in range(4)), dict(pos))
ok("longest share", longest / n <= 0.45, longest / n)
ok("mix", tags["seam"] >= 6 and tags["calc"] >= 5 and tags["diagnose"] >= 5 and tags["code"] >= 4, dict(tags))

# ---- lesson object and concept note
for key in ("id", "number", "level", "title", "category", "combines", "buildsOn", "seams", "failureLab", "buildTask",
            "scalingLimits", "designBrief", "architecture", "milestones", "rubric", "fitnessFunctions", "decisionRecords",
            "steps", "code", "codeWalkthrough", "tryIt", "validation", "platforms", "conceptNote"):
    ok("lesson key " + key, key in LESSON)
ok("code is scheduler.py", LESSON["code"] == (LAB / "scheduler.py").read_text(encoding="utf-8"))
ok("main file <= 150 lines", LESSON["code"].count("\n") <= 150)
for p in LESSON["decisionRecords"] + [LESSON["architecture"]["diagram"], LESSON["buildTask"]["solution"]]:
    ok("path " + p, (ROOT / p).exists())
for s in LESSON["seams"]:
    ok("seam test " + s["test"], (ROOT / s["test"]).exists())
for step in LESSON["steps"]:
    ok("step os " + step["title"], step.get("mac") and step.get("windows"))
words = len(NOTE.split())
ok("note words", 800 <= words <= 1000, words)
for t in ("astronomy", "simulation", "ai-agents"):
    titles = {l["number"]: l["title"] for lv in ("L100", "L200", "L300", "L400")
              for l in json.loads((ROOT.parent / t / "content" / f"{lv}.json").read_text(encoding="utf-8"))}
    for b in LESSON["buildsOn"]:
        if b["topic"] == t:
            ok("buildsOn title " + b["title"], titles.get(b["lesson"]) == b["title"])

if FAIL:
    print("FAIL")
    for x in FAIL:
        print(" -", x)
    sys.exit(1)
print(f"OK ({n} questions; answers {dict(sorted(pos.items()))}; tags {dict(tags)}; note {words} words)")
