import base64
import unittest

import agent_assist as aa


class TestAgentAssist(unittest.TestCase):
    def test_fake_server_run(self):
        self.assertEqual(aa.main([]), 0)

    def test_scanner_is_the_judge(self):
        server, url = aa.fake_model_server.start_in_thread()
        try:
            rows, truth = aa.review(aa.Path(aa.HERE / "review_me.log").read_text(encoding="utf-8"), url, aa.fake_model_server.MODEL_ID)
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(truth, {2, 3, 6})
        verdicts = {n: v.split(" ")[0] for n, v in rows}
        self.assertEqual(verdicts, {2: "MISSED", 3: "CONFIRMED", 4: "REJECTED", 6: "MISSED"})

    def test_redaction_leaves_nothing_for_the_gate(self):
        text = aa.Path(aa.HERE / "review_me.log").read_text(encoding="utf-8")
        self.assertEqual(aa.gate(aa.redact(text)), aa.redact(text))
        self.assertNotIn("demo-only-s3cr3t", aa.redact(text))

    def test_gate_refuses_secret_like_text(self):
        key = base64.b64encode(bytes(range(32))).decode()
        for leaky in ("api_key: abcdef", "Bearer " + "x" * 30, "-----BEGIN PRIVATE KEY-----", key):
            with self.assertRaises(ValueError):
                aa.gate(leaky)


if __name__ == "__main__":
    unittest.main()
