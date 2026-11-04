"""Post-quantum key exchange in practice: X25519, ML-KEM-768 (FIPS 203) and the hybrid X25519MLKEM768 (RFC 10024).
A toy TLS-1.3-shaped exchange: the client sends a key share, the server answers with a share, both derive one key.
Shares and secret order follow RFC 10024: ML-KEM part first, then X25519 (1216 B client share, 1120 B server share)."""
import hashlib
import json
import random

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import mlkem, x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

SEED = 18  # seeds the injected fault (how the attacker rewrites the server share)
GROUP = "X25519MLKEM768"  # IANA TLS group 0x11EC (RFC 10024 section 7.1)
MLKEM_PK, MLKEM_CT, X_LEN = 1184, 1088, 32


class HandshakeError(Exception):
    """Abort the handshake (TLS: illegal_parameter alert) instead of continuing with weaker keys."""


def x_pub(k) -> bytes:
    return k.public_key().public_bytes_raw()


def derive(secret: bytes, client_share: bytes, server_share: bytes) -> bytes:
    transcript = hashlib.sha256(client_share + server_share).digest()  # bind the key to both shares
    return HKDF(hashes.SHA256(), 32, salt=None, info=b"kb-l18 hybrid" + transcript).derive(secret)


def client_hello():
    st = {"mlkem": mlkem.MLKEM768PrivateKey.generate(), "x": x25519.X25519PrivateKey.generate()}
    st["share"] = st["mlkem"].public_key().public_bytes_raw() + x_pub(st["x"])  # 1184 + 32 = 1216 bytes
    return st, st["share"]


def server_respond(client_share: bytes):
    if len(client_share) != MLKEM_PK + X_LEN:
        raise HandshakeError("illegal_parameter: client share length")
    ss_pq, ct = mlkem.MLKEM768PublicKey.from_public_bytes(client_share[:MLKEM_PK]).encapsulate()
    xk = x25519.X25519PrivateKey.generate()
    ss_x = xk.exchange(x25519.X25519PublicKey.from_public_bytes(client_share[MLKEM_PK:]))
    server_share = ct + x_pub(xk)  # 1088 + 32 = 1120 bytes
    return server_share, derive(ss_pq + ss_x, client_share, server_share)  # 64-byte hybrid secret, ML-KEM first


def client_finish(st: dict, server_share: bytes):
    """Returns (key, mode). mode tells which secrets protect the session."""
    if len(server_share) == MLKEM_CT + X_LEN:
        ss_pq = st["mlkem"].decapsulate(server_share[:MLKEM_CT])
        ss_x = st["x"].exchange(x25519.X25519PublicKey.from_public_bytes(server_share[MLKEM_CT:]))
        return derive(ss_pq + ss_x, st["share"], server_share), GROUP
    # BUG on purpose: "be liberal in what you accept" - silently fall back to classical X25519 only
    ss_x = st["x"].exchange(x25519.X25519PublicKey.from_public_bytes(server_share[-X_LEN:]))
    return derive(ss_x, st["share"], server_share), "X25519 (fallback)"


def harvest_then_break(st: dict, server_share: bytes, x_server=None) -> bytes:
    """A future quantum attacker recovers X25519 private keys from recorded traffic (Shor). Can it get the key?"""
    ss_x = st["x"].exchange(x25519.X25519PublicKey.from_public_bytes(server_share[-X_LEN:]))  # X25519 is broken
    return derive(ss_x, st["share"], server_share)  # but it has no ML-KEM shared secret


def sizes() -> dict:
    k = mlkem.MLKEM768PrivateKey.generate()
    k1024 = mlkem.MLKEM1024PrivateKey.generate()
    return {"X25519": {"client_share": 32, "server_share": 32, "secret": 32},
            "ML-KEM-768": {"client_share": len(k.public_key().public_bytes_raw()),
                           "server_share": len(k.public_key().encapsulate()[1]), "secret": 32},
            "ML-KEM-1024": {"client_share": len(k1024.public_key().public_bytes_raw()),
                            "server_share": len(k1024.public_key().encapsulate()[1]), "secret": 32},
            GROUP: {"client_share": MLKEM_PK + X_LEN, "server_share": MLKEM_CT + X_LEN, "secret": 64}}


if __name__ == "__main__":
    rng = random.Random(SEED)
    for name, s in sizes().items():
        print(json.dumps({"kem": name, **s, "on_wire": s["client_share"] + s["server_share"]}))
    st, ch = client_hello()
    sh, k_server = server_respond(ch)
    k_client, mode = client_finish(st, sh)
    print(f"1) hybrid handshake: client share {len(ch)} B, server share {len(sh)} B, keys match: {k_client == k_server}, mode: {mode}")
    print("2) quantum attacker with X25519 broken recovers the key:", harvest_then_break(st, sh) == k_client)
    print("--- fault: an on-path attacker rewrites the server share to its X25519 part only (downgrade)")
    st, ch = client_hello()
    sh, _ = server_respond(ch)
    cut = rng.choice([X_LEN, X_LEN + 1])  # seeded: keep only the classical share (or one stray byte)
    k_client, mode = client_finish(st, sh[-cut:])
    print(f"client accepted a {cut}-byte server share | mode: {mode} | quantum attacker recovers key:",
          harvest_then_break(st, sh[-cut:]) == k_client)
