"""Minimal JWS compact serialization with HS256 (HMAC-SHA256), stdlib only. Learning code: use a library in production."""
import base64
import hashlib
import hmac
import json


class InvalidToken(Exception):
    pass


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")  # base64url without padding


def b64url_decode(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def sign(claims: dict, key: str, header=None) -> str:
    header = header or {"alg": "HS256", "typ": "JWT"}
    signing_input = f"{b64url(json.dumps(header).encode())}.{b64url(json.dumps(claims).encode())}"
    mac = hmac.new(key.encode("utf-8"), signing_input.encode("ascii"), hashlib.sha256).digest()
    return f"{signing_input}.{b64url(mac)}"


def verify(token: str, key: str, allowed_algs=("HS256",)):
    """Return (header, claims) or raise InvalidToken. The alg comes from OUR allow-list, not from the token."""
    try:
        head_b64, body_b64, sig_b64 = token.split(".")
        header = json.loads(b64url_decode(head_b64))
        claims = json.loads(b64url_decode(body_b64))
    except ValueError as exc:
        raise InvalidToken(f"malformed token: {exc}") from exc
    if header.get("alg") not in allowed_algs:  # rejects 'none' and algorithm-switching tricks
        raise InvalidToken(f"alg {header.get('alg')!r} not allowed (expected one of {list(allowed_algs)})")
    expected = hmac.new(key.encode("utf-8"), f"{head_b64}.{body_b64}".encode("ascii"), hashlib.sha256).digest()
    if not hmac.compare_digest(expected, b64url_decode(sig_b64)):  # constant-time comparison
        raise InvalidToken("signature does not match")
    return header, claims
