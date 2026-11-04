"""Macaroon-style capability tokens: chained HMAC-SHA256 over first-party caveats (Birgisson et al., NDSS 2014).

sig_0 = HMAC(root_key, id); sig_i = HMAC(sig_{i-1}, caveat_i). Anyone holding a token can ADD a caveat (attenuate)
without the key; nobody can remove one, because that would need the earlier signature. The verifier recomputes the
chain with the root key and then requires EVERY caveat to hold for this request - an unknown caveat fails (deny by default).
Caveat grammar: "<kind> <op> <value>", e.g. "tool in search_docs,save_memory", "arg read_file.path prefix docs/".
"""
import hashlib
import hmac
import json
import posixpath
import re
import secrets

import _kb

b64u, unb64u = _kb.load("tokens").b64u, _kb.load("tokens").unb64u  # base64url helpers from crypto L200 #11
MAX_TTL = 300  # seconds: a session token never lives longer than this
EMAIL = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")  # exactly ONE address, no lists


class CapabilityError(Exception):
    pass


def _mac(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _pack(ident, caveats, sig):
    return b64u(json.dumps({"id": ident, "c": caveats, "s": b64u(sig)}, separators=(",", ":")).encode("utf-8"))


def mint(root_key: bytes, ident: str, caveats) -> str:
    sig = _mac(root_key, ident)
    for c in caveats:
        sig = _mac(sig, c)
    return _pack(ident, list(caveats), sig)


def parse(token: str):
    try:
        d = json.loads(unb64u(token))
        return d["id"], list(d["c"]), unb64u(d["s"])
    except (ValueError, KeyError, TypeError):
        raise CapabilityError("malformed token") from None


def attenuate(token: str, caveat: str) -> str:
    ident, caveats, sig = parse(token)  # no root key needed: HMAC(sig, caveat) extends the chain
    return _pack(ident, caveats + [caveat], _mac(sig, caveat))


def _arg_ok(op, value, arg, normalize):
    if not isinstance(arg, str):
        return False
    if op == "prefix":
        path = posixpath.normpath(arg) if normalize else arg  # 'docs/../secrets/x' -> 'secrets/x'
        return not path.startswith(("/", "..")) and path.startswith(value)
    if op == "endswith":
        return (EMAIL.match(arg) is not None or not normalize) and arg.lower().endswith(value.lower())
    if op == "in":
        return arg in value.split(",")
    return False


def check_caveat(caveat, req, normalize=True):
    kind, op, value = (caveat.split(" ", 2) + ["", ""])[:3]
    if kind == "session" and op == "=":
        return req["session"] == value
    if kind == "expires" and op == "<":
        return req["now"] < int(value)
    if kind == "tool" and op == "in":
        return req["tool"] in value.split(",")
    if kind == "arg":
        tool, field = (op.split(".", 1) + [""])[:2]
        if tool != req["tool"]:
            return True  # this caveat constrains another tool
        rule_op, _, rule_value = value.partition(" ")
        return _arg_ok(rule_op, rule_value, req["args"].get(field), normalize)
    return None  # unknown caveat kind


def verify(token, root_key, req, extra=None, normalize=True):
    """req = {session, now, tool, args} built by the HOST. Returns the token id; raises CapabilityError."""
    ident, caveats, sig = parse(token)
    expect = _mac(root_key, ident)
    for c in caveats:
        expect = _mac(expect, c)
    if not hmac.compare_digest(expect, sig):  # constant-time compare
        raise CapabilityError("bad signature")
    for c in caveats:
        ok = check_caveat(c, req, normalize)
        if ok is None and extra:
            ok = extra(c, req)  # extension point (build task: the 'calls' caveat)
        if ok is not True:
            raise CapabilityError(f"caveat not satisfied: {c}" if ok is False else f"unknown caveat: {c}")
    return ident


class TokenService:
    """Mints one short-lived token per agent session, scoped to the tools (and argument shapes) of the task."""

    def __init__(self, clock, root_key=None, expiry=True):
        self.clock, self.root_key, self.expiry = clock, root_key or secrets.token_bytes(32), expiry

    def session_token(self, session, tools, ttl=60, arg_rules=()):
        if not 0 < ttl <= MAX_TTL:
            raise ValueError(f"ttl must be 1..{MAX_TTL} s")
        caveats = [f"session = {session}", f"tool in {','.join(tools)}", *arg_rules]
        if self.expiry:  # seeded fault 'no-expiry' drops this line
            caveats.insert(1, f"expires < {int(self.clock()) + ttl}")
        return mint(self.root_key, f"cap-{session}", caveats)


if __name__ == "__main__":
    t0 = 1_790_000_000
    svc = TokenService(lambda: t0, root_key=b"k" * 32)
    tok = svc.session_token("s-1", ["search_docs", "read_file"], ttl=60, arg_rules=["arg read_file.path prefix docs/"])
    req = {"session": "s-1", "now": t0 + 10, "tool": "read_file", "args": {"path": "docs/vpn-setup.md"}}
    print("caveats:", parse(tok)[1])
    print("verify ok:", verify(tok, svc.root_key, req))
    for name, r in [("traversal", {**req, "args": {"path": "docs/../secrets/api_key.txt"}}),
                    ("expired", {**req, "now": t0 + 60}), ("other tool", {**req, "tool": "send_email"})]:
        try:
            verify(tok, svc.root_key, r)
        except CapabilityError as e:
            print(f"{name}: {e}")
