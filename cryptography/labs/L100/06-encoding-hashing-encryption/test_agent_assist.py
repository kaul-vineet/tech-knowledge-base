import base64
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import agent_assist as aa
from local_agent import fake_model_server
from misuse_lint import lint

SNIPPET = Path(__file__).with_name("review_me.txt").read_text(encoding="utf-8")
FIXED = '''import os
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def reset_token():
    return secrets.token_urlsafe(32)


def seal(key, msg):
    nonce = os.urandom(12)
    return nonce + AESGCM(key).encrypt(nonce, msg, None)
'''


class TestLinter(unittest.TestCase):
    def test_finds_the_three_misuses(self):
        self.assertEqual([(f.rule, f.line) for f in lint(SNIPPET)],
                         [("CRY001", 9), ("CRY002", 21), ("CRY003", 13)])

    def test_fixed_code_is_clean(self):
        self.assertEqual(lint(FIXED), [])


class TestAgentAssist(unittest.TestCase):
    def setUp(self):
        self.server, self.url = fake_model_server.start_in_thread()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def test_linter_overrules_the_fake_agent(self):
        reply = aa.ask_agent(SNIPPET, self.url, "fake-model")
        r = aa.judge(SNIPPET, reply)
        self.assertEqual(list(r["confirmed"]), [("CRY001", 9), ("CRY003", 13)])
        self.assertEqual(list(r["missed"]), [("CRY002", 21)])     # agent cannot see data flow
        self.assertEqual(list(r["rejected"]), [("CRY003", 17)])   # SHA-256 file fingerprint is fine

    def test_perfect_reply_is_fully_confirmed(self):
        reply = "CRY001 line 9: x\nCRY003 line 13: y\nCRY002 line 21: z"
        r = aa.judge(SNIPPET, reply)
        self.assertEqual((len(r["confirmed"]), r["missed"], r["rejected"]), (3, {}, {}))

    def test_secret_guard_blocks_before_sending(self):
        leaky = SNIPPET + '\nKEY = "-----BEGIN PRIVATE KEY-----"\n'
        with self.assertRaises(ValueError):
            aa.ask_agent(leaky, "http://127.0.0.1:9/v1", "never-called")
        self.assertIn("long hex string", aa.find_secrets("k = '" + "ab" * 16 + "'"))

    def test_secret_guard_catches_base64_keys_and_jwk(self):
        key = bytes(range(1, 33))  # a 32-byte key in the three text forms people paste
        std = base64.b64encode(key).decode()                       # 44 chars, padded
        url = base64.urlsafe_b64encode(key).rstrip(b"=").decode()  # 43 chars, unpadded (JWK/JWT)
        self.assertIn("long base64 string", aa.find_secrets(f"KEY = '{std}'"))
        self.assertIn("long base64url string", aa.find_secrets(f"KEY = '{url}'"))
        jwk = '{"kty":"OKP","crv":"Ed25519","x":"11qYAYKxCrfVS_7TyWQHOg7hcvPapiMlrwIaaPcHURo","d":"nWGxne_9WmC6hEr0kuwsxERJxWl7MmkZcDusAxyuf2A"}'
        self.assertIn("JWK private member", aa.find_secrets(jwk))

    def test_secret_guard_lets_normal_code_through(self):
        self.assertEqual(aa.find_secrets(SNIPPET), [])
        self.assertEqual(aa.find_secrets("def this_is_a_rather_long_function_name_for_testing(x): pass"), [])

    def test_main_runs_with_fake_server(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(aa.main([]), 0)
        self.assertIn("VERDICT (from linter, not agent): FAIL - 3 misuse(s)", out.getvalue())


if __name__ == "__main__":
    unittest.main()
