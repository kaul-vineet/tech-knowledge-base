"""Agent assist runs against the deterministic fake model server only; the checker's verdicts are asserted."""
import contextlib
import io
import unittest

import agent_assist
import threat_model as tm


class TestAgentAssist(unittest.TestCase):
    def test_checker_decides_each_proposal(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            agent_assist.main([])
        self.assertIn("verdicts {'CONFIRMED': 2, 'GAP': 1, 'REJECTED': 3}", out.getvalue())
        self.assertIn("REJECTED - control C-QUANTUM-SHIELD does not exist", out.getvalue())

    def test_prompt_carries_no_secrets_and_gate_bites(self):
        m = tm.load()
        self.assertNotIn("PRIVATE KEY", agent_assist.prompt_for(m))
        m["elements"]["-----BEGIN PRIVATE KEY-----"] = {"type": "store", "zone": "app"}
        with self.assertRaises(ValueError):
            agent_assist.prompt_for(m)

    def test_unverified_control_is_not_confirmed(self):
        m = tm.load()
        m["controls"]["C-DUAL-SIG"]["tests"] = ["labs/L400/17-crypto-agility/test_build_task.py::X::gone"]
        verdict = agent_assist.judge(m, ("doc-api->envelope-db", "T", "swap", "C-DUAL-SIG"))
        self.assertTrue(verdict.startswith("REJECTED"))


if __name__ == "__main__":
    unittest.main()
