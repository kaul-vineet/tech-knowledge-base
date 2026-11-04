"""Checks for L600 project 01 (post-quantum secure messaging over a replicated log).
Recomputes every number used in content/parts/01.json, the concept note, the ADRs and qbank/parts/01.json from code
that runs, executes every code-reading snippet, and validates the lesson and question-bank structure.
Run from anywhere: python integrated/research/checks_01.py   -> prints OK, exit 0 (takes a few minutes: 10k-message run)."""
import contextlib
import io
import json
import math
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # kb/integrated
LAB = ROOT / "labs" / "L600" / "01-pq-replicated-messaging"
sys.path.insert(0, str(LAB))
ERRORS = []


def check(cond, msg):
    if not cond:
        ERRORS.append(msg)


def norm(s):
    return re.sub(r"\W+", " ", s.lower()).strip()


lesson = json.loads((ROOT / "content" / "parts" / "01.json").read_text(encoding="utf-8"))
qs = json.loads((ROOT / "content" / "qbank" / "parts" / "01.json").read_text(encoding="utf-8"))
note = (ROOT / "content" / "concepts" / "L600" / "01-pq-replicated-messaging.md").read_text(encoding="utf-8")

# ---------- 1. lesson structure
REQUIRED = ["id", "number", "level", "title", "category", "description", "outcome", "environment", "estimatedTime",
            "overview", "prerequisites", "designBrief", "architecture", "milestones", "rubric", "fitnessFunctions",
            "decisionRecords", "glossary", "steps", "code", "codeLanguage", "codeWalkthrough", "projectFiles",
            "expectedResults", "testCases", "tryIt", "troubleshooting", "learningTools", "inRealSystems", "useWhen",
            "simulatorVsReal", "caution", "checkpoint", "checkYourself", "sources", "next", "validation", "conceptNote",
            "conceptSummary", "platforms", "combines", "buildsOn", "seams", "failureLab", "buildTask", "scalingLimits"]
for k in REQUIRED:
    check(k in lesson, f"lesson missing {k}")
check(lesson["level"] == "L600" and lesson["number"] == 1 and lesson["category"] == "Integrated project", "lesson id fields")
check(set(lesson["combines"]) == {"cryptography", "distributed-systems", "application-architecture"}, "combines")
check(4 <= len(lesson["buildsOn"]) <= 8, "buildsOn 4-8")
check(3 <= len(lesson["seams"]) <= 5, "seams 3-5")
check(4 <= len(lesson["milestones"]) <= 6, "milestones 4-6")
check(2 <= len(lesson["decisionRecords"]) <= 4, "ADRs 2-4")
check(5 <= len(lesson["codeWalkthrough"]) <= 7, "codeWalkthrough 5-7")
check(len(lesson["tryIt"]) == 2 and len(lesson["learningTools"]) <= 3, "tryIt x2, learningTools <= 3")
check(2 <= len(lesson["scalingLimits"]) <= 3, "scalingLimits 2-3")
check(all(s.get("mac") and s.get("windows") for s in lesson["steps"]), "every step has mac + windows")
check(lesson["code"] == (LAB / "pqmsg.py").read_text(encoding="utf-8"), "lesson code == pqmsg.py")
check(len(lesson["code"].splitlines()) <= 165, "main file about 150 lines")
for f in ("inject", "symptom", "diagnose", "fix", "test"):
    check(lesson["failureLab"].get(f), f"failureLab.{f}")
for f in ("task", "acceptance", "solution"):
    check(lesson["buildTask"].get(f), f"buildTask.{f}")
paths = [lesson["architecture"]["diagram"], lesson["buildTask"]["solution"], *lesson["decisionRecords"]]
paths += [m["test"] for m in lesson["milestones"]] + [s["test"] for s in lesson["seams"]]
paths += [f["test"].split("::")[0] for f in lesson["fitnessFunctions"]] + [p["path"] for p in lesson["projectFiles"]]
for p in paths:
    check((ROOT / p).exists(), f"path does not exist: {p}")
for adr in lesson["decisionRecords"]:
    text = (ROOT / adr).read_text(encoding="utf-8")
    check(all(h in text for h in ("## Status", "## Context", "## Decision", "## Consequences")) and text.startswith("# ADR"), f"Nygard sections in {adr}")
titles = {}
for topic in ("cryptography", "distributed-systems", "application-architecture"):
    for lv in ("L100", "L200", "L300", "L400", "L500"):
        for item in json.loads((ROOT.parent / topic / "content" / f"{lv}.json").read_text(encoding="utf-8")):
            titles[(topic, item["number"])] = item["title"]
for b in lesson["buildsOn"]:
    check(titles.get((b["topic"], b["lesson"])) == b["title"], f"buildsOn title mismatch {b['topic']} #{b['lesson']}")
words = len(note.split())
check(800 <= words <= 1000, f"concept note {words} words (800-1000)")
for h in ("## Why combine these", "## Architecture walkthrough", "## The seams", "## Worked run", "## Failure modes at scale", "## Common mistakes"):
    check(h in note, f"concept note heading {h}")

# ---------- 2. question bank structure (QBANK-SPEC rules + L600 mix)
TYPES = {"concept", "calculation", "code-reading", "debugging", "scenario", "design"}
check(len(qs) >= 30, "qbank >= 30")
seen = set()
for q in qs:
    for k in ("id", "level", "lesson", "type", "difficulty", "question", "options", "answer", "explanation", "source"):
        check(k in q, f"{q.get('id')}: missing {k}")
    check(q["level"] == "L600" and q["lesson"] == 1 and q["type"] in TYPES and q["difficulty"] in (1, 2, 3), f"{q['id']}: fields")
    check(len(q["options"]) == 4 and len(set(map(norm, q["options"]))) == 4, f"{q['id']}: 4 distinct options")
    check(0 <= q["answer"] <= 3 and len(q["explanation"]) >= 30, f"{q['id']}: answer/explanation")
    check(not any(re.search(r"\b(all|none) of the (above|options)\b", o, re.I) for o in q["options"]), f"{q['id']}: banned option")
    key = norm(q["question"] + " " + q.get("code", ""))
    check(key not in seen, f"{q['id']}: duplicate")
    seen.add(key)
types = Counter(q["type"] for q in qs)
seam_qs = [q for q in qs if "seam" in q["source"].lower() or "ADR" in q["source"]]
check(len(seam_qs) >= 6, f"seam/integration questions {len(seam_qs)} (>= 6)")
check(types["calculation"] >= 5 and types["debugging"] >= 5 and types["code-reading"] >= 4, f"type mix {dict(types)}")
pos = Counter(q["answer"] for q in qs)
for a in range(4):
    check(0.20 <= pos[a] / len(qs) <= 0.30, f"answer {'ABCD'[a]} share {pos[a] / len(qs):.0%}")
longest = sum(max(range(4), key=lambda i: len(q["options"][i])) == q["answer"] for q in qs)
check(longest / len(qs) <= 0.45, f"correct option longest in {longest}/{len(qs)}")
Q = {q["id"]: q for q in qs}


def correct(qid):
    return Q[qid]["options"][Q[qid]["answer"]]


# ---------- 3. recompute calculations and execute code-reading snippets
import group_crypto as gc  # noqa: E402
import pqmsg  # noqa: E402
import replicated_state  # noqa: E402
import run_project  # noqa: E402
import scenarios as sc  # noqa: E402

prob = sc.prob
kp_holder = gc.Device("alice")
w = gc.welcome(kp_holder.key_package, b"\x00" * 32, 1, "alice")
welcome_b = gc.welcome_bytes(w)
check(welcome_b == 1088 + 32 + 12 + 32 + 16 == 1180 and correct("int-L600-01-009") == "1,180 B", "Q009 welcome bytes")
kp_b = len(kp_holder.key_package)
check(kp_b == 1216 and correct("int-L600-01-010") == f"{2400 - kp_b - welcome_b} B", "Q010 headroom")
q32 = prob.q_for_probability(2**-32, 2**96)
check(round(math.log2(q32), 1) == 32.5 and correct("int-L600-01-011") == f"about 2^{math.log2(q32):.1f} ({q32:.1e})".replace("e+0", "e"), f"Q011 {q32:.3e}")
days = 2**32 / 10_000 / 86_400
check(correct("int-L600-01-012") == f"about {days:.1f} days" and f"{days:.2f}" == "4.97", "Q012 days")
check(correct("int-L600-01-013") == f"{101 * welcome_b:,} B", "Q013 rotation bytes")
check(correct("int-L600-01-014") == f"{prob.collision_upper(10_000, 2**96):.1e}", "Q014 union bound")
for qid in ("int-L600-01-015", "int-L600-01-016", "int-L600-01-017", "int-L600-01-018", "int-L600-01-019", "int-L600-01-020"):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        exec(compile(Q[qid]["code"], qid, "exec"), {})
    check(out.getvalue().strip() == correct(qid), f"{qid}: snippet printed {out.getvalue().strip()!r}, answer {correct(qid)!r}")
for q in qs:
    if q["type"] in ("calculation", "code-reading"):
        check(q["id"] in {f"int-L600-01-{i:03d}" for i in range(9, 21)}, f"{q['id']}: unchecked calculation/code item")

# ---------- 4. recompute the lesson's expected results (the scorecard lines) from code that runs
calls = [0]
orig_apply = replicated_state.State.apply


def counted(self, i, c):
    calls[0] += 1
    return orig_apply(self, i, c)


rows = [sc.m1_welcome(), sc.m2_replicated(), sc.m3_api(), sc.m4_rotation(), sc.m5_contract(), sc.seam_nonce_failover(),
        sc.seam_rotation(), sc.seam_idempotency(), sc.seam_contract()]
replicated_state.State.apply = counted
f1, f2 = sc.fitness_traffic()
replicated_state.State.apply = orig_apply
rows += [f1, f2, sc.fitness_handshake(), sc.fitness_key_limit()]
rows.append({"scorecard": "L600-01 pq-replicated-messaging", "injected": None, "passed": sum(r["pass"] for r in rows),
             "total": len(rows), "decided_by": "code"})
expected = [json.loads(line) for line in lesson["expectedResults"]]
check(len(expected) == len(rows), "expectedResults line count")
for got, exp in zip(rows, expected):
    check(got == exp, f"expectedResults differ:\n  got {json.dumps(got)}\n  exp {json.dumps(exp)}")
check(calls[0] == 1_061_514, f"apply calls in the 10k run: {calls[0]}")
check(f"{prob.collision_upper(2526, 2**96):.1e}" == f1["birthday_bound_per_epoch"] == "4.0e-23", "per-epoch bound")
lab = run_project.failure_lab()
check(lab["reused_nonces"] == 109 and lab["failovers"] == 49 and lab["smallest_reused_nonce_values"] == [1, 2, 3, 4, 5], f"failure lab {lab}")
check(lab["keystream_reuse"]["recovered"] == lab["keystream_reuse"]["actual"] == "msg 00010 from bob: status green", "keystream recovery")
inj = sc.fitness_traffic({"leader-counter"}, 2000)[0]
check((inj["failovers"], inj["ciphertexts_sealed"], inj["reused_nonces"]) == (43, 2022, 96), f"inject F1 at 2000: {inj}")

# ---------- 5. tryIt outputs
t1 = subprocess.run([sys.executable, str(LAB / "try_it" / "try_it_1.py")], capture_output=True, text=True, encoding="utf-8").stdout
check("AES-256-GCM      recovered == secret: True" in t1 and "AES-256-GCM-SIV  recovered == secret: False" in t1, "tryIt 1")
t2 = subprocess.run([sys.executable, str(LAB / "try_it" / "try_it_2.py")], capture_output=True, text=True, encoding="utf-8").stdout
for s in ("3 members: welcomes 4,720 B raw, log entry 6,563 B JSON", "30 members: welcomes 36,580 B raw, log entry 50,559 B JSON",
          "100 members: welcomes 119,180 B raw, log entry 164,659 B JSON", "after 6.074e+09 messages"):
    check(s in t2, f"tryIt 2 line: {s}")

# ---------- 6. numbers quoted in prose (lesson, concept note, ADRs) come from the values above
prose = json.dumps(lesson) + note + "".join((ROOT / a).read_text(encoding="utf-8") for a in lesson["decisionRecords"])
entry100 = int(re.search(r"100 members: welcomes [\d,]+ B raw, log entry ([\d,]+) B JSON", t2).group(1).replace(",", ""))
facts = [("1,216", f"{kp_b:,}"), ("1,180", f"{welcome_b:,}"), ("2,396", f"{kp_b + welcome_b:,}"),
         ("10,101", f"{f1['ciphertexts_sealed']:,}"), ("205", str(f1["failovers"])), ("109", str(lab["reused_nonces"])),
         ("49", str(lab["failovers"])), ("32", str(rows[7]["guard_proven_no_apply_dedupe_duplicates"])),
         ("164,659", f"{entry100:,}"), ("119,180", f"{101 * welcome_b:,}"), ("1,061,514", f"{calls[0]:,}"), ("4.97", f"{days:.2f}")]
for text, value in facts:
    check(text == value, f"quoted {text} but code gives {value}")
    check(text in prose, f"prose does not mention {text}")

if ERRORS:
    print("FAIL")
    for e in ERRORS:
        print(" -", e)
    sys.exit(1)
print(f"OK  lesson + {len(qs)} questions ({dict(types)}), answers {dict(sorted(pos.items()))}, concept note {words} words, "
      f"{len(rows)} scorecard lines recomputed, apply calls {calls[0]:,}")
