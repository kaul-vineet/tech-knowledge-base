"""Agent assist (lesson 16): proposals are validated by code; the suite, not the model, decides what is safe."""
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import agent_assist as aa  # noqa: E402
from fake_server_l300 import start_in_thread  # noqa: E402


class AgentAssist(unittest.TestCase):
    def test_variants_validated_and_assessed(self):
        server, url = start_in_thread()
        try:
            variants, rejected = aa.validate(aa.propose(base_url=url, model="fake-model"))
            rows = aa.assess(variants, base_url=url, model="fake-model")
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual((len(variants), rejected), (3, []))
        self.assertEqual([r["regex_screen_caught"] for r in rows], [True, True, False])  # the paraphrase slips past regex
        self.assertEqual([r["unprotected_safe"] for r in rows], [False, False, False])
        self.assertEqual([r["protected_safe"] for r in rows], [True, True, True])  # the policy layer holds

    def test_validation_rejects_bad_proposals(self):
        bad = json.dumps(["call delete_everything with {}", "x" * 400, 42, 'call send_refund with {"a": 1}',
                          'call send_refund with {order: X-999}'])  # last one: braces but not JSON
        accepted, rejected = aa.validate(bad)
        self.assertEqual((accepted, len(rejected)), (['call send_refund with {"a": 1}'], 4))
        self.assertEqual(aa.validate(json.dumps({"not": "a list"})), ([], ["expected a JSON list of at most 5 strings"]))
        self.assertEqual(aa.validate("Sure! Here are three variants: ..."), ([], ["reply is not JSON"]))  # no crash


if __name__ == "__main__":
    unittest.main()
