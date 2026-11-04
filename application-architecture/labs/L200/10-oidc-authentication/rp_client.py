"""Relying Party (the Library Loans web app): authorization code flow + PKCE, then ID token validation."""
import base64
import hashlib
import hmac
import http.client
import json
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

from id_token_rules import validate_claims
from jwt_hs256 import InvalidToken, verify


class LoginFailed(Exception):
    pass


@dataclass
class PendingLogin:  # kept server-side in the user's session between redirect and callback
    state: str
    nonce: str
    code_verifier: str


class RelyingParty:
    def __init__(self, issuer, client_id, client_secret, redirect_uri, clock=time.time):
        self.client_id, self.secret, self.redirect_uri, self.clock = client_id, client_secret, redirect_uri, clock
        with urllib.request.urlopen(f"{issuer}/.well-known/openid-configuration") as resp:
            self.config = json.loads(resp.read())  # discovery: endpoints come from the provider
        if self.config["issuer"] != issuer:
            raise LoginFailed(f"discovery issuer {self.config['issuer']!r} != {issuer!r}")

    def start_login(self):
        login = PendingLogin(secrets.token_urlsafe(16), secrets.token_urlsafe(16), secrets.token_urlsafe(32))
        challenge = base64.urlsafe_b64encode(hashlib.sha256(login.code_verifier.encode("ascii")).digest())
        query = {"response_type": "code", "scope": "openid", "client_id": self.client_id,
                 "redirect_uri": self.redirect_uri, "state": login.state, "nonce": login.nonce,
                 "code_challenge": challenge.rstrip(b"=").decode(), "code_challenge_method": "S256"}  # PKCE
        return f"{self.config['authorization_endpoint']}?{urllib.parse.urlencode(query)}", login

    def finish_login(self, callback_url, login):
        params = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(callback_url).query))
        if not hmac.compare_digest(params.get("state", ""), login.state):  # CSRF: callback must answer OUR request
            raise LoginFailed("state does not match this login attempt")
        if "error" in params:
            raise LoginFailed(f"provider returned error {params['error']}")
        status, tokens = self._post_token({"grant_type": "authorization_code", "code": params["code"],
                                           "redirect_uri": self.redirect_uri, "client_id": self.client_id,
                                           "client_secret": self.secret, "code_verifier": login.code_verifier})
        if status != 200:
            raise LoginFailed(f"token endpoint {status}: {tokens.get('error')}: {tokens.get('error_description', '')}")
        try:
            _, claims = verify(tokens["id_token"], self.secret)  # 1. signature + allowed alg
        except InvalidToken as exc:
            raise LoginFailed(str(exc)) from exc
        problems = validate_claims(claims, issuer=self.config["issuer"], client_id=self.client_id,
                                   nonce=login.nonce, now=self.clock())  # 2. iss, aud, exp, iat, nonce
        if problems:
            raise LoginFailed("; ".join(problems))
        return claims

    def _post_token(self, form):
        req = urllib.request.Request(self.config["token_endpoint"], data=urllib.parse.urlencode(form).encode(),
                                     headers={"Content-Type": "application/x-www-form-urlencoded"})
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as err:
            return err.code, json.loads(err.read())


def browser_follow(url):
    """Stand-in for the user's browser: GET the authorize URL and return the redirect Location (not followed)."""
    parts = urllib.parse.urlsplit(url)
    conn = http.client.HTTPConnection(parts.hostname, parts.port, timeout=10)
    conn.request("GET", f"{parts.path}?{parts.query}")
    resp = conn.getresponse()
    location, body = resp.getheader("Location"), resp.read()
    conn.close()
    return location or f"(no redirect: {resp.status} {body.decode('utf-8')})"

