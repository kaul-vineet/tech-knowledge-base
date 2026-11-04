"""Try it (lesson 19): add a handler that forgets authorize(); a suspended librarian tries to borrow.

Run: python try_it.py   (scratch copy in .tryit-work/, deleted after)
"""
import shutil
import time

import fitness_policy
from app import HERE
from rego_lite import DecisionPoint, load_policy

WORK = HERE / ".tryit-work"


def try_1_handler_without_check():
    WORK.mkdir(exist_ok=True)
    text = (HERE / "handlers.py").read_text(encoding="utf-8")
    text += "\n\ndef renew(pdp, subject, resource, loan_id):\n    return {\"loan_id\": loan_id, \"status\": \"renewed\"}\n"
    (WORK / "handlers.py").write_text(text, encoding="utf-8")
    print(f"[1] new renew() handler -> {fitness_policy.gate_pep_coverage(WORK / 'handlers.py')}")


def try_2_deny_overrides_allow():
    pdp = DecisionPoint(load_policy(HERE / "solution" / "loans.rego"))
    inp = {"action": "borrow", "subject": {"id": "s1", "tenant": "lib00", "roles": ["librarian"], "suspended": True},
           "resource": {"tenant": "lib00", "member_id": "m2", "active_loans": 0}}
    print(f"[2] suspended librarian borrows for m2 -> {pdp.decide(inp)}")


if __name__ == "__main__":
    try:
        try_1_handler_without_check()
        try_2_deny_overrides_allow()
    finally:
        for _ in range(5):  # retry: some network mounts need a second pass
            shutil.rmtree(WORK, ignore_errors=True)
            if not WORK.exists():
                break
            time.sleep(0.5)
