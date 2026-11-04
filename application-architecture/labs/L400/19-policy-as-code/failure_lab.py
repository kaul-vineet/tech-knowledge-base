"""Lesson 19 failureLab: a new librarian rule without the tenant check lets librarians act in other libraries.

Run: python failure_lab.py
"""
import fitness_policy
from app import CASES, HERE
from rego_lite import DecisionPoint, load_policy

CROSS = next(c for c in CASES if c["id"] == "librarian of another library")


def main():
    print(f"request: {CROSS['input']}")
    for label, folder in [("base    ", "policy"), ("solution", "solution")]:
        policy = load_policy(HERE / folder / "loans.rego")
        decision = DecisionPoint(policy).decide(CROSS["input"])
        tests = fitness_policy.gate_policy_tests(policy)
        print(f"{label}: allowed={decision['allowed']} matched={decision['matched']}; policy tests failed: "
              f"{tests['value']}")


if __name__ == "__main__":
    main()
