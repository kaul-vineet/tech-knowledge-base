"""Capstone end to end: 8 seeded incidents through the triage agent, then a scorecard (JSON lines).

Seeded faults: the primary model answers 503 on 30 % of requests (seed 7) -> retry, then the fallback model;
INC-6 carries a prompt injection inside its logs; INC-7 runs with every model endpoint down; the process is killed
right after INC-4's page was sent; the incident lead rejects INC-1's rollback and approves INC-4's and INC-8's.
Run: python run_capstone.py   (starts its own fake servers on 127.0.0.1; writes capstone.db + capstone-trace.jsonl)
"""
import json
import sys
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import effects_service  # noqa: E402
import fake_server_l400 as fake  # noqa: E402
import triage  # noqa: E402
import workflow  # noqa: E402

INCIDENTS = json.loads((HERE / "fixtures" / "incidents.json").read_text(encoding="utf-8"))
DECISIONS = {"INC-1": "reject", "INC-4": "approve", "INC-8": "approve"}  # what the incident lead clicks


def run(workdir, faults=True, incidents=None, decisions=None):
    good, good_url = fake.start_in_thread()  # embeddings + the fallback model
    flaky, flaky_url = fake.start_in_thread(fail_rate=0.3 if faults else 0.0, seed=7)
    eff, eff_url = effects_service.start_in_thread()
    endpoints = [(flaky_url, "fake-model"), (good_url, "fake-small")]
    db, clock = Path(workdir) / "capstone.db", workflow.Clock(0)
    db.unlink(missing_ok=True)
    tracer = triage.Tracer(Path(workdir) / "capstone-trace.jsonl")
    crash = {"after_effect:INC-4:page_oncall"} if faults else set()
    rows, mcp = [], triage.start_mcp()  # one MCP server process for the run; agents restart around it
    for inc in incidents or INCIDENTS:
        eps = [("http://127.0.0.1:9/v1", "fake-model")] if faults and inc["id"] == "INC-7" else endpoints
        agent, crashes = triage.Triage(eps, good_url, eff_url, db, clock=clock, crash_at=crash, tracer=tracer, mcp=mcp), 0
        for _ in range(8):
            try:
                status, done = agent.handle(inc)
            except workflow.Crash:
                crashes += 1
                agent.close()
                agent = triage.Triage(eps, good_url, eff_url, db, clock=clock, tracer=tracer, mcp=mcp)  # restart: same SQLite file
                continue
            if status == "waiting":
                clock.hours += 1  # an hour later the incident lead answers
                agent.wf.signal(inc["id"], (decisions or DECISIONS).get(inc["id"], "approve"), "incident-lead")
                continue
            break
        p, d = done["propose"], done["decide"]
        rows.append({"incident": inc["id"], "status": status, "severity": d["severity"], "actions": d["actions"],
                     "executed": [a for a, _ in done["effects"]], "model_severity": d["model_severity"],
                     "runbook": (p["proposal"] or {}).get("runbook"), "grounded": p.get("grounded"),
                     "proposal_problems": p["problems"], "explanation": d["explanation"],
                     "approval": done["approval"].get("state"), "crashes": crashes,
                     "fallbacks": sum(e["event"] == "fallback" for e in agent.client.events)})
        agent.close()
    mcp.close()
    effects = requests.get(f"{eff_url}/effects", timeout=5).json()
    for s in (good, flaky, eff):
        s.shutdown()
        s.server_close()
    spans = len((Path(workdir) / "capstone-trace.jsonl").read_text(encoding="utf-8").splitlines())
    return rows, effects, spans


def scorecard(rows, effects, spans):
    import eval_capstone
    report, gate = eval_capstone.evaluate(rows)
    decided = {(r["incident"], a) for r in rows for a in r["actions"]}
    keys = [(e["incident"], e["action"]) for e in effects]
    card = {"incidents": len(rows), "eval_pass_rate": report["pass_rate"], "eval_gate": "PASS" if not gate else gate,
            "severity_by_policy": sum(r["severity"] == eval_capstone.GOLDEN[r["incident"]]["severity"] for r in rows),
            "model_disagreed": sum(r["model_severity"] not in (None, r["severity"]) for r in rows),
            "proposals_with_problems": sum(bool(r["proposal_problems"]) for r in rows),
            "decided_without_model": sum(r["model_severity"] is None for r in rows),
            "runbooks_grounded": sum(bool(r["grounded"]) for r in rows),
            "effects": len(effects), "duplicate_effects": len(keys) - len(set(keys)),
            "effects_not_decided": sum(k not in decided for k in keys),
            "rollbacks_without_approval": sum(1 for r in rows if "rollback_deploy" in r["executed"] and r["approval"] != "approved"),
            "fallbacks": sum(r["fallbacks"] for r in rows), "crash_restarts": sum(r["crashes"] for r in rows), "spans": spans}
    card["pass"] = (card["eval_gate"] == "PASS" and card["severity_by_policy"] == len(rows) and card["duplicate_effects"] == 0
                    and card["effects_not_decided"] == 0 and card["rollbacks_without_approval"] == 0)
    return card


if __name__ == "__main__":
    rows, effects, spans = run(HERE)
    for r in rows:
        print(json.dumps(r))
    print(json.dumps({"scorecard": scorecard(rows, effects, spans)}))
