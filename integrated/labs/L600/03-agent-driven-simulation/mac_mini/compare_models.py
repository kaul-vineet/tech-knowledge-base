"""Experiment 1: the same brief, several real open-weight models - what do the gates catch per model?

For each model one agent session runs the project's BRIEF through the unchanged pipeline (contract gate, budget gate,
seeded registry, replications policy) and the claim checker. Recorded per model (JSON line):
  contract_rejected  proposals the contract refused before anything ran (schema or verified envelope rho <= 0.9)
  budget_rejected    proposals that passed the contract but did not fit the simulation budget
  claims_dropped     summary sentences the claim checker refused (uncited / untraced number, over-claim)
  budget_spent       simulated customers used of SIM_BUDGET; agent_calls / tokens of the agent budget
  stopped            final_answer | agent budget: ...   (a model that never stops hits MAX_CALLS)
  published_traced   numbers in the published text that trace to registry runs (must equal numbers_found)
  rejected_proposals the refused tool arguments + the contract's errors (input for export_rejections.py)

python compare_models.py --here                    fake model only (deterministic; runs anywhere)
python compare_models.py --auto                    models sized by mac_profile.py for this Mac (Ollama must run)
python compare_models.py --models qwen2.5:3b,qwen2.5:7b [--ram 16]
Model server: LOCAL_MODEL_URL (default http://localhost:11434/v1). The model only proposes; the gates decide.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error

import _lab
import agent
import claims
import pipeline
import registry as reg
import run_project

FIELDS = ("model", "contract_rejected", "budget_rejected", "claims_dropped", "budget_spent", "agent_calls", "stopped")


def slug(name):
    return re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-")


def run_one(url, model, out_dir):
    path = out_dir / f"03-registry-{slug(model)}.jsonl"
    path.unlink(missing_ok=True)
    registry = reg.Registry(path)
    pl = pipeline.Pipeline(registry, pipeline.SimBudget(run_project.SIM_BUDGET), half_width=run_project.HALF_WIDTH)
    t0 = time.perf_counter()
    try:
        out = agent.run_session(run_project.BRIEF, pl, url, model, max_calls=run_project.MAX_CALLS)
    except (urllib.error.URLError, OSError, KeyError, ValueError) as exc:  # server down, model missing, bad reply
        registry.close()
        return {"model": model, "error": f"{type(exc).__name__}: {exc}"[:300]}
    seconds = time.perf_counter() - t0
    rows, published = claims.review(out["summary"], registry)
    rejected = [j for j in pl.jobs if j["states"][-1] == "REJECTED"]
    by_contract = [j for j in rejected if "VALIDATED" not in j["states"]]
    found, traced = claims.traced_runs(published, registry)
    rec = {"model": model, "seconds": round(seconds, 1), "proposals": len(pl.jobs),
           "contract_rejected": len(by_contract), "budget_rejected": len(rejected) - len(by_contract),
           "claims_total": len(rows), "claims_dropped": sum(not r["ok"] for r in rows),
           "dropped_reasons": sorted({r["reason"] for r in rows if not r["ok"]}),
           "budget_spent": pl.budget.spent, "budget_limit": run_project.SIM_BUDGET,
           "agent_calls": out["calls"], "agent_call_limit": run_project.MAX_CALLS, "tokens": out["tokens"],
           "stopped": out["stopped"], "numbers_found": found, "published_traced": traced,
           "budget_respected": pl.budget.spent <= run_project.SIM_BUDGET,
           "unparseable_calls": sum(t["args"] is None for t in out["trace"]),
           "rejected_proposals": [{"tool": t["tool"], "args": t["args"], "errors": t["errors"]}
                                  for t in out["trace"] if t["status"] == "rejected"],
           "registry": path.name}
    registry.close()
    return rec


def models_from_profile(ram=None):
    import mac_profile
    return mac_profile.profile(ram)["compare_models"]


def table(rows):
    lines = ["  ".join(f"{f:<18}" for f in FIELDS)]
    for r in rows:
        lines.append("  ".join(f"{str(r.get(f, r.get('error', '-')))[:18]:<18}" for f in FIELDS))
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="compare real local models behind the same gates")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--here", action="store_true", help="fake model only (sandbox)")
    g.add_argument("--auto", action="store_true", help="models from mac_profile.py")
    g.add_argument("--models", help="comma-separated Ollama model names")
    ap.add_argument("--ram", type=float, help="with --auto: simulate this RAM (GB)")
    ap.add_argument("--out", help="output folder (default $KB_RUNS_DIR or ~/kb-runs)")
    a = ap.parse_args(argv)
    out_dir = _lab.runs_dir(a.out)
    rows, server = [], None
    if a.here:
        import fake_sim_agent
        server, url = fake_sim_agent.start_in_thread()
        models = ["fake-model"]
    else:
        url = os.environ.get("LOCAL_MODEL_URL", "http://localhost:11434/v1")
        models = models_from_profile(a.ram) if a.auto else [m.strip() for m in a.models.split(",") if m.strip()]
    try:
        for m in models:
            rows.append(run_one(url, m, out_dir))
            print(json.dumps({k: v for k, v in rows[-1].items() if k != "rejected_proposals"}))
    finally:
        if server:
            server.shutdown()
            server.server_close()
    path = _lab.write_jsonl(out_dir / "03-compare-models.jsonl", rows)
    print(table(rows))
    print(f"wrote {path}")
    # Code decides even here: a model may be wrong, but the gates must hold for every model.
    bad = [r["model"] for r in rows if "error" not in r and (not r["budget_respected"]
                                                             or r["published_traced"] != r["numbers_found"])]
    errs = [r["model"] for r in rows if "error" in r]
    if bad:
        print(f"GATE VIOLATION for {bad}")
    return 1 if bad or len(errs) == len(rows) else 0


if __name__ == "__main__":
    sys.exit(main())
