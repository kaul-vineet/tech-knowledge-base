"""Build-task solution: no silent fallback. The client accepts exactly the share the negotiated group defines
(RFC 10024: the client MUST check the ciphertext length and abort with illegal_parameter). Classical-only is a
separate, explicitly configured group - never a reaction to a malformed or truncated share."""
import json

from pq_hybrid import (GROUP, MLKEM_CT, X_LEN, HandshakeError, client_hello, derive, harvest_then_break,  # noqa: F401
                       server_respond, x25519)

POLICY = {"group": GROUP, "allow_classical": False}


def client_finish(st: dict, server_share: bytes):
    if len(server_share) != MLKEM_CT + X_LEN:
        print(json.dumps({"event": "handshake_abort", "alert": "illegal_parameter", "share_bytes": len(server_share)}))
        raise HandshakeError(f"illegal_parameter: {POLICY['group']} server share must be {MLKEM_CT + X_LEN} bytes, got {len(server_share)}")
    ss_pq = st["mlkem"].decapsulate(server_share[:MLKEM_CT])
    ss_x = st["x"].exchange(x25519.X25519PublicKey.from_public_bytes(server_share[MLKEM_CT:]))
    return derive(ss_pq + ss_x, st["share"], server_share), POLICY["group"]


if __name__ == "__main__":
    st, ch = client_hello()
    sh, k_server = server_respond(ch)
    key, mode = client_finish(st, sh)
    print("normal:", mode, "| keys match:", key == k_server)
    st, ch = client_hello()
    sh, _ = server_respond(ch)
    for cut in (X_LEN, X_LEN + 1):
        try:
            client_finish(st, sh[-cut:])
        except HandshakeError as e:
            print(f"downgraded {cut}-byte share: refused ({e})")
