"""Fitness functions (lesson 19). Run: python fitness_policy.py [--solution]   (exit 1 = a gate failed)

policy-tests   every requirement case in policy/cases.json gets the expected decision
rule-coverage  every allow/deny rule body is the reason for at least one case (like opa test --coverage)
pep-coverage   every public handler in handlers.py calls authorize() as its first statement
"""
import ast
import json
import pathlib
import sys

from rego_lite import DecisionPoint, load_policy

HERE = pathlib.Path(__file__).resolve().parent
CASES = json.loads((HERE / "policy" / "cases.json").read_text(encoding="utf-8"))["cases"]


def gate_policy_tests(policy):
    pdp = DecisionPoint(policy)
    failed = [c["id"] for c in CASES if pdp.decide(c["input"])["allowed"] != c["allowed"]]
    return {"gate": "policy-tests", "ok": not failed, "value": failed, "budget": f"{len(CASES)}/{len(CASES)} pass"}


def gate_rule_coverage(policy):
    pdp, covered = DecisionPoint(policy), set()
    for c in CASES:
        covered.update(pdp.decide(c["input"])["matched"])
    rules = [r[0] for r in policy.rules if r[1] in ("allow", "deny")]
    missing = [r for r in rules if r not in covered]
    return {"gate": "rule-coverage", "ok": not missing, "value": missing, "budget": "every allow/deny rule"}


def gate_pep_coverage(path=HERE / "handlers.py"):
    missing = []
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_") and node.name != "authorize":
            first = node.body[0]
            call = first.value if isinstance(first, ast.Expr) else getattr(first, "value", None)
            if not (isinstance(call, ast.Call) and getattr(call.func, "id", "") == "authorize"):
                missing.append(node.name)
    return {"gate": "pep-coverage", "ok": not missing, "value": missing, "budget": "0 handlers without authorize()"}


def main(argv=None):
    policy = load_policy(HERE / ("solution" if "--solution" in (argv or sys.argv[1:]) else "policy") / "loans.rego")
    results = [gate_policy_tests(policy), gate_rule_coverage(policy), gate_pep_coverage()]
    for r in results:
        print(json.dumps(r))
    return 0 if all(r["ok"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
