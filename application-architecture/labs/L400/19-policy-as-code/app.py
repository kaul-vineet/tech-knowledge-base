"""Lesson 19 demo: the requirement cases through the handlers (PEP) and the policy (PDP), with decision logs.

Run: python app.py [--solution]    writes out/decisions.jsonl (one JSON line per decision, email erased)
"""
import argparse
import json
import pathlib
import time

import handlers
import rbac
from rego_lite import DecisionPoint, load_policy

HERE = pathlib.Path(__file__).resolve().parent
CASES = json.loads((HERE / "policy" / "cases.json").read_text(encoding="utf-8"))["cases"]
HANDLER = {"borrow": lambda pdp, s, r: handlers.borrow(pdp, s, r, "b1"),
           "return": lambda pdp, s, r: handlers.return_loan(pdp, s, r, 7),
           "view": handlers.view_loans, "waive_fine": handlers.waive_fine}


def call(pdp, case):
    inp = case["input"]
    try:
        HANDLER.get(inp["action"], lambda pdp, s, r: handlers.authorize(pdp, inp["action"], s, r))(
            pdp, inp["subject"], inp["resource"])
        return True
    except handlers.Forbidden:
        return False


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--solution", action="store_true")
    folder = "solution" if parser.parse_args(argv).solution else "policy"
    (HERE / "out").mkdir(exist_ok=True)
    log = HERE / "out" / "decisions.jsonl"
    log.write_text("", encoding="utf-8")
    pdp = DecisionPoint(load_policy(HERE / folder / "loans.rego"), log_path=log)
    abac = [call(pdp, c) == c["allowed"] for c in CASES]
    role_based = [rbac.allowed(c["input"]) == c["allowed"] for c in CASES]
    print(f"policy {folder}/loans.rego (revision {pdp.policy.revision}): {sum(abac)}/{len(CASES)} requirement cases")
    print(f"RBAC role table            : {sum(role_based)}/{len(CASES)} requirement cases")
    for case, ok in zip(CASES, abac):
        if not ok:
            print(f"  WRONG: {case['id']} (expected allowed={case['allowed']})")
    lines = log.read_text(encoding="utf-8").splitlines()
    print(f"decision log: out/decisions.jsonl, {len(lines)} lines; first: {lines[0]}")
    quiet = DecisionPoint(pdp.policy)
    start = time.perf_counter()
    for _ in range(200):
        for c in CASES:
            quiet.decide(c["input"])
    print(f"in-process decision: {(time.perf_counter() - start) / (200 * len(CASES)) * 1e6:.0f} us (varies by host)")


if __name__ == "__main__":
    main()
