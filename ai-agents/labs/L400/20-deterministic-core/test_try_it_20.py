"""Try it (lesson 20): change the policy in code; loosen the proposal schema."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import edge  # noqa: E402
import fake_server_l400  # noqa: E402
import policy  # noqa: E402


class TryIt(unittest.TestCase):
    def setUp(self):
        self.server, self.url = fake_server_l400.start_in_thread()
        self.ask = lambda p: edge.ask(p, self.url, "fake-model")

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def test_1_raise_auto_limit_to_150(self):
        old, policy.AUTO_LIMIT = policy.AUTO_LIMIT, 150.0
        try:
            out = edge.code_decides(edge.CASES[1], self.ask)
        finally:
            policy.AUTO_LIMIT = old
        print(f"\nobserved: c02 -> {out['action']} {out['amount']} ({out['rule']})")
        self.assertEqual((out["action"], out["amount"]), ("approve_auto", 120.0))

    def test_2_allow_extra_keys_in_proposals(self):
        old = edge.PROPOSAL_SCHEMA["additionalProperties"]
        edge.PROPOSAL_SCHEMA["additionalProperties"] = True
        try:
            out = edge.code_decides(edge.CASES[3], self.ask)
        finally:
            edge.PROPOSAL_SCHEMA["additionalProperties"] = old
        print(f"\nobserved: c04 proposal problems {out['proposal_problems']} -> decision {out['action']}")
        self.assertEqual((out["proposal_problems"], out["action"]), ([], "deny"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
