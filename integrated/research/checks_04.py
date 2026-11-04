"""Recompute every number in L600 #04 (lesson, concept note, ADRs, README) and its question bank; print OK.

Run from kb/:  python integrated/research/checks_04.py      (Windows: py integrated\\research\\checks_04.py)
Runs the lab's scripts as subprocesses (in parallel; simulated time, seeded), recomputes the calculations,
executes every code-reading snippet, and validates the JSON parts. Exit 0 only if everything matches.
"""
import collections
import contextlib
import datetime
import io
import json
import math
import subprocess
import sys
from pathlib import Path

INT = Path(__file__).resolve().parents[1]
LAB = INT / "labs" / "L600" / "04-microbit-sensor-fleet"
sys.path.insert(0, str(LAB))
import _kb  # noqa: E402
import fleet_sim  # noqa: E402
import gateway  # noqa: E402

FAIL = []


def expect(name, got, want):
    if got != want:
        FAIL.append("%s: got %r, want %r" % (name, got, want))


EXTRA = r"""
import json, fleet_sim, api
r = fleet_sim.run()
b1 = r["stores"]["b1"]
nosel = fleet_sim.run(selective_ack=False)
d07 = api.latest(b1, "d07", 2)[0]
print(json.dumps({"p95": r["p95_to_gateway_s"], "d07": [d07["boot"], d07["seq"]], "frames_nosel": nosel["frames"],
                  "air_lost_positive": r["air"]["lost"] > 0, "conv": fleet_sim.convergence_experiment(),
                  "f1_seeds": [fleet_sim.run(seed=s)["lost"] for s in (5, 6)]}))
"""


def launch():
    """try_it + extra run in parallel; the run_project.py jobs run one after another (they rewrite contracts/)."""
    parallel = {"try1": ["try_it/sync_interval.py"], "try2": ["try_it/partition_capacity.py"], "extra": ["-c", EXTRA]}
    procs = {k: subprocess.Popen([sys.executable] + v, cwd=LAB, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 encoding="utf-8") for k, v in parallel.items()}
    parse = lambda text: [json.loads(line) for line in text.splitlines() if line.startswith("{")]  # noqa: E731
    out = {}
    for k, args in [("base", [])] + [(f, ["--inject", f]) for f in fleet_sim.INJECTS]:
        p = subprocess.run([sys.executable, "run_project.py"] + args, cwd=LAB, capture_output=True, encoding="utf-8")
        out[k] = (p.returncode, parse(p.stdout), p.stderr)
    for k, p in procs.items():
        stdout, stderr = p.communicate()
        out[k] = (p.returncode, parse(stdout), stderr)
    return out


def card(lines):
    return {row["check"].split()[0]: row for row in lines if "check" in row}, lines[-1]


def calc_values():
    fig = _kb.budget().FIGURES
    epoch = int(datetime.datetime(2027, 1, 1, tzinfo=datetime.timezone.utc).timestamp())
    ack = gateway.encode_ack(1, fleet_sim.EPOCH0, [(1, 5)], [(1, 7), (1, 9)])
    return {
        "rpf_32_v2": str((32 - 3) // 9),
        "rpf_251_v1": str((251 - 3) // 8),
        "full_state_frames": "%d frames" % math.ceil(720 * 9 / 29),
        "life_sample_only": "{:,.1f} h".format(fleet_sim.life_hours(60 * fig["ACTIVE_MS"], 3600000, fig)[0]),
        "life_10s_sync": "{:,.1f} h".format(fleet_sim.life_hours(1200 + 360 * 170, 3600000, fig)[0]),
        "flash_hours": "%.1f h" % (400 / 60),
        "deprecation": "@%d" % epoch,
        "ack_len": "%d bytes" % len(ack),
    }


def check_qbank(calcs):
    qs = json.loads((INT / "content" / "qbank" / "parts" / "04.json").read_text(encoding="utf-8"))
    expect("qbank size >= 30", len(qs) >= 30, True)
    types, pos, tags = collections.Counter(), collections.Counter(), collections.Counter()
    for q in qs:
        for k in ("id", "level", "lesson", "type", "difficulty", "question", "options", "answer", "explanation", "source"):
            if k not in q:
                FAIL.append("%s missing %s" % (q.get("id"), k))
        expect(q["id"] + " level/lesson", (q["level"], q["lesson"]), ("L600", 4))
        expect(q["id"] + " 4 distinct options", len(set(q["options"])), 4)
        if any(w in " ".join(q["options"]).lower() for w in ("all of the above", "none of the above")):
            FAIL.append(q["id"] + " all/none of the above")
        types[q["type"]] += 1
        pos[q["answer"]] += 1
        tags.update(q.get("tags", []))
        if q.get("check") == "code":
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                exec(compile(q["code"], q["id"], "exec"), {})
            expect(q["id"] + " snippet output", q["options"][q["answer"]], buf.getvalue().strip())
        elif q.get("check"):
            expect(q["id"] + " " + q["check"], q["options"][q["answer"]], calcs[q["check"]])
    for a in range(4):
        share = pos[a] / len(qs)
        if not 0.20 <= share <= 0.30:
            FAIL.append("answer %s share %.0f%%" % ("ABCD"[a], 100 * share))
    expect("seam questions >= 6", tags["seam"] >= 6, True)
    expect("calculation >= 5", types["calculation"] >= 5, True)
    expect("diagnose >= 5", tags["diagnose"] >= 5, True)
    expect("code-reading >= 4", types["code-reading"] >= 4, True)
    return len(qs), dict(types), dict(sorted(pos.items()))


def check_lesson(base_summary):
    lesson = json.loads((INT / "content" / "parts" / "04.json").read_text(encoding="utf-8"))
    expect("code == run_project.py", lesson["code"], (LAB / "run_project.py").read_text(encoding="utf-8"))
    for k in ("combines", "buildsOn", "seams", "failureLab", "buildTask", "scalingLimits", "milestones", "rubric",
              "fitnessFunctions", "decisionRecords", "designBrief", "architecture", "validation", "tryIt"):
        if not lesson.get(k):
            FAIL.append("lesson missing " + k)
    expect("buildsOn 4-8", 4 <= len(lesson["buildsOn"]) <= 8, True)
    expect("seams 3-5", 3 <= len(lesson["seams"]) <= 5, True)
    expect("milestones 4-6", 4 <= len(lesson["milestones"]) <= 6, True)
    expect("walkthrough 5-7", 5 <= len(lesson["codeWalkthrough"]) <= 7, True)
    expect("learningTools <= 3", len(lesson["learningTools"]) <= 3, True)
    expect("run_project.py <= ~150 lines", len(lesson["code"].splitlines()) <= 150, True)
    titles = {}
    for topic in lesson["combines"]:
        for level in ("L100", "L200", "L300", "L400"):
            for item in json.loads((INT.parent / topic / "content" / ("%s.json" % level)).read_text(encoding="utf-8")):
                titles[(topic, item["number"])] = item["title"]
    for b in lesson["buildsOn"]:
        expect("buildsOn title %s #%d" % (b["topic"], b["lesson"]), titles.get((b["topic"], b["lesson"])), b["title"])
    paths = [lesson["architecture"]["diagram"], lesson["buildTask"]["solution"]] + lesson["decisionRecords"] + \
        [s["test"].split("::")[0] for s in lesson["seams"]] + [p["path"] for p in lesson["projectFiles"]]
    for p in paths:
        if not (INT / p).exists():
            FAIL.append("missing file " + p)
    expect("steps expected summary", lesson["steps"][1]["expected"].startswith(json.dumps(base_summary)), True)
    words = len((INT / lesson["conceptNote"]).read_text(encoding="utf-8").split())
    expect("concept note 800-1000 words", 800 <= words <= 1000, True)
    return words


def main():
    calcs = calc_values()
    expect("ack hex in learningTools", gateway.encode_ack(1, fleet_sim.EPOCH0, [(1, 5)]).hex(" "),
           "02 41 01 6a b1 3b 80 01 01 00 05")
    expect("records per 251-byte frame, schema 2", (251 - 3) // 9, 27)
    expect("frame sizes 1-3 records", [3 + 9 * n for n in (1, 2, 3)], [12, 21, 30])
    expect("full log bytes", 720 * 9, 6480)
    expect("records per sync", 3 * 8 * 3, 72)
    out = launch()
    rc, lines, err = out["base"]
    expect("base exit", rc, 0)
    c, summary = card(lines)
    expect("base summary", (summary["scorecard"], summary["passed"], summary["total"]), ("PASS", 12, 12))
    expect("M1", c["M1"]["value"], {"sampled": 14400, "dropped": 0, "peak_log": 190})
    expect("M2", c["M2"]["value"], {"reached_gateway": 14400, "tries": 2835, "frames": 9752, "logs_empty": True})
    expect("M3", c["M3"]["value"], {"laws": "300/300", "replicas_equal": True, "wrong_values": 0})
    expect("M4", c["M4"]["value"], {"contract_problems": 0, "v1_deprecation": "@1798761600", "api_rows": 14400})
    expect("S1", (c["S1"]["value"]["max_frame_bytes"], c["S1"]["value"]["full_state_frames_per_device"]), (30, 224))
    expect("S2", c["S2"]["value"], {"wall_key_repeats": 1421, "lost": 0})
    expect("S3/F3 life", c["F3"]["value"], {"sync_every_min": 10, "life_h_min": 2419.7})
    expect("S4", c["S4"]["value"], {"schema1_rows": 2880, "rec_len_equal": True})
    expect("F2", c["F2"]["value"], {"end_of_run": 1, "experiment_max": 3, "experiment_mean": 2.27})
    expected_inject = {"wallclock-lww": (9, {"S2": {"wall_key_repeats": 1421, "lost": 1421}}),
                       "oversize-frame": (4, {}), "schema-drift": (5, {})}
    for f, (passed, rows) in expected_inject.items():
        rc, lines, err = out[f]
        c2, s2 = card(lines)
        expect(f + " exit", rc, 1)
        expect(f + " passed", (s2["scorecard"], s2["passed"]), ("FAIL", passed))
        for key, val in rows.items():
            expect(f + " " + key, c2[key]["value"], val)
        if f == "wallclock-lww":
            expect("lww M4 still passes", c2["M4"]["pass"], True)
            expect("lww S4 rows", c2["S4"]["value"]["schema1_rows"], 2670)
        if f == "oversize-frame":
            expect("oversize lost", c2["F1"]["value"]["lost"], 14082)
            expect("oversize max frame", c2["S1"]["value"]["max_frame_bytes"], 32)
        if f == "schema-drift":
            expect("drift lost", c2["F1"]["value"]["lost"], 2880)
            expect("drift contract problems", c2["M4"]["value"]["contract_problems"], 7)
    rc, lines, err = out["try1"]
    expect("try1", [(x["sync_every_min"], x["life_h_min"], x["tries"], x["frames"], x["p95_to_gateway_s"], x["lost"],
                     x["peak_log"]) for x in lines],
           [(1, 2212.4, 21816, 39841, 2280, 0, 181), (10, 2419.7, 2835, 9752, 4020, 0, 190),
            (60, 2445.1, 871, 6750, 14940, 0, 305)])
    rc, lines, err = out["try2"]
    expect("try2", [(x["partition_h"], x["selective_ack"], x["peak_log"], x["dropped_flash_full"], x["lost"],
                     x["logs_empty"]) for x in lines],
           [(3.0, True, 190, 0, 0, True), (8.0, True, 400, 451, 450, True), (8.0, False, 400, 1039, 2330, False)])
    rc, lines, err = out["extra"]
    if rc or not lines:
        FAIL.append("extra script failed: " + err[-500:])
    else:
        x = lines[0]
        expect("extra", (x["p95"], x["d07"], x["frames_nosel"], x["air_lost_positive"], x["conv"]["max"],
                         x["conv"]["mean"], x["f1_seeds"]), (4020, [2, 420], 13177, True, 3, 2.27, [0, 0]))
    n, types, pos = check_qbank(calcs)
    words = check_lesson(summary)
    if FAIL:
        print("FAIL")
        for f in FAIL:
            print("  " + f)
        return 1
    print("OK  qbank %d questions %s answers %s; concept note %d words; 7 scripts re-run" % (n, types, pos, words))
    return 0


if __name__ == "__main__":
    sys.exit(main())
