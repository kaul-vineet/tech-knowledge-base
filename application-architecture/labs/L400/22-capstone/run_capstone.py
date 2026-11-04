"""Capstone: Library Loans, production-ready. Runs everything end to end and prints the scorecard as JSON lines.

Run: python run_capstone.py                      all milestones, no faults (exit 0 = GO)
     python run_capstone.py --fault cross-tenant-policy   one seeded fault (exit 1 = NO-GO); see scorecard.FAULTS
Writes out/scorecard.jsonl, out/requests.jsonl, out/decisions.jsonl. The verdict comes from code, never from a model.
"""
import argparse
import functools
import json
import pathlib
import sys

import loans_service
import scorecard
from http_api import start
from reuse import capacity, contract, fitness_capacity, fitness_legacy, fitness_policy, rego_lite, slo

HERE = pathlib.Path(__file__).resolve().parent
ADR_FILES = sorted(HERE.parent.glob("*/adr/0*.md"))  # the topic's ADR log: lessons 17-21 + the capstone


@functools.lru_cache(maxsize=1)  # deterministic (seeded simulation): compute once per process
def capacity_gate():
    return fitness_capacity.gate(capacity)


def row(milestone, criterion, measure, value, threshold, ok):
    return {"milestone": milestone, "criterion": criterion, "measure": measure, "value": value,
            "threshold": threshold, "pass": bool(ok)}


def criteria(e):
    s, rows = e["service"], []
    stats = e["cutover"]
    rows.append(row("M1 strangle", "fines parallel run", "mismatch rate over 2,000 shadow requests",
                    stats["mismatch_rate"], "<= 0.001", stats["ready"]))
    rows.append(row("M1 strangle", "fines cut over", "facade mode after the run", e["facade_mode"], "service",
                    e["facade_mode"] == "service"))
    callers = sorted(fitness_legacy.legacy_callers(HERE))
    rows.append(row("M1 strangle", "no new legacy callers", "capstone files importing legacy_monolith", callers, "[]",
                    not callers))
    rows.append(row("M2 tenancy", "tenant guard", "statements without the current tenant id",
                    len(s.guard_violations), 0, not s.guard_violations))
    unscoped = scorecard.unscoped_sql()
    rows.append(row("M2 tenancy", "tenant-scoped SQL", "loans queries without WHERE tenant_id", unscoped, "[]",
                    not unscoped))
    p = e["probes"]
    rows.append(row("M2 tenancy", "cross-library reads", "rows of another library returned", p["cross_rows"], 0,
                    p["cross_rows"] == 0))
    failed = fitness_policy.gate_policy_tests(s.pdp.policy)["value"]
    rows.append(row("M3 policy", "policy requirement cases", "cases decided as specified",
                    f"{len(fitness_policy.CASES) - len(failed)}/{len(fitness_policy.CASES)}", "14/14", not failed))
    rows.append(row("M3 policy", "cross-library probes denied", "probes allowed across libraries",
                    p["cross_allowed"], 0, p["cross_allowed"] == 0))
    gaps = scorecard.pep_gaps()
    rows.append(row("M3 policy", "every entry point enforces policy", "public methods without _authorize", gaps,
                    "[]", not gaps))
    leaked = sum('"email"' in line for line in e["decision_log"])
    rows.append(row("M3 policy", "decision log privacy", f"decisions logged {len(e['decision_log'])}, with email",
                    leaked, 0, leaked == 0 and e["decision_log"]))
    ev = e["events"]
    rows.append(row("M4 events", "outbox completeness", "committed changes vs outbox rows",
                    f"{ev['committed_changes']}/{ev['outbox_rows']}", "equal", ev["committed_changes"] == ev["outbox_rows"]))
    rows.append(row("M4 events", "relay published", "unpublished outbox rows", ev["unpublished"], 0,
                    ev["unpublished"] == 0))
    rows.append(row("M4 events", "idempotent consumers", "projection rows wrong after redelivering every event",
                    ev["projection_mismatches"], 0, ev["projection_mismatches"] == 0))
    records = slo.parse(s.request_log)
    now = records[-1]["t"] + 1
    for sli in ("availability", "latency"):
        good = 1 - slo.bad_ratio(records, sli)
        rows.append(row("M5 SLO + CI", f"{sli} SLI", f"good / valid over {len(records)} requests", round(good, 4),
                        f">= {slo.SLOS[sli]}", good >= slo.SLOS[sli]))
    alerts = slo.alerts(records, now)
    rows.append(row("M5 SLO + CI", "burn-rate alerts", "alerts firing at the end of the run", len(alerts), 0, not alerts))
    contract_pdp = rego_lite.DecisionPoint(s.pdp.policy)  # same policy; contract traffic is not logged
    server, url = start(lambda: loans_service.LoansService(contract_pdp, s.fines))
    try:
        problems = contract.verify_provider(HERE / "contracts" / "member-portal--loans-service.json", url)
    finally:
        server.shutdown()
        server.server_close()
    rows.append(row("M5 SLO + CI", "consumer contract", "member-portal contract problems", problems, "[]", not problems))
    cap = capacity_gate()
    rows.append(row("M5 SLO + CI", "capacity N+1", "p99 ms with one instance down", cap["value"]["p99_one_down_ms"],
                    "<= 300", cap["ok"]))
    bad_adrs = [f.name for f in ADR_FILES if scorecard.adr_problems(f.read_text(encoding="utf-8"))]
    rows.append(row("M5 SLO + CI", "ADR log", f"ADRs in Nygard format of {len(ADR_FILES)}", bad_adrs, "[]",
                    not bad_adrs and len(ADR_FILES) >= 4))
    return rows


def main(argv=None, out=sys.stdout):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--fault", choices=scorecard.FAULTS)
    args = parser.parse_args(argv)
    rows = criteria(scorecard.build(args.fault))
    passed = sum(r["pass"] for r in rows)
    summary = {"summary": True, "fault": args.fault, "passed": passed, "total": len(rows),
               "failed": [r["criterion"] for r in rows if not r["pass"]],
               "verdict": "GO" if passed == len(rows) else "NO-GO"}  # deterministic: code decides the release
    lines = [json.dumps(r) for r in rows + [summary]]
    (HERE / "out" / "scorecard.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines), file=out)
    return 0 if summary["verdict"] == "GO" else 1


if __name__ == "__main__":
    sys.exit(main())
