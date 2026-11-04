"""Recompute every number in L600 #06 (lesson part, concept note, qbank) from the lab code; print OK and exit 0.
python integrated/research/checks_06.py        (takes a few minutes: it rebuilds the seeded worlds)"""
import collections
import contextlib
import hashlib
import io
import json
import math
import re
import subprocess
import sys
from pathlib import Path

INT = Path(__file__).resolve().parents[1]
LAB = INT / "labs" / "L600" / "06-signed-science-data"
sys.path.insert(0, str(LAB))

import canonical as C  # noqa: E402
import checks  # noqa: E402
import merkle  # noqa: E402
import publisher as P  # noqa: E402
import science  # noqa: E402
from world import World  # noqa: E402

ERR = []


def expect(label, got, want):
    if got != want:
        ERR.append(f"{label}: got {got!r}, want {want!r}")


lesson = json.loads((INT / "content" / "parts" / "06.json").read_text(encoding="utf-8"))
qbank = json.loads((INT / "content" / "qbank" / "parts" / "06.json").read_text(encoding="utf-8"))
note = (INT / "content" / "concepts" / "L600" / "06-signed-science-data.md").read_text(encoding="utf-8")
text = json.dumps(lesson, ensure_ascii=False) + note

# --- lesson object shape
for k in ("id", "number", "level", "title", "category", "combines", "buildsOn", "seams", "failureLab", "buildTask",
          "scalingLimits", "milestones", "rubric", "fitnessFunctions", "decisionRecords", "steps", "code",
          "codeWalkthrough", "tryIt", "validation", "platforms", "sources", "conceptNote"):
    if k not in lesson:
        ERR.append(f"lesson: missing {k}")
expect("level", lesson["level"], "L600")
expect("number", lesson["number"], 6)
expect("combines", lesson["combines"], ["astronomy", "cryptography", "distributed-systems"])
expect("code == run_project.py", lesson["code"], (LAB / "run_project.py").read_text(encoding="utf-8"))
if not 4 <= len(lesson["buildsOn"]) <= 8 or not 3 <= len(lesson["seams"]) <= 5 or not 4 <= len(lesson["milestones"]) <= 6:
    ERR.append("lesson: buildsOn 4-8, seams 3-5, milestones 4-6")
if not 5 <= len(lesson["codeWalkthrough"]) <= 7 or len(lesson["tryIt"]) != 2 or len(lesson["learningTools"]) > 3:
    ERR.append("lesson: codeWalkthrough 5-7, tryIt 2, learningTools <= 3")
for s in lesson["steps"]:
    if not s.get("mac") or not s.get("windows"):
        ERR.append(f"step {s['title']}: needs mac + windows")
KB = INT.parent
for b in lesson["buildsOn"]:  # exact titles of the reused lessons
    lv = next(l for f in ("L100", "L200", "L300", "L400") for l in json.loads((KB / b["topic"] / "content" / f"{f}.json")
              .read_text(encoding="utf-8")) if l["number"] == b["lesson"])
    expect(f"buildsOn {b['topic']} #{b['lesson']} title", b["title"], lv["title"])
for path in [s["test"] for s in lesson["seams"]] + [m["test"].split("::")[0] for m in lesson["milestones"]] + \
        lesson["decisionRecords"] + [lesson["architecture"]["diagram"], lesson["buildTask"]["solution"]]:
    if not (INT / path).exists():
        ERR.append(f"missing file {path}")
words = len(note.split())
if not 800 <= words <= 1000:
    ERR.append(f"concept note {words} words (want 800-1000)")

# --- the seeded world: every scorecard number
w = World()
res = {cid: fn(w) for _, cid, _, fn in checks.CHECKS}
for cid, (ok, _) in res.items():
    expect(f"{cid} pass", ok, True)
d = {cid: det for cid, (_, det) in res.items()}
expect("rows", d["M1"]["rows"], 28)
expect("needs_prior", d["M1"]["needs_prior"], 10)
expect("first", d["M1"]["first"], "4000000 270.70193010476163 pc")
expect("merkle root", d["M2"]["merkle_root"], "3b45768398c20ed6")
expect("licence", d["M2"]["licence"], "CC-BY-NC-4.0")
expect("sig bytes", d["M3"]["sig_bytes"], [64, 3309])
expect("rounds", d["M4"]["rounds"], {1: 2, 2: 2, 3: 2, 4: 4})
expect("jcs bytes", (d["S1"]["jcs_bytes"], d["S1"]["platform_bytes"]), (6536, 7901))
expect("old releases", d["S2"]["old_releases_verify"], [1, 2, 3, 4])
expect("lagging", d["S3"]["lagging"], "m3-lagging: offers v3, client has seen v4 (rollback)")
expect("frozen", d["S3"]["frozen"], "m3-lagging: timestamp expired at 6000 (freeze attack or stale mirror)")
expect("F1", (d["F1"]["caught"], d["F1"]["total"]), (15586, 15586))
expect("F2", (d["F2"]["all_up"], d["F2"]["all_up_mean"], d["F2"]["m3_down_3"]), (3, 2.04, 1))
expect("F3", d["F3"]["older_versions_rejected"], [1, 2, 3])
expect("F1 total = bytes of v4 objects", sum(len(v) for k, v in w.objects.items()), 15586)
expect("growth %", round((7901 - 6536) / 6536 * 100, 1), 20.9)

# --- faults
ff = World("float-format")
ok4, d4 = checks.m4_replicated(ff)
ok5, d5 = checks.m5_client(ff)
expect("ff M4", (ok4, d4["rounds"]), (False, {1: None, 2: None, 3: None, 4: None}))
expect("ff M5", (ok5, d5["verified_from"], d5["rejected"]), (False, ["m0", "m1", "m3"], {"m2": "v4: catalogue.json missing or changed"}))
sys.path.insert(0, str(LAB))
import run_project  # noqa: E402
expect("ff diagnose", run_project.diagnose(ff), {"m0": "\"dec\":-3.94153,\"distance_pc\":270.7",
                                                 "m2": "\"dec\":-3.9415300000000002,\"distanc", "offset": 168})
expect("ff passed", sum(fn(ff)[0] for _, _, _, fn in checks.CHECKS), 9)
expect("drop-old-key S2", checks.s2_rotation(World("drop-old-key"))[1]["old_releases_verify"], [4])
nf = World("no-freshness")
expect("no-freshness S3", (checks.s3_freshness(nf)[1]["lagging"], checks.f3_rollback(nf)[1]["older_versions_rejected"]), ("ACCEPTED", []))
expect("licence-drop S4", checks.s4_licence(World("licence-drop"))[1]["gate"],
       "licence CC-BY-4.0 drops the NC condition of input gaia_dr3_astrometry (LicenseRef-CC-BY-NC-3.0-IGO)")

# --- tryIt lines, exactly as the lesson quotes them
for i, script in enumerate(("try_1_python_json.py", "try_2_short_ttl.py")):
    out = subprocess.run([sys.executable, str(LAB / "try_it" / script)], capture_output=True, text=True,
                         encoding="utf-8", cwd=str(LAB), check=True).stdout.strip().splitlines()
    expect(f"tryIt {i + 1}", " | ".join(out), lesson["tryIt"][i]["expected"])

# --- concept-note / lesson numbers that are not scorecard fields
for snippet in ("270.70193010476163", "6,536", "7,901", "15,586", "3,309", "-3.9415300000000002", "timestamp expired at 3720"):
    if snippet not in text:
        ERR.append(f"text does not mention {snippet}")
expect("1/parallax", 1 / (3.6941 / 1000), 270.70193010476163)
expect("CyberChef JCS", hashlib.sha256(b'{"a":[1e-7,0.000025],"b":5}').hexdigest(),
       "b599ec35493709057db5e098bad6c959297a94fdb7e36d7e0d99dce4593b9f7c")
expect("CyberChef json.dumps", hashlib.sha256(b'{"a":[1e-07,2.5e-05],"b":5.0}').hexdigest(),
       "66f1ed9f286f835e9307d6e69cf01f2f69b8dd1fef7bbf181227aafb10fa4160")

# --- qbank: schema, mix, balance, calculations, code snippets
CALC = {
    "sig_bytes": lambda: f"{64 + 3309:,} B",
    "distance": lambda: (lambda dd: f"{dd:.2f} pc and M = {8.445 - 5 * math.log10(dd / 10):.2f}")(1 / 0.0036941),
    "snr": lambda: ("Distance null, method needs-prior: the fractional error is 25 %, above the 20 % limit"
                    if 1.2 / 0.3 < science.MIN_PARALLAX_SNR and round(0.3 / 1.2 * 100) == 25 else "?"),
    "growth": lambda: f"{(7901 - 6536) / 6536 * 100:.1f} %",
    "incl5": lambda: str(len(merkle.inclusion_proof(4, [bytes([i]) for i in range(5)]))),
    "ttl": lambda: f"More than {900 + 3 * 60 + 60:,} s",
    "log_proof": lambda: f"{math.ceil(math.log2(1_000_000))} hashes, {32 * math.ceil(math.log2(1_000_000))} bytes",
}
types, tags, pos = collections.Counter(), collections.Counter(), collections.Counter()
seen = set()
for q in qbank:
    qid = q["id"]
    for k in ("id", "level", "lesson", "type", "difficulty", "question", "options", "answer", "explanation", "source"):
        if k not in q:
            ERR.append(f"{qid}: missing {k}")
    expect(f"{qid} level/lesson", (q["level"], q["lesson"]), ("L600", 6))
    if len(q["options"]) != 4 or len(set(q["options"])) != 4 or not 0 <= q["answer"] <= 3:
        ERR.append(f"{qid}: needs 4 distinct options and answer 0-3")
    if re.search(r"\b(all|none) of the (above|options)\b", " ".join(q["options"]), re.I) or len(q["explanation"]) < 30:
        ERR.append(f"{qid}: banned option or short explanation")
    key = re.sub(r"\W+", " ", (q["question"] + q.get("code", "")).lower())
    if key in seen:
        ERR.append(f"{qid}: duplicate")
    seen.add(key)
    types[q["type"]] += 1
    pos[q["answer"]] += 1
    tags.update(q.get("tags", []))
    correct = q["options"][q["answer"]]
    if q["type"] == "calculation":
        expect(f"{qid} calc", correct, CALC[q["check"]]())
    if q["type"] == "code-reading":
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exec(q["code"], {"__name__": "__qbank__"})
        expect(f"{qid} code output", buf.getvalue().strip(), correct)
n = len(qbank)
if n < 30:
    ERR.append(f"qbank: {n} questions (< 30)")
for t, need in (("seam", 6), ("calc", 5), ("diagnose", 5), ("code", 4)):
    if tags[t] < need:
        ERR.append(f"qbank: {tags[t]} '{t}' questions (< {need})")
expect("calc type count", types["calculation"] >= 5 and types["debugging"] >= 5 and types["code-reading"] >= 4, True)
for a in range(4):
    if not 0.2 <= pos[a] / n <= 0.3:
        ERR.append(f"qbank: answer {'ABCD'[a]} correct in {pos[a] / n:.0%}")
longest = sum(max(range(4), key=lambda i: len(q["options"][i])) == q["answer"] for q in qbank)
if longest / n > 0.45:
    ERR.append(f"qbank: correct option is the longest in {longest}/{n}")

if ERR:
    print("\n".join("FAIL " + e for e in ERR))
    sys.exit(1)
print(f"OK - lesson, concept note ({words} words), {n} questions ({dict(types)}; answers {dict(sorted(pos.items()))}), "
      f"scorecard 12/12, faults reproduced, tryIt lines match")
