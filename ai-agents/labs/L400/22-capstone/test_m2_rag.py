"""Milestone 2: runbook retrieval + grounded citations (lesson 7's RAG over runbooks/)."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from capstone_fixture import Env, INCIDENTS  # noqa: E402


class M2Rag(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env = Env()

    @classmethod
    def tearDownClass(cls):
        cls.env.close()

    def test_citations_come_from_retrieved_runbooks(self):
        agent = self.env.agent()
        got = {}
        for iid in ("INC-1", "INC-2", "INC-4"):
            status, done = agent.handle(INCIDENTS[iid])
            got[iid] = ([cid for cid, _ in done["retrieve"]][0], done["propose"]["proposal"]["runbook"], done["propose"]["grounded"])
        agent.close()
        self.assertEqual(got, {"INC-1": ("RB-1-dependency-timeouts#0", "RB-1-dependency-timeouts#0", True),
                               "INC-2": ("RB-2-memory-pressure#0", "RB-2-memory-pressure#0", True),
                               "INC-4": ("RB-2-memory-pressure#0", "RB-3-bad-deploy-rollback#0", True)})  # cited hit #2


if __name__ == "__main__":
    unittest.main()
