"""Capstone scorecard (python run_capstone.py [--explain [--fake]]): runs the chaos campaign, then prints one JSON line
per rubric criterion and a final verdict. Deterministic code decides every pass/fail. With --explain a local model
explains the chaos results; its claims are checked against the campaign and it never changes the verdict."""
import json, sys

from chaos_campaign import BLAST_PCT, campaign

RUBRIC = ["money invariant (audit)", "no lost orders", "one order and one charge per key", "exactly-once effects",
          "outbox delivered", "one trace per order", "bounded queue", "config via Raft"]


def scorecard(runs):
    rows = []
    for criterion in RUBRIC:
        passed = sum(results[criterion][0] for _, results in runs)
        baseline = next(results[criterion][1] for row, results in runs if row["experiment"] == "baseline")
        rows.append({"criterion": criterion, "measure": f"passes in {passed}/{len(runs)} runs (baseline: {baseline})",
                     "pass": passed == len(runs)})
    held = sum(row["held"] for row, _ in runs)
    rows.append({"criterion": "chaos hypotheses held", "measure": f"{held}/{len(runs)} experiments", "pass": held == len(runs)})
    radius = max(row["blast_radius_pct"] or 0 for row, _ in runs)
    rows.append({"criterion": "blast radius of order faults", "measure": f"max {radius}% (limit {BLAST_PCT:.0f}%)",
                 "pass": radius <= BLAST_PCT})
    return rows


def main(argv):
    runs = campaign()
    for row, _ in runs:
        print(json.dumps(row, sort_keys=True))
    rows = scorecard(runs)
    for r in rows:
        print(json.dumps(r))
    ok = all(r["pass"] for r in rows)
    print(json.dumps({"scorecard": f"{sum(r['pass'] for r in rows)}/{len(rows)}", "pass": ok}))
    if "--explain" in argv:
        import agent_assist
        agent_assist.explain([row for row, _ in runs], fake="--fake" in argv)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
