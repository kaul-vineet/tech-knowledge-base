"""JWT-style signed tokens: algorithm allow-list, one key per algorithm, exp/nbf/aud (RFC 7519, RFC 8725 BCP).
FOR LEARNING ONLY - not for production. In real services use a maintained library (e.g. PyJWT) configured the same way."""
import base64
import hashlib
import hmac
import json
import time

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


class TokenError(Exception):
    pass


def b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def unb64u(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _hs256(key: bytes, msg: bytes) -> bytes:
    return hmac.new(key, msg, hashlib.sha256).digest()


def sign(claims: dict, alg: str, key) -> str:
    seg = [b64u(json.dumps(x, separators=(",", ":")).encode()) for x in ({"alg": alg, "typ": "JWT"}, claims)]
    msg = ".".join(seg).encode()  # the signature covers header AND payload
    sig = _hs256(key, msg) if alg == "HS256" else key.sign(msg)  # HS256 = shared secret, EdDSA = private key
    return ".".join(seg + [b64u(sig)])


def verify(token: str, keys: dict, audience: str, now=None, leeway=30) -> dict:
    """keys = the allow-list: exactly one key per accepted algorithm, e.g. {"EdDSA": public_key}."""
    try:
        h, p, s = token.split(".")
        alg = json.loads(unb64u(h)).get("alg")
    except ValueError as e:
        raise TokenError("malformed token") from e
    if alg not in keys:  # algorithm allow-list: rejects "none" and any alg we did not configure
        raise TokenError(f"algorithm {alg!r} not allowed")
    key, msg, sig = keys[alg], f"{h}.{p}".encode(), unb64u(s)
    if alg == "HS256" and not hmac.compare_digest(_hs256(key, msg), sig):  # constant-time compare
        raise TokenError("bad signature")
    if alg == "EdDSA":
        try:
            key.verify(sig, msg)
        except InvalidSignature:
            raise TokenError("bad signature") from None
    claims = json.loads(unb64u(p))  # trust claims only AFTER the signature check
    now = time.time() if now is None else now
    if "exp" not in claims or now > claims["exp"] + leeway:  # exp required; small leeway for clock skew
        raise TokenError("expired or no exp")
    if now + leeway < claims.get("nbf", 0):
        raise TokenError("not yet valid (nbf)")
    if audience not in (claims.get("aud") if isinstance(claims.get("aud"), list) else [claims.get("aud")]):
        raise TokenError("wrong audience")  # a token minted for another service is not for us
    return claims


if __name__ == "__main__":
    from naive import naive_verify  # the anti-pattern, kept in its own file

    issuer = Ed25519PrivateKey.generate()
    pub = issuer.public_key()
    keys = {"EdDSA": pub}  # this API accepts EdDSA only
    now = int(time.time())  # NumericDate: seconds since the epoch
    good = sign({"sub": "alice", "aud": "orders-api", "exp": now + 300, "role": "user"}, "EdDSA", issuer)
    print("valid token:", verify(good, keys, "orders-api")["sub"], f"({len(good)} chars)")

    forged_claims = {"sub": "alice", "aud": "orders-api", "exp": now + 300, "role": "admin"}
    none_tok = ".".join([b64u(b'{"alg":"none","typ":"JWT"}'), b64u(json.dumps(forged_claims).encode()), ""])
    confused = sign(forged_claims, "HS256", pub.public_bytes_raw())  # attacker HMACs with the PUBLIC key
    cases = [("alg none", none_tok), ("key confusion", confused),
             ("expired", sign({"aud": "orders-api", "exp": now - 3600}, "EdDSA", issuer)),
             ("wrong audience", sign({"aud": "billing-api", "exp": now + 300}, "EdDSA", issuer)),
             ("payload edited", good.split(".")[0] + "." + b64u(json.dumps(forged_claims).encode()) + "." + good.split(".")[2])]
    for label, tok in cases:
        try:
            naive = "ACCEPTS role=" + naive_verify(tok, pub.public_bytes_raw()).get("role", "?")
        except (ValueError, InvalidSignature):
            naive = "rejects"
        try:
            verify(tok, keys, "orders-api")
            safe = "ACCEPTS"
        except TokenError as e:
            safe = f"rejects ({e})"
        print(f"{label:<15} naive {naive:<18} | safe {safe}")
