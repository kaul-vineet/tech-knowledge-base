"""LEARNING-ONLY mock OpenID Provider (stdlib). NOT an identity provider - never deploy or reuse it.

Shortcuts on purpose: no login page (it "logs in" a fixed user), plain HTTP on 127.0.0.1, HS256 ID tokens
signed with the client secret, in-memory codes, no consent, no refresh tokens, no key rotation.
It exists so the authorization-code + PKCE flow can be run and broken offline. Real equivalent: Keycloak.
"""
import base64
import hashlib
import hmac
import json
import secrets
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from jwt_hs256 import sign


def s256(verifier: str) -> str:  # PKCE: BASE64URL-ENCODE(SHA256(ASCII(code_verifier)))
    return base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest()).rstrip(b"=").decode()


class MockIdP:
    def __init__(self, clients, user="member-m1", code_ttl=60, token_ttl=300, clock=time.time):
        self.clients, self.user, self.code_ttl, self.token_ttl, self.clock = clients, user, code_ttl, token_ttl, clock
        self.codes = {}
        self.overrides = {}  # learning knob: claims to tamper with in the next ID token (tests, try_it)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), _handler(self))
        self.issuer = f"http://127.0.0.1:{self.server.server_port}"  # a real issuer MUST use https

    def __enter__(self):
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()

    def discovery(self):
        return {"issuer": self.issuer, "authorization_endpoint": f"{self.issuer}/authorize",
                "token_endpoint": f"{self.issuer}/token", "response_types_supported": ["code"],
                "subject_types_supported": ["public"], "id_token_signing_alg_values_supported": ["HS256"],
                "code_challenge_methods_supported": ["S256"],
                "token_endpoint_auth_methods_supported": ["client_secret_post"]}

    def authorize(self, q):
        client = self.clients.get(q.get("client_id"))
        if not client or q.get("redirect_uri") not in client["redirect_uris"]:  # exact match, else never redirect
            return 400, {"error": "invalid_request", "error_description": "unknown client or redirect_uri"}
        error = ("unsupported_response_type" if q.get("response_type") != "code" else
                 "invalid_scope" if "openid" not in q.get("scope", "").split() else
                 "invalid_request" if q.get("code_challenge_method") != "S256" or not q.get("code_challenge") else None)
        params = {"error": error} if error else {"code": self._new_code(q)}
        params["state"] = q.get("state", "")
        return 302, q["redirect_uri"] + "?" + urllib.parse.urlencode(params)

    def _new_code(self, q):
        code = secrets.token_urlsafe(32)
        self.codes[code] = {"client_id": q["client_id"], "redirect_uri": q["redirect_uri"], "nonce": q.get("nonce"),
                            "challenge": q["code_challenge"], "auth_time": int(self.clock()),
                            "expires": self.clock() + self.code_ttl}
        return code

    def token(self, form):
        client = self.clients.get(form.get("client_id"))
        if not client or not hmac.compare_digest(form.get("client_secret", ""), client["secret"]):
            return 401, {"error": "invalid_client"}
        grant = self.codes.pop(form.get("code", ""), None)  # pop: a code works exactly once
        if form.get("grant_type") != "authorization_code" or grant is None:
            return 400, {"error": "invalid_grant", "error_description": "code unknown or already used"}
        if grant["expires"] < self.clock() or grant["client_id"] != form["client_id"] \
                or grant["redirect_uri"] != form.get("redirect_uri"):
            return 400, {"error": "invalid_grant", "error_description": "code expired or issued to another client"}
        if not hmac.compare_digest(s256(form.get("code_verifier", "")), grant["challenge"]):
            return 400, {"error": "invalid_grant", "error_description": "PKCE verification failed"}
        now = int(self.clock())
        claims = {"iss": self.issuer, "sub": self.user, "aud": form["client_id"], "exp": now + self.token_ttl,
                  "iat": now, "auth_time": grant["auth_time"], "nonce": grant["nonce"], "name": "Ada Member"}
        claims.update(self.overrides)
        return 200, {"access_token": secrets.token_urlsafe(32), "token_type": "Bearer",
                     "expires_in": self.token_ttl, "id_token": sign(claims, client["secret"])}


def _handler(idp):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            url = urllib.parse.urlsplit(self.path)
            if url.path == "/.well-known/openid-configuration":
                return self._json(200, idp.discovery())
            if url.path == "/authorize":
                status, result = idp.authorize(dict(urllib.parse.parse_qsl(url.query)))
                if status == 302:
                    self.send_response(302)
                    self.send_header("Location", result)
                    self.send_header("Content-Length", "0")
                    return self.end_headers()
                return self._json(status, result)
            self._json(404, {"error": "not_found"})

        def do_POST(self):
            if self.path != "/token":
                return self._json(404, {"error": "not_found"})
            body = self.rfile.read(int(self.headers.get("Content-Length", 0))).decode("utf-8")
            self._json(*idp.token(dict(urllib.parse.parse_qsl(body))))

        def _json(self, status, payload):
            data = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *args):
            pass

    return Handler
