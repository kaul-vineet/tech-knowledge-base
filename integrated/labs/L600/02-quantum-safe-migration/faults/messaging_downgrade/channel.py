"""SEEDED FAULT (--inject downgrade): a "compatibility shim" for the mixed-version rollout.

When the registry stops offering the classical group (pq_required on), this client adds it back so that v1 servers
keep working - and it no longer refuses a classical server choice. Messages still flow: a silent downgrade that
only the rollout<->policy seam test (tests/test_seam_rollout_downgrade.py) notices.
"""
import hashlib
import os

import crypto_registry as registry
import wire

SERVICE = "messaging"


class Refused(Exception):
    """The handshake is aborted instead of continuing with weaker protection."""


def send(network, server, pinned_pk, message):
    offers = registry.kex_offers(SERVICE)
    if all(k.pq for k in offers):
        offers.append(registry.classic_fallback(SERVICE))          # "keep v1 servers working"
    states, shares = {}, []
    for kex in offers:
        states[kex.id], share = kex.client_hello()
        shares.append(share)
    hello = wire.encode({"t": "client_hello", "service": SERVICE, "groups": list(states)}, *shares)
    reply = network.roundtrip(SERVICE, server, hello)
    header, blobs = wire.decode(reply)
    if header["t"] != "server_hello":
        raise Refused(header.get("alert", "unexpected message"))
    group = header["group"]
    kex = registry.kex(group, SERVICE)
    server_share, signature = blobs
    if not registry.verifier(SERVICE, header["sig"]).verify(pinned_pk, signature, hashlib.sha256(hello + server_share).digest()):
        raise Refused("bad transcript signature")
    key = kex.client_finish(states[group], server_share)
    aead, nonce = registry.aead(SERVICE), os.urandom(12)
    record = wire.encode({"t": "data", "aead": aead.id}, nonce, aead.seal(key, nonce, message))
    network.roundtrip(SERVICE, server, record)
    return {"group": group, "pq": kex.pq, "client_flight": len(hello), "server_flight": len(reply),
            "delivered": int(server.received[-1] == message)}
