"""Build-task solution: one-time tokens. Reject a token whose jti was already used (until it expires)."""
import time

import tokens


class ReplayGuard:
    def __init__(self):
        self.seen = {}  # jti -> exp; store in Redis/DB in a real multi-instance service

    def check(self, claims: dict, now: float) -> None:
        self.seen = {j: e for j, e in self.seen.items() if e >= now}  # forget expired ids (exp already blocks them)
        jti = claims.get("jti")
        if not jti:
            raise tokens.TokenError("missing jti")
        if jti in self.seen:
            raise tokens.TokenError("replayed token")
        self.seen[jti] = claims["exp"]


def verify_once(token: str, keys: dict, audience: str, guard: ReplayGuard, now=None) -> dict:
    now = time.time() if now is None else now
    claims = tokens.verify(token, keys, audience, now=now)  # signature, alg, exp/nbf/aud first
    guard.check(claims, now)
    return claims
