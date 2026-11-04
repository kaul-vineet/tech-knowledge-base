"""L600 #03: an AI agent that runs simulation experiments - and can't fool you.

The agent (a tool-calling loop) proposes screening runs and A/B experiments on the L200 #10 help-desk simulation and
writes a summary. Code decides everything else: the contract gate (schema + verified envelope), the budget gate,
seeded runs into an append-only registry, replications sized from a target CI half-width, and a claim check of
every sentence. Prints one JSON line per milestone, seam and fitness function; exits 1 on any failure.
python run_project.py [--inject few-reps|unseeded|no-contract|no-budget-gate] [--real-model]
"""
import argparse
import json
import os
import sys
from pathlib import Path

import agent
import claims
import model
import pipeline
import registry as reg
import stats

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
BRIEF = ("Help-desk study, seed 13. Screen with sobol 64. Screen with morris 10. "
         "Compare mu 1.0 vs 1.05 at lam 0.8 with 3 replications. Compare mu 1.0 vs 1.05 at lam 0.97 with 3 replications.")
SIM_BUDGET, HALF_WIDTH, MAX_CALLS = 300_000, 0.3, 8  # customers per session; min; agent model calls
FAULTS = ("few-reps", "unseeded", "no-contract", "no-budget-gate")


def verify_model():
    """M1 (L100 #6 V&V): 95% CI of 10 long runs must cover the M/M/1 formula; same seed -> same bits."""
    rows = []
    for rho in (0.5, 0.8, 0.9):
        p = {"lam": rho, "mu": 1.0, "backlog": 0, "customers": 20_000, "warmup": 2_000}
        m, h = stats.mean_ci([model.run_once(p, model.seed_for(6, 0, r)) for r in range(10)])
        rows.append({"rho": rho, "sim": round(m, 3), "half_width": round(h, 3), "formula": round(model.mm1_wq(rho, 1.0), 3),
                     "covered": abs(m - model.mm1_wq(rho, 1.0)) <= h})
    p = {"lam": 0.8, "mu": 1.0}
    same = model.run_once(p, 123).hex() == model.run_once(p, 123).hex()
    return rows, same


def session(inject, real_model, registry):
    pl = pipeline.Pipeline(registry, pipeline.SimBudget(SIM_BUDGET, gate=inject != "no-budget-gate"),
                           half_width=HALF_WIDTH, policy=pipeline.naive_policy if inject == "few-reps" else None,
                           gate=inject != "no-contract", seeded=inject != "unseeded")
    server = None
    if real_model:
        url, name = os.environ.get("LOCAL_MODEL_URL", "http://localhost:11434/v1"), os.environ.get("LOCAL_MODEL", "qwen2.5:1.5b")
    else:
        import fake_sim_agent
        (server, url), name = fake_sim_agent.start_in_thread(), "fake-model"
    try:
        out = agent.run_session(BRIEF, pl, url, name, max_calls=MAX_CALLS)
    finally:
        if server:
            server.shutdown()
            server.server_close()
    return pl, out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--inject", choices=FAULTS)
    ap.add_argument("--real-model", action="store_true")
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args(argv)
    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "registry.jsonl").unlink(missing_ok=True)  # fresh registry per run (append-only within a run)
    registry = reg.Registry(out_dir / "registry.jsonl")
    lines = []

    def score(kind, name, passed, **measures):
        lines.append({kind: name, "pass": bool(passed), **measures})
        print(json.dumps(lines[-1]))

    v_rows, same = verify_model()
    pl, out = session(args.inject, args.real_model, registry)
    rows, published = claims.review(out["summary"], registry)
    rejected_jobs = [j for j in pl.jobs if j["states"][-1] == "REJECTED"]
    by_contract = [j["job"] for j in rejected_jobs if "VALIDATED" not in j["states"]]
    by_budget = [j["job"] for j in rejected_jobs if "VALIDATED" in j["states"]]
    runs_rejected = sum(r["job"] in by_contract + by_budget for r in registry.runs())
    outside = [j["job"] for j in pl.jobs if j["tool"] == "run_experiment" and "RAN" in j["states"]
               and max(j["args"][a]["lam"] / j["args"][a]["mu"] for a in ("baseline", "candidate")) > 0.9]
    exps = [r for r in registry.records if r["kind"] == "experiment" and "verdict" in r["facts"]]
    ab = {k: v["value"] for k, v in exps[0]["facts"].items()} if exps else {}
    hw = ab.get("difference_half_width", float("inf"))
    run_ids = registry.run_ids()
    facts_ok = all(set(f["runs"]) <= run_ids for e in registry.records if e["kind"] == "experiment" for f in e["facts"].values())
    repro = [reg.reproduce(r) for r in registry.runs()]
    found, traced = claims.traced_runs(published, registry)
    recheck = [r for r in claims.review(published, registry)[0] if not r["ok"]]
    overclaim = [r["sentence"] for r in rows if "significan" in r["sentence"] and not r["ok"]]

    score("milestone", "M1 model verified (V&V) + reproducible", all(r["covered"] for r in v_rows) and same,
          checks=v_rows, same_seed_same_bits=same, model=f"{model.NAME}@{model.VERSION}")
    score("milestone", "M2 contract gate before any run", bool(by_contract) and not outside and not runs_rejected,
          rejected_by_contract=by_contract, ran_outside_envelope=outside, runs_for_rejected_jobs=runs_rejected)
    score("milestone", "M3 experiment registry", len(repro) > 0 and facts_ok and all(repro),
          runs=len(repro), experiments=len([r for r in registry.records if r["kind"] == "experiment"]),
          facts_trace_to_runs=facts_ok)
    score("milestone", "M4 replications from target half-width", hw <= HALF_WIDTH and ab.get("replications", 0) >= 10,
          requested=3, replications=ab.get("replications"), diff_half_width=round(hw, 3), target=HALF_WIDTH,
          verdict=ab.get("verdict"), diff=round(ab.get("difference", 0), 3))
    score("milestone", "M5 claim check + published report", bool(rows) and not recheck,
          sentences=len(rows), rejected=[{"sentence": r["sentence"][:60], "reason": r["reason"]} for r in rows if not r["ok"]])
    score("seam", "agent <-> tool schema", bool(by_contract) and not outside, test="tests/test_seam_contract.py")
    score("seam", "agent claims <-> computed statistics", not recheck and all(not r["ok"] for r in rows
          if r["sentence"].startswith("At lam")), test="tests/test_seam_claims.py")
    score("seam", "sim stochasticity <-> conclusions", ab.get("verdict") != "inconclusive" and hw <= HALF_WIDTH
          and not overclaim, verdict=ab.get("verdict"), overclaims_rejected=overclaim, test="tests/test_seam_replications.py")
    score("seam", "cost/time budget", pl.budget.spent <= SIM_BUDGET and out["calls"] <= MAX_CALLS
          and not runs_rejected, rejected_by_budget=by_budget, spent=pl.budget.spent, limit=SIM_BUDGET, agent_calls=out["calls"], ledger=pl.budget.ledger,
          test="tests/test_seam_budget.py")
    score("fitness", "100% of numeric claims traced to a registry run", found > 0 and traced == found,
          numbers=found, traced=traced, test="tests/test_fitness.py::test_claims_traced")
    score("fitness", "every run reproducible bit-for-bit from its seed", repro and all(repro),
          reproduced=sum(repro), runs=len(repro), env=model.ENVIRONMENT, test="tests/test_fitness.py::test_runs_reproducible")
    score("fitness", "budget never exceeded", pl.budget.spent <= SIM_BUDGET
          and sum(a for _, a in pl.budget.ledger) == pl.budget.spent, spent=pl.budget.spent, limit=SIM_BUDGET,
          test="tests/test_fitness.py::test_budget_never_exceeded")
    passed = sum(x["pass"] for x in lines)
    final = {"scorecard": "PASS" if passed == len(lines) else "FAIL", "passed": passed, "total": len(lines),
             "inject": args.inject}
    print(json.dumps(final))
    registry.close()
    (out_dir / "scorecard.jsonl").write_text("".join(json.dumps(x) + "\n" for x in lines + [final]), encoding="utf-8")
    (out_dir / "report.md").write_text(f"# Published summary\n\n{published}\n\n# Agent draft\n\n{out['summary']}\n",
                                   encoding="utf-8")
    return 0 if final["scorecard"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
