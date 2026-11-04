"""L600 #08 checks: recompute every number in the lesson + qbank, execute every code-reading snippet. Prints OK.

Run from anywhere: python integrated/research/checks_08.py   (starts the shared fake model on 127.0.0.1; ~1-2 min)
"""
import base64
import collections
import contextlib
import io
import json
import math
import re
import sys
from pathlib import Path

INT = Path(__file__).resolve().parents[1]
LAB = INT / "labs" / "L600" / "08-secure-agent-tools"
sys.path.insert(0, str(LAB))
LESSON = json.loads((INT / "content" / "parts" / "08.json").read_text(encoding="utf-8"))
QB = json.loads((INT / "content" / "qbank" / "parts" / "08.json").read_text(encoding="utf-8"))
NOTE = (INT / "content" / "concepts" / "L600" / "08-secure-agent-tools.md").read_text(encoding="utf-8")
errors = []


def check(cond, msg):
    if not cond:
        errors.append(msg)


# ---------- lesson object shape
REQUIRED = ["id", "number", "level", "title", "category", "description", "outcome", "environment", "estimatedTime", "overview",
            "prerequisites", "designBrief", "architecture", "milestones", "rubric", "fitnessFunctions", "decisionRecords", "glossary",
            "steps", "code", "codeLanguage", "codeWalkthrough", "projectFiles", "expectedResults", "testCases", "tryIt",
            "troubleshooting", "learningTools", "inRealSystems", "useWhen", "simulatorVsReal", "caution", "checkpoint",
            "checkYourself", "sources", "next", "validation", "conceptNote", "conceptSummary", "platforms", "combines",
            "buildsOn", "seams", "failureLab", "buildTask", "scalingLimits"]
for k in REQUIRED:
    check(k in LESSON, f"lesson missing {k}")
check(LESSON["level"] == "L600" and LESSON["number"] == 8, "level/number")
check(4 <= len(LESSON["milestones"]) <= 6 and 3 <= len(LESSON["seams"]) <= 5 and 4 <= len(LESSON["buildsOn"]) <= 8, "counts")
check(2 <= len(LESSON["decisionRecords"]) <= 4 and 5 <= len(LESSON["codeWalkthrough"]) <= 7 and len(LESSON["tryIt"]) == 2, "counts 2")
check(len(LESSON["learningTools"]) <= 3 and 2 <= len(LESSON["scalingLimits"]) <= 3, "tools/scaling")
check(all("mac" in s and "windows" in s for s in LESSON["steps"]), "steps need mac+windows")
check(LESSON["code"] == (LAB / "host.py").read_text(encoding="utf-8"), "code field != host.py")
check(len(LESSON["code"].splitlines()) <= 150, "main file > 150 lines")
for p in [LESSON["architecture"]["diagram"], *LESSON["decisionRecords"], LESSON["buildTask"]["solution"],
          *[m["test"] for m in LESSON["milestones"]], *[s["test"] for s in LESSON["seams"]], *[f["test"] for f in LESSON["fitnessFunctions"]]]:
    check((INT / p).exists(), f"missing path {p}")
for adr in LESSON["decisionRecords"]:
    text = (INT / adr).read_text(encoding="utf-8")
    check(all(h in text for h in ("## Status", "## Context", "## Decision", "## Consequences")), f"ADR sections {adr}")
words = len(NOTE.split())
check(800 <= words <= 1000, f"concept note {words} words")
kbroot = INT.parent
for b in LESSON["buildsOn"]:
    titles = {l["number"]: l["title"] for lv in ("L100", "L200", "L300", "L400")
              for l in json.loads((kbroot / b["topic"] / "content" / f"{lv}.json").read_text(encoding="utf-8"))}
    check(titles.get(b["lesson"]) == b["title"], f"buildsOn title mismatch {b['topic']} {b['lesson']}")
tools = json.loads((kbroot / "shared" / "learning-tools.json").read_text(encoding="utf-8"))
catalog = {t["name"] for topic in ("ai-agents", "cryptography", "application-architecture") for t in tools[topic]}
check(all(t["name"] in catalog for t in LESSON["learningTools"]), "learning tool not in catalog")

# ---------- recompute the lab numbers
import audit  # noqa: E402
import corpus  # noqa: E402
import manifest  # noqa: E402
import scenarios as sc  # noqa: E402
from adapters import FakeClock, start_fake_model  # noqa: E402
from capability import TokenService, parse  # noqa: E402
from policy_engine import RegoPolicy  # noqa: E402
from run_project import audit_mutations, ttl_fitness  # noqa: E402

_, url = start_fake_model()
registry, rejected = sc.load_registry()
check(len(registry) == 5 and rejected == [], "registry")
signed = sc.signed_pack()
check(len(base64.b64decode(signed[0]["sig"])) == 64 and signed[0]["kid"] == "5fb0188328180fc4", "sig/kid")
rows = sc.run_corpus(url, registry)
naive = sc.run_corpus(url, registry, {"naive-host"})
got = (len(rows), sum(r["requested"] for r in rows), sum(r["executed"] for r in rows), sum(r["unscoped_side_effects"] for r in rows),
       sum(r["executed"] for r in naive), sum(r["effects"] for r in naive))
check(got == (40, 24, 0, 0, 24, 16), f"corpus {got}")
check(len(corpus.phrasings()) == 5, "phrasings")
env2, _ = sc.s2_injection(url, registry)
check(len(env2.audit.entries) == 5, "S2 entries")
check(audit_mutations(env2.audit, set())[:2] == (31, 31) and audit_mutations(env2.audit, {"per-entry-hash"})[:2] == (20, 31), "mutations")
check(ttl_fitness(set()) == (50, 50, True) and ttl_fitness({"no-expiry"})[0] == 0, "ttl")
tok = TokenService(FakeClock(), root_key=b"\x08" * 32).session_token("s-1", corpus.SCOPE, ttl=60, arg_rules=corpus.ARG_RULES)
check(len(tok) == 252 and len(parse(tok)[1]) == 4, f"token length {len(tok)}")
check(RegoPolicy().revision == "c332681181f5", "policy revision")
sys.path.insert(0, str(LAB / "try_it"))
import try_it_1  # noqa: E402
import try_it_2  # noqa: E402
check(str(try_it_1.run()) in LESSON["tryIt"][0]["expected"], "tryIt 1")
check(str(try_it_2.run()) in LESSON["tryIt"][1]["expected"], "tryIt 2")
lesson_text = json.dumps(LESSON)
for needle in ['\\"requested\\": 24', '\\"naive_effects\\": 16', '\\"detected\\": 31, \\"mutations\\": 31', '\\"expired_at_ttl\\": 50',
               "passed\\\": 4", "5fb0188328180fc4", "1790000060"]:
    check(needle in lesson_text, f"lesson lacks {needle}")
for needle in ["24 payloads", "executed 0", "16 side effects", "5 entries", "31 seeded edits", "20 of 31", "Fifty tokens", "13 PASS"]:
    check(needle in NOTE, f"note lacks {needle}")

# ---------- qbank structure
check(len(QB) >= 30, "qbank < 30")
pos, types = collections.Counter(q["answer"] for q in QB), collections.Counter(q["type"] for q in QB)
for q in QB:
    check(q["level"] == "L600" and q["lesson"] == 8 and len(q["options"]) == 4 and len(set(q["options"])) == 4, f"{q['id']} shape")
    check(q["answer"] in range(4) and len(q["explanation"]) >= 30 and q["difficulty"] in (1, 2, 3), f"{q['id']} fields")
    check(not re.search(r"\b(all|none) of the (above|options)\b", " ".join(q["options"]), re.I), f"{q['id']} banned option")
check(all(0.2 <= pos[a] / len(QB) <= 0.3 for a in range(4)), f"answer balance {pos}")
longest = sum(1 for q in QB if max(range(4), key=lambda i: len(q["options"][i])) == q["answer"])
check(longest / len(QB) <= 0.45, f"correct is longest in {longest}")
seam_ids = {f"int-L600-08-{i:03d}" for i in range(1, 8)}
check(sum(q["id"] in seam_ids for q in QB) >= 6, "seam questions")
check(types["calculation"] >= 5 and types["debugging"] >= 5 and types["code-reading"] >= 4, f"mix {types}")

# ---------- calculation answers, recomputed
by_id = {q["id"]: q for q in QB}
CALC = {
    "int-L600-08-008": str(1 + 4),
    "int-L600-08-009": str(math.ceil(32 * 8 / 6)),
    "int-L600-08-010": f"{round((1 - 0.95 ** 24) * 100)}%",
    "int-L600-08-011": str(8 * 5 + (8 - 1) + 2),
    "int-L600-08-012": str(1790000000 + 60 - 1),
    "int-L600-08-013": str(4 * math.ceil(64 / 3)),
    "int-L600-08-014": f"{int(11 / 31 * 100)}%",
}
check(len(base64.urlsafe_b64encode(bytes(32)).rstrip(b"=")) == 43 and len(base64.b64encode(bytes(64))) == 88, "b64 lengths")
check(5 * (3 + 1 + 1) + 4 + 2 == 31, "31 = n=5 formula")
for qid, ans in CALC.items():
    q = by_id[qid]
    check(q["type"] == "calculation" and q["options"][q["answer"]] == ans, f"{qid}: expected {ans}, got {q['options'][q['answer']]}")

# ---------- code-reading snippets, executed
for q in QB:
    if q["type"] == "code-reading":
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exec(q["code"], {})
        check(buf.getvalue().strip() == q["options"][q["answer"]], f"{q['id']}: printed {buf.getvalue().strip()!r}")
        check(len(q["code"].splitlines()) <= 15, f"{q['id']} snippet too long")

if errors:
    print("\n".join("FAIL " + e for e in errors))
    sys.exit(1)
print(f"OK - lesson + {len(QB)} questions ({dict(types)}), corpus {got}, note {words} words")
