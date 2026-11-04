"""Demo: one login with the authorization code flow + PKCE against the LEARNING-ONLY mock IdP. Run: python app.py"""
import secrets
import urllib.parse

from mock_idp import MockIdP
from rp_client import LoginFailed, RelyingParty, browser_follow

REDIRECT = "http://127.0.0.1:8400/callback"  # never opened: browser_follow stops at the redirect


def query(url):
    return dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query))


def start(**idp_options):
    """Start the mock IdP with one registered client and an RP configured for it."""
    secret = secrets.token_urlsafe(32)
    idp = MockIdP({"library-web": {"secret": secret, "redirect_uris": [REDIRECT]}}, **idp_options).__enter__()
    return idp, RelyingParty(idp.issuer, "library-web", secret, REDIRECT)


if __name__ == "__main__":
    idp, rp = start()
    try:
        url, login = rp.start_login()
        print("mock IdP (LEARNING ONLY) at http://127.0.0.1:<port>")
        print("1 authorize request ->", sorted(query(url)))
        callback = browser_follow(url)
        print(f"2 redirect to RP    -> code of {len(query(callback)['code'])} chars, state matches: "
              f"{query(callback)['state'] == login.state}")
        claims = rp.finish_login(callback, login)
        print(f"3 ID token accepted -> sub={claims['sub']} aud={claims['aud']} nonce ok, "
              f"valid {claims['exp'] - claims['iat']} s")
        try:
            rp.finish_login(callback, login)
        except LoginFailed as exc:
            print(f"4 same code again   -> LoginFailed: {exc}")
    finally:
        idp.__exit__(None, None, None)
