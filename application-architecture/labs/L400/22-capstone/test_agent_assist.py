import pathlib
import sys
import unittest

from agent_assist import check_note, draft

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "_shared"))
from local_agent import fake_model_server  # noqa: E402

NO_GO = {"passed": "16", "total": "19", "failed": "cross-library reads, policy requirement cases", "verdict": "NO-GO"}


class CheckNoteTest(unittest.TestCase):
    def test_optimistic_go_is_rejected(self):
        problems = check_note("Release summary: GO. 16 of 19 criteria passed.", NO_GO)
        self.assertIn("verdict is NO-GO, the note says GO", problems)

    def test_invented_number_is_rejected(self):
        problems = check_note("NO-GO: 17 of 19 passed; cross-library reads, policy requirement cases.", NO_GO)
        self.assertEqual(problems, ["number 17 is not in the scorecard"])

    def test_fake_model_loop_ends_honest(self):
        server, url = fake_model_server.start_in_thread()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        reply, problems, log = draft(url, "fake-model", NO_GO)
        self.assertEqual((problems, log[1]), ([], "attempt 2: OK"))
        self.assertTrue(reply.startswith("Release summary: NO-GO."))


if __name__ == "__main__":
    unittest.main()
