"""Recompute every number in L600 #02 (lesson, concept note, question bank) from code that runs. Prints OK, exit 0.

Run from kb/:  python integrated/research/checks_02.py
"""
import collections
import contextlib
import io
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

INTEGRATED = Path(__file__).resolve().parents[1]
KB = INTEGRATED.parent
LAB = INTEGRATED / "labs" / "L600" / "02-quantum-safe-migration"
sys.path.insert(0, str(LAB))

import crypto_registry as registry  # noqa: E402
import estimates  # noqa: E402
import fitness  # noqa: E402
import fleet  # noqa: E402
import inventory  # noqa: E402
import migration_plan as mp  # noqa: E402
import run_project  # noqa: E402
import seams  # noqa: E402
import shor_sim  # noqa: E402

sys.path.insert(0, str(LAB / "try_it"))
import experiments  # noqa: E402

LESSON = json.loads((INTEGRATED / "content" / "parts" / "02.json").read_text(encoding="utf-8"))
QBANK = json.loads((INTEGRATED / "content" / "qbank" / "parts" / "02.json").read_text(encoding="utf-8"))
NOTE = (INTEGRATED / "content" / "concepts" / "L600" / "02-quantum-safe-migration.md").read_text(encoding="utf-8")
README = (LAB / "README.md").read_text(encoding="utf-8")
problems = []


def check(cond, msg):
    if not cond:
        problems.append(msg)


# ---------- 1. lesson structure ----------
REQUIRED = ["id", "number", "level", "title", "category", "description", "outcome", "environment", "estimatedTime", "overview",
            "prerequisites", "designBrief", "architecture", "milestones", "rubric", "fitnessFunctions", "decisionRecords",
            "glossary", "steps", "code", "codeLanguage", "codeWalkthrough", "projectFiles", "expectedResults", "testCases",
            "tryIt", "troubleshooting", "learningTools", "inRealSystems", "useWhen", "simulatorVsReal", "caution",
            "checkpoint", "checkYourself", "sources", "next", "validation", "conceptNote", "conceptSummary", "platforms",
            "combines", "buildsOn", "seams", "failureLab", "buildTask", "scalingLimits"]
for k in REQUIRED:
    check(k in LESSON, f"lesson missing {k}")
check(LESSON["level"] == "L600" and LESSON["number"] == 2 and LESSON["category"] == "Integrated project", "lesson header")
check(set(LESSON["combines"]) == {"quantum-computing", "cryptography", "application-architecture"}, "combines")
check(4 <= len(LESSON["milestones"]) <= 6 and 3 <= len(LESSON["seams"]) <= 5 and 4 <= len(LESSON["buildsOn"]) <= 8, "counts")
check(5 <= len(LESSON["codeWalkthrough"]) <= 7 and len(LESSON["tryIt"]) == 2 and len(LESSON["learningTools"]) <= 3, "counts 2")
check(2 <= len(LESSON["decisionRecords"]) <= 4 and 2 <= len(LESSON["scalingLimits"]) <= 3, "ADRs / scaling limits")
check(all(s.get("mac") and s.get("windows") for s in LESSON["steps"]), "every step needs mac + windows")
check(LESSON["code"] == (LAB / "run_project.py").read_text(encoding="utf-8"), "code field != run_project.py")
check(len(LESSON["code"].splitlines()) <= 155, "main file too long")
for path in [m["test"] for m in LESSON["milestones"]] + [s["test"] for s in LESSON["seams"]] + LESSON["decisionRecords"] + \
        [LESSON["architecture"]["diagram"], LESSON["buildTask"]["solution"]] + [f["test"].split("::")[0] for f in LESSON["fitnessFunctions"]]:
    check((INTEGRATED / path).exists(), f"missing file {path}")
for adr in LESSON["decisionRecords"]:
    text = (INTEGRATED / adr).read_text(encoding="utf-8")
    check(all(h in text for h in ("## Status", "## Context", "## Decision", "## Consequences")), f"ADR sections {adr}")
for b in LESSON["buildsOn"]:
    lv = {n: lvl for lvl in ("L100", "L200", "L300", "L400", "L500")
          for n in [x["number"] for x in json.loads((KB / b["topic"] / "content" / f"{lvl}.json").read_text(encoding="utf-8"))]}
    titles = {x["number"]: x["title"] for x in json.loads((KB / b["topic"] / "content" / f"{lv[b['lesson']]}.json").read_text(encoding="utf-8"))}
    check(titles.get(b["lesson"]) == b["title"], f"buildsOn title mismatch {b['topic']} #{b['lesson']}")
catalog = json.loads((KB / "shared" / "learning-tools.json").read_text(encoding="utf-8"))
names = {t["name"] for k, v in catalog.items() if isinstance(v, list) for t in v}
check(all(t["name"] in names for t in LESSON["learningTools"]), "learning tool not in catalog")
words = len(NOTE.split())
check(800 <= words <= 1000, f"concept note {words} words")
for h in ("## Why combine these", "## Architecture walkthrough", "## The seams", "## Worked run", "## Failure modes at scale", "## Common mistakes"):
    check(h in NOTE, f"note heading {h}")

# ---------- 2. recompute the numbers ----------
s15, s15g, s21 = shor_sim.shor(15, 7), shor_sim.shor(15, 7, gate_level=True), shor_sim.shor(21, 2)
check((s15["qubits"], s15["p_success_per_run"], s15["successes"], s15["factors"]) == (12, 0.5, 101, [3, 5]), "N=15")
check((s21["qubits"], s21["p_success_per_run"], s21["successes"], s21["factors"]) == (15, 0.3222, 66, [3, 7]), "N=21")
check(s15g["gates"]["cx"] == 14 and s15g["gates"]["ccx"] == 5, "gate-level counts")
check(s21["gates"]["iqft_cp"] == 45 and s21["statevector_bytes"] == 524288 == 512 * 1024, "N=21 gates/bytes")
peaks = {m: round(float(p), 4) for m, p in enumerate(s15["probs"]) if p > 1e-9}
check(peaks == {0: 0.25, 64: 0.25, 128: 0.25, 192: 0.25}, "N=15 peaks")
check(all(shor_sim.matches_fft_shortcut(s) for s in (s15, s15g, s21)), "closed form")
ge = estimates.ge_formula(2048)
check((ge["logical_qubits"], ge["toffoli"]) == (6190, 2624225018), "GE formula")
before, after = inventory.scan("before"), inventory.scan("after")
expected_inv = json.loads((LAB / "EXPECTED_INVENTORY.json").read_text(encoding="utf-8"))
sc = inventory.score(before, expected_inv["before"])
check(len(before) == 10 and sc["recall"] == sc["precision"] == 1.0, "inventory")
check(mp.summary(mp.plan(before)) == {"P1": 3, "P2-kex": 2, "P2-sig": 3, "none": 2}, "plan before")
check(mp.summary(mp.plan(after)) == {"P1": 2, "P2-kex": 2, "P2-sig": 2, "done": 2, "none": 2}, "plan after")
check(not mp.exposed(7, 3, mp.HORIZON) and mp.exposed(12, 2, mp.HORIZON) and 12 + 2 - 10 == 4 and 10 + 3 - 10 == 3, "Mosca")
sizes = seams.measured_sizes()
check(sizes["X25519MLKEM768"] == {"client_share": 1216, "server_share": 1120} and 1216 + 1120 == 2336, "hybrid sizes")
check(sizes["ML-DSA-65"] == {"public_key": 1952, "signature": 3309} and sizes["ML-DSA-87"] == {"public_key": 2592, "signature": 4627}, "ML-DSA sizes")
late = fitness.f1_no_classical_kex_for_exposed_data(after, today=date(2027, 7, 1))
check(len(late["violations"]) == 2, "F1 overdue")


def phase(variant, versions, required, sig=None):
    registry.reset()
    old = registry.POLICY["messaging"]["sig"]
    if sig:
        registry.POLICY["messaging"]["sig"] = sig
    registry.FLAGS.set("pq_required.messaging", required)
    try:
        return fleet.run_traffic(fleet.load_channel(variant), fleet.make_fleet(versions))
    finally:
        registry.POLICY["messaging"]["sig"] = old
        registry.reset()


mixed = fitness.f2_handshake_budget(phase("migrated", [2, 2, 1], False)["tap"])
allv2 = fitness.f2_handshake_budget(phase("migrated", [2, 2, 2], True)["tap"])
big = fitness.f2_handshake_budget(phase("migrated", [2, 2, 2], True, sig="ML-DSA-87")["tap"])
check((mixed["client_flight_bytes"], mixed["handshake_bytes"]) == (1352, 5871), f"mixed budget {mixed}")
check(allv2["handshake_bytes"] == 5827 and big["handshake_bytes"] == 7145 == 5827 + 4627 - 3309, "ML-DSA-87 budget")
check(big["handshake_bytes"] - 6144 == 1001, "overshoot")
sweep = experiments.horizon_sweep()
check([len(sweep[z]) for z in (5, 10, 15)] == [5, 3, 0], "horizon sweep")
byp = phase("bypass", [2, 2, 2], True)
check((byp["delivered"], byp["refused"]) == (0, 6), "bypass loud once required")

# ---------- 3. the scorecard in the lesson is what the code prints ----------
out = subprocess.run([sys.executable, str(LAB / "run_project.py")], capture_output=True, text=True, encoding="utf-8", cwd=LAB)
check(out.returncode == 0 and out.stdout.splitlines() == LESSON["expectedResults"], "expectedResults != run_project output")
c_bypass = run_project.collect("bypass")
with contextlib.redirect_stdout(io.StringIO()) as buf:
    code = run_project.main(["--inject", "bypass"])
bypass_lines = buf.getvalue().splitlines()
check(code == 1 and all(line in README for line in bypass_lines if '"pass": false' in line), "bypass lines in README")
f3 = [v["f3"] for v in c_bypass["phases"].values()]
check(sum(v["handshakes"] for v in f3) == 24 and sum(v["client_kex_resolutions"] for v in f3) == 0, "bypass F3 numbers")
c_down = run_project.collect("downgrade")
s4 = seams.s4_rollout_to_policy(c_down["phases"]["rollback-v1"], c_down["phases"]["rollback-v1"]["servers"])
check(s4["classical_sessions"] == 2 and s4["refused"] == 0, "downgrade S4 numbers")

for token in ["0.3222", "101/200", "66/200", "1,352", "5,871", "7,145", "512 KiB", "14 CX, 5 CCX", "24 handshakes",
              "12 + 2 - 10 = 4", "10 + 3 - 10 = 3", "7 + 3 = 10", "1,400 / 6,144"]:
    check(token in NOTE, f"concept note token {token}")

# ---------- 4. question bank ----------
check(len(QBANK) >= 30, "qbank size")
focus = collections.Counter(q["focus"] for q in QBANK)
check(focus["seam"] >= 6 and focus["calculation"] >= 5 and focus["diagnose"] >= 5 and focus["code-reading"] >= 4, f"focus {focus}")
pos = collections.Counter(q["answer"] for q in QBANK)
check(all(0.2 <= pos[a] / len(QBANK) <= 0.3 for a in range(4)), f"answer balance {pos}")
longest = sum(1 for q in QBANK if max(range(4), key=lambda i: len(q["options"][i])) == q["answer"])
check(longest / len(QBANK) <= 0.45, "correct option too often the longest")
seen = set()
for q in QBANK:
    for k in ("id", "level", "lesson", "type", "difficulty", "question", "options", "answer", "explanation", "source"):
        check(k in q, f"{q.get('id')} missing {k}")
    check(q["level"] == "L600" and q["lesson"] == 2 and q["id"] not in seen, f"{q['id']} header")
    seen.add(q["id"])
    check(len(q["options"]) == 4 and len({o.lower() for o in q["options"]}) == 4, f"{q['id']} options")
    check(len(q["explanation"]) >= 30 and not re.search(r"\b(all|none) of the (above|options)\b", " ".join(q["options"]), re.I),
          f"{q['id']} explanation/options")
by_id = {q["id"]: q for q in QBANK}


def correct(qid):
    q = by_id[qid]
    return q["options"][q["answer"]]


rows_b = mp.plan(before)
records = next(r for r in rows_b if r["service"] == "records")
check(correct("int02-L600-008").startswith(records["priority"]), "Q8")
check(correct("int02-L600-009") == f"{s21['statevector_bytes']:,} bytes", "Q9")
check(correct("int02-L600-010") == f"{sizes['X25519MLKEM768']['client_share'] + sizes['X25519MLKEM768']['server_share']:,}", "Q10")
check("5,827" in by_id["int02-L600-011"]["question"] and correct("int02-L600-011") == f"{big['handshake_bytes'] - 6144:,}", "Q11")
check(correct("int02-L600-012") == str(s21["gates"]["iqft_cp"]), "Q12")
check(correct("int02-L600-013") == str(s15["p_success_per_run"]), "Q13")
check(correct("int02-L600-014") == f"{ge['logical_qubits']:,}", "Q14")
for q in QBANK:
    if q["type"] == "code-reading":
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            exec(compile(q["code"], q["id"], "exec"), {})
        check(buf.getvalue().strip() == correct(q["id"]), f"{q['id']} code output {buf.getvalue().strip()!r}")
check("24 handshakes" in by_id["int02-L600-020"]["question"] and "classical_sessions = 2" in by_id["int02-L600-023"]["question"]
      and "6 of 6" in by_id["int02-L600-024"]["question"], "diagnose numbers")

if problems:
    print("\n".join("PROBLEM: " + p for p in problems))
    sys.exit(1)
print(f"OK - lesson, concept note ({words} words), {len(QBANK)} questions {dict(focus)}, answers {dict(sorted(pos.items()))}")
