import time
import unittest
import urllib.parse

from app import REDIRECT, query, start
from id_token_rules import validate_claims
from jwt_hs256 import InvalidToken, b64url, sign, verify
from keycloak_check import check_discovery
from mock_idp import s256
from rp_client import LoginFailed, browser_follow


class PkceTest(unittest.TestCase):
    def test_rfc7636_appendix_b_vector(self):
        self.assertEqual(s256("dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"),
                         "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM")


class JwtTest(unittest.TestCase):
    def test_round_trip_and_tampering(self):
        token = sign({"sub": "m1"}, "k")
        self.assertEqual(verify(token, "k")[1], {"sub": "m1"})
        head, body, sig = token.split(".")
        admin = b64url(b'{"sub": "admin"}')
        forged = f"{head}.{admin}.{sig}"
        self.assertRaisesRegex(InvalidToken, "signature does not match", verify, forged, "k")
        self.assertRaisesRegex(InvalidToken, "signature does not match", verify, token, "other-key")

    def test_alg_none_is_rejected(self):
        unsigned = sign({"sub": "m1"}, "k", header={"alg": "none"}).rsplit(".", 1)[0] + "."
        self.assertRaisesRegex(InvalidToken, "alg 'none' not allowed", verify, unsigned, "k")


class ClaimRulesTest(unittest.TestCase):
    NOW = 1_800_000_000
    GOOD = {"iss": "https://idp", "sub": "m1", "aud": "library-web", "exp": NOW + 300, "iat": NOW, "nonce": "n1"}

    def check(self, **changes):
        return validate_claims({**self.GOOD, **changes}, issuer="https://idp", client_id="library-web",
                               nonce="n1", now=self.NOW)

    def test_good_token(self):
        self.assertEqual(self.check(), [])
        self.assertEqual(self.check(aud=["other-api", "library-web"]), [])

    def test_each_rule(self):
        self.assertIn("is not the expected issuer", self.check(iss="https://evil")[0])
        self.assertIn("does not contain 'library-web'", self.check(aud="other-app")[0])
        self.assertIn("token expired", self.check(exp=self.NOW - 61)[0])
        self.assertEqual(self.check(exp=self.NOW - 59), [])  # 60 s leeway for clock skew
        self.assertIn("in the future", self.check(iat=self.NOW + 3600)[0])
        self.assertIn("nonce does not match", self.check(nonce="n2")[0])


class FlowTest(unittest.TestCase):
    def setUp(self):
        self.idp, self.rp = start()
        self.addCleanup(self.idp.__exit__, None, None, None)

    def login(self):
        url, pending = self.rp.start_login()
        return browser_follow(url), pending

    def test_happy_path(self):
        callback, pending = self.login()
        claims = self.rp.finish_login(callback, pending)
        self.assertEqual((claims["sub"], claims["aud"], claims["nonce"]), ("member-m1", "library-web", pending.nonce))
        self.assertEqual(len(pending.code_verifier), 43)  # 32 random bytes, base64url

    def test_code_is_single_use(self):
        callback, pending = self.login()
        self.rp.finish_login(callback, pending)
        self.assertRaisesRegex(LoginFailed, "code unknown or already used", self.rp.finish_login, callback, pending)

    def test_stolen_code_without_verifier_fails(self):
        callback, pending = self.login()
        pending.code_verifier = "attacker-does-not-know-the-verifier-" + "x" * 10
        self.assertRaisesRegex(LoginFailed, "PKCE verification failed", self.rp.finish_login, callback, pending)

    def test_state_mismatch_stops_before_token_request(self):
        callback, pending = self.login()
        pending.state = "other"
        self.assertRaisesRegex(LoginFailed, "state does not match", self.rp.finish_login, callback, pending)

    def test_unregistered_redirect_uri_is_not_followed(self):
        url, _ = self.rp.start_login()
        evil = url.replace(urllib.parse.quote(REDIRECT, safe=""), urllib.parse.quote("https://evil.example/cb", safe=""))
        self.assertTrue(browser_follow(evil).startswith("(no redirect: 400"))

    def test_rp_rejects_token_for_another_audience(self):
        self.idp.overrides = {"aud": "other-app"}
        callback, pending = self.login()
        self.assertRaisesRegex(LoginFailed, "does not contain 'library-web'", self.rp.finish_login, callback, pending)

    def test_rp_rejects_expired_token(self):
        self.idp.overrides = {"exp": int(time.time()) - 3600}
        callback, pending = self.login()
        self.assertRaisesRegex(LoginFailed, "token expired", self.rp.finish_login, callback, pending)

    def test_missing_pkce_is_refused_by_the_idp(self):
        url, pending = self.rp.start_login()
        no_pkce = url.split("&code_challenge=")[0]
        self.assertEqual(query(browser_follow(no_pkce))["error"], "invalid_request")

    def test_discovery_document(self):
        self.assertEqual(check_discovery(self.idp.discovery(), self.idp.issuer, signing_alg="HS256"), [])
        self.assertIn("RS256 not in id_token_signing_alg_values_supported",
                      check_discovery(self.idp.discovery(), self.idp.issuer))


if __name__ == "__main__":
    unittest.main()
