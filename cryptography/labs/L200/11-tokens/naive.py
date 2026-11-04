"""ANTI-PATTERN for the demo only: the token header picks the algorithm, one key serves every algorithm.
This is the bug class behind the 'alg:none' and RS256->HS256 key-confusion attacks (RFC 8725 section 2.1)."""
import hmac
import json

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from tokens import _hs256, unb64u


def naive_verify(token: str, key_bytes: bytes) -> dict:
    """DON'T DO THIS: lets the token's header pick the algorithm, with one key for every algorithm."""
    h, p, s = token.split(".")
    alg = json.loads(unb64u(h))["alg"]
    if alg == "HS256" and not hmac.compare_digest(_hs256(key_bytes, f"{h}.{p}".encode()), unb64u(s)):
        raise ValueError("bad signature")
    if alg == "EdDSA":
        Ed25519PublicKey.from_public_bytes(key_bytes).verify(unb64u(s), f"{h}.{p}".encode())
    return json.loads(unb64u(p))  # alg "none" falls straight through to here
