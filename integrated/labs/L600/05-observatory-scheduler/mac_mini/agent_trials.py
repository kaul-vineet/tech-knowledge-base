"""Experiment 1: real local models propose tonight's plan and explain it; validator.py and agent_plan decide.

Per model (one JSON line): the plan text's PLAN lines, parse problems (times without a zone are refused, never
guessed), validator violations by kind (airmass, darkness, Moon, overlap, grid, unknown target, twice), whether the
plan was adopted (only if valid AND its expected value >= the optimiser's), and whether the explanation was published
(every number must be one of the facts, every star name a requested target).

python agent_trials.py --here                    the fake model (deterministic, runs anywhere)
python agent_trials.py --auto                    models sized by mac_profile.py (Ollama must run on this Mac)
python agent_trials.py --models qwen2.5:7b,qwen2.5:14b
"""
import argparse
import json
import os
import re
import sys
import urllib.error

import _lab
import _kb
import agent_plan

KINDS = {"zone": "ISO 8601", "airmass": "airmass", "darkness": "outside darkness", "moon": "from the Moon",
         "overlap": "overlap", "grid": "slot grid", "unknown": "not a requested target", "twice": "scheduled twice",
         "no_plan": "no PLAN lines", "sun": "Sun above"}


def classify(reasons):
    out = {k: sum(v in x for x in reasons) for k, v in KINDS.items()}
    out["other"] = len(reasons) - sum(out.values())
    return {k: v for k, v in out.items() if v}


def trial(url, model, r):
    reqs, slots = r["reqs"], r["slots"]
    chat = lambda prompt: _kb.agent_client.chat([{"role": "user", "content": prompt}], base_url=url, model=model,
                                                timeout=180)
    try:
        plan_text = chat(agent_plan.plan_prompt(reqs, slots))
        facts = agent_plan.explain_facts(r)
        expl = chat(agent_plan.explain_prompt(facts))
    except (urllib.error.URLError, OSError, KeyError, ValueError) as exc:
        return {"model": model, "error": f"{type(exc).__name__}: {exc}"[:300]}
    verdict = agent_plan.decide(plan_text, r["local"], reqs, slots)
    shown, _ = agent_plan.checked_explanation(expl, facts, reqs)
    allowed = {float(n) for v in facts.values() for n in agent_plan.NUM.findall(v)}
    invented = sorted({n for n in agent_plan.NUM.findall(expl) if float(n) not in allowed})
    return {"model": model, "plan_lines": len(re.findall(r"^PLAN\s", plan_text, re.M)),
            "adopted": verdict["adopted"], "agent_ok": verdict["agent_ok"], "agent_value": verdict.get("agent_value"),
            "optimiser_value": round(r["local_value"], 3), "violations": len(verdict["reasons"]),
            "violation_kinds": classify(verdict["reasons"]), "first_reasons": verdict["reasons"][:4],
            "explanation_published": shown, "invented_numbers": invented[:10], "explanation_chars": len(expl)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--here", action="store_true")
    g.add_argument("--auto", action="store_true")
    g.add_argument("--models")
    ap.add_argument("--ram", type=float)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    r, server = _lab.build(), None
    if a.here:
        server, url = _kb.fake_model_server.start_in_thread()
        models = ["fake-model"]
    else:
        url = os.environ.get("LOCAL_MODEL_URL", "http://localhost:11434/v1")
        if a.auto:
            import mac_profile
            models = mac_profile.profile(a.ram)["compare_models"]
        else:
            models = [m.strip() for m in a.models.split(",") if m.strip()]
    rows = []
    try:
        for m in models:
            rows.append(trial(url, m, r))
            print(json.dumps(rows[-1]))
    finally:
        if server:
            server.shutdown()
            server.server_close()
    path = _lab.write_jsonl(_lab.runs_dir(a.out) / "05-agent-trials.jsonl", rows)
    print(f"wrote {path}")
    # The decision rule must hold for any model: an adopted plan is valid and at least as good as the optimiser's.
    bad = [x["model"] for x in rows if x.get("adopted") == "agent" and (not x["agent_ok"] or
                                                                       x["agent_value"] < x["optimiser_value"] - 1e-3)]
    return 1 if bad or all("error" in x for x in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
