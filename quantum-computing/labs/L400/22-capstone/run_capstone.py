"""Capstone runner: drive the service end to end and print a scorecard as JSON lines.

Run: python run_capstone.py      (numpy + stdlib; the agent uses the deterministic fake model server)
Seeded faults: transient backend failures on job attempts 3 and 4, and the drifted CX edge (1, 2) on the device.
Every milestone and rubric line is decided by code; the agent's explanation is only checked, never trusted.
"""
import functools
import json
import urllib.error
import urllib.request

import agent_assist
import fake_explain_rule
import noisy_backend as nb
import pipeline
import service
from reuse import l18_bench

IGNORE = ("local_s",)


def call(url, path, body=None):
    req = urllib.request.Request(url + path, data=None if body is None else json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        with e:
            return e.code, json.loads(e.read())


def rows(report):
    return [{k: v for k, v in r.items() if k not in IGNORE} for r in report["benchmark"]]


@functools.lru_cache(maxsize=1)
def collect():
    server, url = service.start()
    try:
        out = {"health": call(url, "/health"), "default": call(url, "/solve", {}), "bad": call(url, "/solve", {"n": 30}),
               "large": call(url, "/solve", {"n": 12})}
    finally:
        server.shutdown()
    out["no_faults"] = pipeline.solve({"faults": []})
    out["white_noise"] = nb.white_noise_check()
    from local_agent import fake_model_server
    fake_explain_rule.register(fake_model_server)
    fake, fake_url = fake_model_server.start_in_thread()
    try:
        out["agent"] = agent_assist.run(out["default"][1], fake_url)
    finally:
        fake.shutdown()
    return out


def milestones(o):
    rep, large = o["default"][1], o["large"][1]
    ex, cp, mt = rep["execution"], rep["compile"], rep["mitigation"]
    return [
        ("M1 API and validation", o["health"][0] == 200 and o["default"][0] == 200 and o["bad"][0] == 400 and o["large"][0] == 200,
         {"health": o["health"][0], "solve": o["default"][0], "bad_request": o["bad"][0], "bad_reason": o["bad"][1]["error"]}),
        ("M2 orchestrated quantum path (batched, cached, retried)",
         ex["mode"] == "batched" and ex["transpiles"] == 1 and ex["jobs"] <= 10 and ex["retries"] == 2 and rows(rep) == rows(o["no_faults"]), ex),
        ("M3 compile + noise model", cp["within_depth_budget"] and o["white_noise"]["tvd_model"] <= 0.03 < o["white_noise"]["tvd_ideal"],
         {**{k: cp[k] for k in ("esp", "cx", "depth", "gate_fidelity")}, **o["white_noise"]}),
        ("M4 readout mitigation", abs(mt["mitigated"] - mt["gate_noise_only"]) < abs(mt["raw"] - mt["gate_noise_only"]), mt),
        ("M5 fair benchmark + code decides", len({r["budget"] for r in rep["benchmark"]}) == 1
         and {r["runs"] for r in rep["benchmark"]} == {rep["request"]["seeds"]} and rep["winner"] == l18_bench.decide(rep["benchmark"])
         and not large["feasibility"]["quantum_path"], {"winner": rep["winner"], "n12_winner": large["winner"],
                                                         "n12_reason": large["feasibility"]["reason"]}),
        ("M6 agent explains, code checks", [o["agent"][k][0] for k in ("explain", "pitch", "brief")] == ["ACCEPT", "REJECT", "REJECT"],
         {k: (v[0], v[1]) for k, v in o["agent"].items()}),
    ]


def rubric(o):
    rep = o["default"][1]
    best = next(r for r in rep["benchmark"] if r["solver"] == rep["winner"])
    return [
        ("correctness", f"winner median ratio {best['median_ratio']}", best["median_ratio"] >= 0.95),
        ("fairness", "one budget and one seed list for every solver", len({(r["budget"], r["runs"]) for r in rep["benchmark"]}) == 1),
        ("reliability", "2 injected job failures retried; results identical to a fault-free run", rows(rep) == rows(o["no_faults"])),
        ("cost", f"modelled wall {rep['execution']['wall_s']} s, {rep['execution']['jobs']} jobs (budget 60 s)", rep["execution"]["wall_s"] <= 60),
        ("honesty", "n = 12 refused for the 8-qubit device; classical answer returned", not o["large"][1]["feasibility"]["quantum_path"]),
        ("safety", "agent cannot change the winner; server binds 127.0.0.1", o["agent"]["pitch"][0] == "REJECT"),
    ]


if __name__ == "__main__":
    o = collect()
    ms = milestones(o)
    for name, ok, measure in ms:
        print(json.dumps({"milestone": name, "pass": bool(ok), "measure": measure}))
    rb = rubric(o)
    for criterion, measure, ok in rb:
        print(json.dumps({"rubric": criterion, "measure": measure, "pass": bool(ok)}))
    print(json.dumps({"scorecard": f"{sum(bool(m[1]) for m in ms)}/{len(ms)} milestones, {sum(bool(r[2]) for r in rb)}/{len(rb)} rubric",
                      "winner": o["default"][1]["winner"], "decided_by": "code"}))
