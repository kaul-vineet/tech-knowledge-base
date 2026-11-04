"""Capstone: classroom environmental monitor network - run it end to end and print a scorecard.

Deterministic core decides (firmware + gateway rules, verifier, twin's CUSUM, fleet registry);
the local model only explains, and code checks what it says. Prints JSON lines, one per rubric
criterion, then {"scorecard": "PASS"|"FAIL", ...}. Seeded (22); simulated time; stub boards only.
Run:  python run_capstone.py            (Windows: py run_capstone.py)   ~1 minute
"""
import json
import statistics
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_firmware  # noqa: E402
import pipeline  # noqa: E402
from simnet import percentile, reuse  # noqa: E402
from store import to_csv, to_prometheus  # noqa: E402

fleet_sim = reuse("L400/18-fleet-config/fleet_sim.py", "l400_fleet_sim")
assistant = reuse("L400/21-edge-ai-explain/solution.py", "l400_assistant")
sys.path[:] = [p for p in sys.path if not any(k in p for k in ("18-fleet", "20-digital", "21-edge-ai"))]
twin_cls = reuse("L400/20-digital-twin/solution.py", "l400_twin").Twin
rules = assistant.rules
from labtest import load_lab  # noqa: E402
firmware = load_lab(str(HERE.parent / "21-edge-ai-explain"), "firmware_alarm.py")
LABELS = dict(assistant.incident.LABELS)                  # fleet registry labels; n4's carries an injection


def m1_m2_network(seed):
    res, gw, eve = pipeline.run_network(build_firmware.build(), seed=seed)
    lat = [r["t_store"] - r["t_sensor"] for r in gw.rows]
    return gw, {"sampled": res["sampled"], "stored": len(gw.rows), "p95_ms": percentile(lat, 95),
                "forged_stored": sum(r["temp"] == 45 for r in gw.rows), "replays_stored": gw.store.duplicates,
                "rejects": dict((k, sum(k in line for line in gw.verifier.log)) for k in ("mac", "replay")),
                "eve": eve.sent}


def m3_fleet(seed):
    m, _ = fleet_sim.run("solution.py", "staged", seed=seed)
    return {"unacked_ticks": m["unacked_ticks"], "max_on_bad": m["max_on_bad"],
            "final": "".join(str(v) for v in m["final"].values())}


def m4_twin(gw):
    by = {}
    for r in sorted(gw.rows, key=lambda r: (r["dev"], r["seq"])):
        by.setdefault(r["dev"], []).append(r)
    twin = twin_cls(pipeline.twin_model.calibrate(by))
    wins = dict((d, pipeline.twin_model.windows(rows)) for d, rows in by.items())
    found = {}
    for i in range(pipeline.twin_model.CALIB_WINDOWS, max(len(w) for w in wins.values())):
        for dev in sorted(wins):
            if i < len(wins[dev]):
                for a in twin.update(dev, pipeline.twin_model.observe(wins[dev][i])):
                    found["%s %s" % (a["dev"], a["alarm"])] = i
    return twin, found


def m5_alarms_and_agent(gw, twin, auth):
    by = {}
    for r in sorted(gw.rows, key=lambda r: (r["dev"], r["seq"])):
        by.setdefault(r["dev"], []).append(r)
    snap = {"devices": [{"dev": d, "label": LABELS[d], "temps": [r["temp"] for r in rows[-3:]], "readings": len(rows)}
                        for d, rows in sorted(by.items())],
            "twin_alarms": [{"dev": a["dev"], "alarm": a["alarm"], "z": a["z"]} for a in twin.alarms], "auth": auth}
    hot_fw, fw = False, {}
    for d in snap["devices"]:
        for t in by[d["dev"]][-60:]:
            hot_fw = firmware.check(fw.get(d["dev"], False), t["temp"])
            fw[d["dev"]] = hot_fw
    from local_agent import fake_model_server
    from local_agent.client import chat
    server, url = fake_model_server.start_in_thread()
    try:
        out = assistant.run(lambda m: chat(m, base_url=url, model="fake-model", timeout=60), snap)
    finally:
        server.shutdown()
        server.server_close()
    return snap, out, fw


def m6_dashboard(gw, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_text, prom = to_csv(gw.store.rows()), to_prometheus(gw.store.summary())
    (out_dir / "dashboard.csv").write_text(csv_text, encoding="utf-8")     # Superset: Upload CSV
    (out_dir / "metrics.txt").write_text(prom, encoding="utf-8")         # Prometheus text format (text/plain)
    prom_total = sum(int(line.split()[-1]) for line in prom.splitlines() if line.startswith("classroom_readings_total{"))
    return {"csv_rows": len(csv_text.splitlines()) - 1, "prom_total": prom_total}


def scorecard(seed=pipeline.SEED, out_dir=None):
    gw, net = m1_m2_network(seed)
    fleet = m3_fleet(seed)
    twin, drift = m4_twin(gw)
    snap, agent, fw = m5_alarms_and_agent(gw, twin, net["rejects"])
    with tempfile.TemporaryDirectory(dir=HERE) as tmp:      # exports go to out_dir, or to a private folder
        dash = m6_dashboard(gw, Path(out_dir or tmp))
    code = rules.decide(snap)
    rows = [
        ("M1", "delivery", round(100.0 * net["stored"] / net["sampled"], 2), ">= 99.0 %", net["stored"] >= 0.99 * net["sampled"]),
        ("M1", "p95 latency ms", net["p95_ms"], "<= 2000", net["p95_ms"] <= 2000),
        ("M2", "forged/replayed readings stored", [net["forged_stored"], net["replays_stored"]], "[0, 0]",
         net["forged_stored"] == 0 and net["replays_stored"] == 0),
        ("M2", "attacks seen and rejected", net["rejects"], "mac >= 1 and replay >= 1", min(net["rejects"].values()) >= 1),
        ("M3", "unacked config ticks / canary blast radius", [fleet["unacked_ticks"], fleet["max_on_bad"]], "[0, <= 1]",
         fleet["unacked_ticks"] == 0 and fleet["max_on_bad"] <= 1 and fleet["final"] == "222222"),
        ("M4", "n5 link drift found (window)", drift.get("n5 DRIFT_LAT"), "<= 19 (drift from window 10)",
         drift.get("n5 DRIFT_LAT") is not None and drift["n5 DRIFT_LAT"] <= 19),
        ("M4", "other drift alarms", sorted(k for k in drift if k not in ("n5 DRIFT_LAT", "n4 DRIFT_TEMP")), "<= 1 entry",
         len([k for k in drift if k not in ("n5 DRIFT_LAT", "n4 DRIFT_TEMP")]) <= 1),
        ("M5", "TEMP_HIGH n4 by gateway and firmware", [any(a["name"] == "TEMP_HIGH" and a["dev"] == "n4" for a in code), fw.get("n4")],
         "[true, true]", any(a["name"] == "TEMP_HIGH" and a["dev"] == "n4" for a in code) and fw.get("n4") is True),
        ("M5", "model cannot change alarms", agent["digest"] == rules.freeze(code)[1] and not agent["accepted"],
         "digest equal; injected reply rejected", agent["digest"] == rules.freeze(code)[1] and not agent["accepted"]),
        ("M6", "dashboard exports match the store", [dash["csv_rows"], dash["prom_total"], net["stored"]], "all equal",
         dash["csv_rows"] == dash["prom_total"] == net["stored"]),
    ]
    lines = [json.dumps({"milestone": m, "criterion": c, "value": v, "threshold": t, "pass": bool(p)}) for m, c, v, t, p in rows]
    passed = sum(bool(r[4]) for r in rows)
    lines.append(json.dumps({"scorecard": "PASS" if passed == len(rows) else "FAIL", "passed": passed, "total": len(rows),
                             "operator_note": agent["note"][:120] + "..."}))
    return lines, {"net": net, "fleet": fleet, "drift": drift, "agent": agent, "dash": dash,
                   "mean_temp": round(statistics.fmean(r["temp"] for r in gw.rows), 2)}


if __name__ == "__main__":
    for line in scorecard(out_dir=HERE / "out")[0]:
        print(line)
