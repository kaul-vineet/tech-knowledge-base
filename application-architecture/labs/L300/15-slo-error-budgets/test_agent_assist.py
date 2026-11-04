import contextlib
import io
import pathlib
import sys
import unittest

import agent_assist
from agent_assist import check_summary, draft, facts

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1].parent / "_shared"))
from local_agent import fake_model_server  # noqa: E402

FACTS = facts()


class CheckSummaryTest(unittest.TestCase):
    def test_facts_come_from_code(self):
        self.assertEqual((FACTS["alert"], FACTS["burn_rate"], FACTS["p99_ms"], FACTS["mean_ms"]),
                         ("latency page", "19.7", "2846.3", "147.9"))

    def test_correct_summary_passes(self):
        text = (f"The latency page fired (burn rate {FACTS['burn_rate']}); p99 {FACTS['p99_ms']} ms, "
                f"mean {FACTS['mean_ms']} ms, {FACTS['budget_used_1h']} of the 30-day budget.")
        self.assertEqual(check_summary(text, FACTS), [])

    def test_invented_number_is_rejected(self):
        self.assertIn("number 37 is not in the facts",
                      check_summary(f"p99 {FACTS['p99_ms']} ms, burn rate {FACTS['burn_rate']}, 37 members hit", FACTS))

    def test_mean_quoted_as_p99_is_rejected(self):
        problems = check_summary(f"p99 latency was {FACTS['mean_ms']} ms, burn rate {FACTS['burn_rate']}", FACTS)
        self.assertIn("p99 is 2846.3, the draft says 147.9", problems)


class FakeModelLoopTest(unittest.TestCase):
    def setUp(self):
        self.server, self.url = fake_model_server.start_in_thread()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)

    def test_first_draft_rejected_then_fixed(self):
        reply, problems, log = draft(self.url, "fake-model", FACTS)
        self.assertEqual(problems, [])
        self.assertTrue(log[0].startswith("attempt 1: REJECTED"))
        self.assertIn("burn rate is 19.7, the draft says 1.97", log[0])
        self.assertEqual(log[1], "attempt 2: OK")
        self.assertIn("p99 2846.3 ms", reply)

    def test_main_returns_zero(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(agent_assist.main([]), 0)
        self.assertIn("accepted draft (a human posts it)", out.getvalue())


if __name__ == "__main__":
    unittest.main()
