"""Evals in CI for the capstone: decisions and runbook citations vs golden_incidents.jsonl, gated with lesson 12's
regression gate. Run: python eval_capstone.py [--write-baseline]  (exit 1 = block the merge)"""
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent.parent / "L300" / "12-eval-golden-set")]
import eval_gate  # noqa: E402

GOLDEN = {g["id"]: g["expect"] for g in map(json.loads, (HERE / "golden_incidents.jsonl").read_text(encoding="utf-8").splitlines())}


def evaluate(rows, baseline_path=HERE / "baseline.json"):
    results = {}
    for r in rows:
        exp, problems = GOLDEN[r["incident"]], []
        problems += [f"severity {r['severity']} != {exp['severity']}"] if r["severity"] != exp["severity"] else []
        problems += [f"actions {r['actions']} != {exp['actions']}"] if r["actions"] != exp["actions"] else []
        if exp["runbook"] and r["runbook"] and not r["runbook"].startswith(exp["runbook"] + "-"):
            problems.append(f"runbook {r['runbook']} != {exp['runbook']}")
        results[r["incident"]] = {"pass": not problems, "problems": problems}
    passed = sum(x["pass"] for x in results.values())
    report = {"passed": passed, "total": len(results), "pass_rate": round(passed / len(results), 3), "results": results}
    baseline = json.loads(Path(baseline_path).read_text(encoding="utf-8")) if Path(baseline_path).exists() else report
    return report, eval_gate.gate(report, baseline, min_pass_rate=1.0)


if __name__ == "__main__":
    import run_capstone
    with tempfile.TemporaryDirectory(dir=HERE) as d:
        rows, _, _ = run_capstone.run(d, faults=False)
    report, reasons = evaluate(rows)
    if "--write-baseline" in sys.argv:
        (HERE / "baseline.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
        print("baseline written")
        sys.exit(0)
    print(f"{report['passed']}/{report['total']} incidents pass; GATE: " + ("BLOCK - " + " | ".join(reasons) if reasons else "PASS"))
    sys.exit(1 if reasons else 0)
