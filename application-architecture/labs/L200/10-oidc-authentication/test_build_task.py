"""Build task check: validate_claims(..., max_age=N) enforces auth_time (recent login for sensitive actions).

By default this checks solution/id_token_rules.py. To check your edited id_token_rules.py instead:
    CHECK_MINE=1 python -m unittest test_build_task -v        (PowerShell: $env:CHECK_MINE = "1")
"""
import importlib.util
import os
import pathlib
import time
import unittest

from app import start
from jwt_hs256 import verify
from rp_client import browser_follow

HERE = pathlib.Path(__file__).resolve().parent
TARGET = HERE / ("id_token_rules.py" if os.environ.get("CHECK_MINE") else "solution/id_token_rules.py")
spec = importlib.util.spec_from_file_location("rules_under_test", TARGET)
rules = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rules)
NOW = 1_800_000_000
GOOD = {"iss": "https://idp", "sub": "m1", "aud": "library-web", "exp": NOW + 300, "iat": NOW, "nonce": "n1"}


def check(max_age=None, **changes):
    return rules.validate_claims({**GOOD, **changes}, issuer="https://idp", client_id="library-web", nonce="n1",
                                 now=NOW, max_age=max_age)


class MaxAgeTest(unittest.TestCase):
    def test_without_max_age_nothing_changes(self):
        self.assertEqual(check(), [])

    def test_auth_time_required_with_max_age(self):
        self.assertEqual(check(max_age=300), ["auth_time is required when max_age is used"])

    def test_recent_login_passes_old_login_fails(self):
        self.assertEqual(check(max_age=300, auth_time=NOW - 200), [])
        self.assertEqual(check(max_age=300, auth_time=NOW - 7200), ["login is 7200 s old, max_age is 300 s"])

    def test_old_rules_still_apply(self):
        self.assertIn("does not contain 'library-web'", check(max_age=300, auth_time=NOW, aud="x")[0])

    def test_with_tokens_from_the_mock_idp(self):
        idp, rp = start()
        self.addCleanup(idp.__exit__, None, None, None)
        idp.overrides = {"auth_time": int(time.time()) - 7200}  # an IdP that did not re-authenticate
        url, pending = rp.start_login()
        params = dict(p.split("=", 1) for p in browser_follow(url).split("?", 1)[1].split("&"))
        status, tokens = rp._post_token({"grant_type": "authorization_code", "code": params["code"],
                                         "redirect_uri": rp.redirect_uri, "client_id": rp.client_id,
                                         "client_secret": rp.secret, "code_verifier": pending.code_verifier})
        _, claims = verify(tokens["id_token"], rp.secret)
        problems = rules.validate_claims(claims, issuer=idp.issuer, client_id="library-web", nonce=pending.nonce,
                                         now=time.time(), max_age=300)
        self.assertEqual(len(problems), 1)
        self.assertRegex(problems[0], r"login is 72\d\d s old, max_age is 300 s")


if __name__ == "__main__":
    unittest.main()
