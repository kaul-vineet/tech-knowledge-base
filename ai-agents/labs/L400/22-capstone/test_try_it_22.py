"""Try it (capstone): approve INC-1's rollback; remove the approval requirement for rollbacks (INC-1 only)."""
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import policy  # noqa: E402
import run_capstone  # noqa: E402

INC1 = [i for i in run_capstone.INCIDENTS if i["id"] == "INC-1"]


def card(**kw):
    with tempfile.TemporaryDirectory(dir=HERE) as d:
        rows, effects, spans = run_capstone.run(d, incidents=INC1, **kw)
    return rows[0], run_capstone.scorecard(rows, effects, spans)


class TryIt(unittest.TestCase):
    def test_1_lead_approves_inc1_rollback(self):
        row, c = card(decisions={"INC-1": "approve"})
        print(f"\nobserved: executed {row['executed']}, effects {c['effects']}, rollbacks_without_approval {c['rollbacks_without_approval']}")
        self.assertEqual((row["executed"], c["rollbacks_without_approval"]), (["page_oncall", "rollback_deploy"], 0))

    def test_2_rollback_without_approval_gate(self):
        policy.NEEDS_APPROVAL.discard("rollback_deploy")
        try:
            row, c = card()
        finally:
            policy.NEEDS_APPROVAL.add("rollback_deploy")
        print(f"\nobserved: approval {row['approval']}, executed {row['executed']}, "
              f"rollbacks_without_approval {c['rollbacks_without_approval']}, pass {c['pass']}")
        self.assertEqual((c["rollbacks_without_approval"], c["pass"]), (1, False))


if __name__ == "__main__":
    unittest.main(verbosity=2)
