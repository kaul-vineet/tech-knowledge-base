import base64
import unittest

import agent_assist as aa
import local_ca


class TestAgentAssist(unittest.TestCase):
    def test_fake_server_run_code_is_judge(self):
        rows = aa.main([]) or None  # prints the table
        self.assertIsNone(rows)

    def test_diagnose_categories(self):
        server, url = aa.fake_model_server.start_in_thread()
        try:
            rows = aa.run(url, aa.fake_model_server.MODEL_ID)
        finally:
            server.shutdown()
            server.server_close()
        truth = {r[0]: r[2] for r in rows}
        self.assertEqual(truth, {"wrong host": "HOSTNAME_MISMATCH", "expired": "EXPIRED",
                                 "clock skew": "NOT_YET_VALID", "untrusted CA": "UNTRUSTED_ISSUER"})
        self.assertEqual([r[4] for r in rows], ["CONFIRMED", "CONFIRMED", "REJECTED", "CONFIRMED"])
        self.assertTrue(all(r[1] == "FAIL" for r in rows))

    def test_ok_case(self):
        k, ca = local_ca.make_root()
        _, leaf = local_ca.issue_server(k, ca)
        self.assertEqual(aa.diagnose(leaf, [ca], "localhost", local_ca.NOW), "OK")

    def test_secret_guard(self):
        with self.assertRaises(ValueError):
            aa.ask_agent("-----BEGIN PRIVATE KEY-----\nabc", "http://127.0.0.1:9/v1", "x")

    def test_secret_guard_catches_base64_keys_and_jwk(self):
        key = bytes(range(1, 33))
        for leaky in (base64.b64encode(key).decode(),                          # 44 chars, padded
                      base64.urlsafe_b64encode(key).rstrip(b"=").decode(),     # 43 chars, base64url
                      '{"kty":"OKP","d":"nWGxne_9WmC6hEr0kuwsxERJxWl7MmkZcDusAxyuf2A"}'):  # JWK private member
            with self.assertRaises(ValueError):
                aa.ask_agent(leaky, "http://127.0.0.1:9/v1", "x")

    def test_public_reports_pass_the_guard(self):
        for label, leaf, roots, host, at in aa.scenarios():
            self.assertIsNone(aa.SECRET.search(aa.report(leaf, host, at, "some error")), label)


if __name__ == "__main__":
    unittest.main()
