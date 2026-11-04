"""Tests for lab 05 agent assist. Run: python -m unittest -v
Runs only against the deterministic fake model server (127.0.0.1, random free port); no real model needed.
"""
import importlib.util
import os
import unittest

import agent_assist
import fake_qasm_rule
from local_agent import fake_model_server


class AgentAssistFake(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fake_qasm_rule.register(fake_model_server)
        cls.server, cls.url = fake_model_server.start_in_thread()
        cls.results = agent_assist.run(cls.url)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_correct_bell_draft_is_accepted_and_only_00_11(self):
        ok, reason, counts = self.results["bell"]
        self.assertTrue(ok, reason)
        self.assertLessEqual(set(counts), {"00", "11"})
        self.assertEqual(sum(counts.values()), 1000)

    def test_wrong_circuit_is_rejected_by_the_simulator_check(self):
        ok, reason, counts = self.results["ghz3"]
        self.assertFalse(ok)
        self.assertIn("'011': 0.5", reason)
        self.assertIsNone(counts)

    def test_unverifiable_draft_is_rejected(self):
        ok, reason, _ = self.results["phase"]
        self.assertFalse(ok)
        self.assertEqual(reason, "parser: unsupported statement: 'rz(pi/2) q[0]'")


class CheckIsDeterministicCode(unittest.TestCase):
    def test_reply_without_program_is_rejected(self):
        self.assertEqual(agent_assist.check("I cannot help.", {"0": 1.0})[:2], (False, "no OpenQASM program found"))

    def test_unfenced_openqasm2_program_is_read(self):
        reply = 'Sure. OPENQASM 2.0; include "qelib1.inc"; qreg q[2]; creg c[2]; h q[0]; cx q[0],q[1]; measure q -> c;'
        self.assertEqual(agent_assist.check(reply, {"00": 0.5, "11": 0.5})[:2], (True, "matches spec"))

    def test_same_seed_same_counts(self):
        p = {"00": 0.5, "11": 0.5}
        self.assertEqual(agent_assist.sample_counts(p), agent_assist.sample_counts(p))


HAVE_QISKIT = all(importlib.util.find_spec(m) for m in ("qiskit", "qiskit_qasm3_import"))
if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit/qiskit-qasm3-import are not installed")


@unittest.skipUnless(HAVE_QISKIT, "qiskit/qiskit-qasm3-import not installed (runs in CI)")
class SdkAgreesWithTheJudge(unittest.TestCase):
    def probs(self, program):
        from qiskit import qasm3
        from qiskit.quantum_info import Statevector
        qc = qasm3.loads(program)
        qc.remove_final_measurements()
        return {k: round(float(v), 12) for k, v in Statevector(qc).probabilities_dict().items() if v > 1e-12}

    def test_accepted_and_rejected_drafts_in_qiskit(self):
        self.assertEqual(self.probs(fake_qasm_rule.BELL), {"00": 0.5, "11": 0.5})
        self.assertEqual(self.probs(fake_qasm_rule.GHZ_BUGGY), {"000": 0.5, "011": 0.5})
        self.assertEqual(self.probs(fake_qasm_rule.BELL_PHASE), {"00": 0.5, "11": 0.5})  # correct, just unverifiable by the tiny parser


if __name__ == "__main__":
    unittest.main()
