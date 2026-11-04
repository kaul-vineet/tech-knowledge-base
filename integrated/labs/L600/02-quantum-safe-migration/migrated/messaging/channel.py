"""Messaging v2 (migrated): every algorithm comes from the registry through ports - none is named in this file.

Client side of the handshake: offer what the registry says, verify the server's signature over the transcript with
the pinned key, refuse a classical group when the service requires PQ, then send one AEAD-sealed message.
"""
import hashlib
import os

import crypto_registry as registry
import wire

SERVICE = "messaging"


class Refused(Exception):
    """The handshake is aborted instead of continuing with weaker protection."""


def send(network, server, pinned_pk, message):
    states, shares = {}, []
    for kex in registry.kex_offers(SERVICE):
        states[kex.id], share = kex.client_hello()
        shares.append(share)
    hello = wire.encode({"t": "client_hello", "service": SERVICE, "groups": list(states)}, *shares)
    reply = network.roundtrip(SERVICE, server, hello)
    header, blobs = wire.decode(reply)
    if header["t"] != "server_hello":
        raise Refused(header.get("alert", "unexpected message"))
    group = header["group"]
    if group not in states:
        raise Refused(f"server chose {group}, which we did not offer")
    kex = registry.kex(group, SERVICE)
    if registry.pq_required(SERVICE) and not kex.pq:
        raise Refused(f"{group} is classical-only and {SERVICE} requires post-quantum key exchange")
    server_share, signature = blobs
    if not registry.verifier(SERVICE, header["sig"]).verify(pinned_pk, signature, hashlib.sha256(hello + server_share).digest()):
        raise Refused("bad transcript signature")
    key = kex.client_finish(states[group], server_share)
    aead, nonce = registry.aead(SERVICE), os.urandom(12)
    record = wire.encode({"t": "data", "aead": aead.id}, nonce, aead.seal(key, nonce, message))
    network.roundtrip(SERVICE, server, record)
    return {"group": group, "pq": kex.pq, "client_flight": len(hello), "server_flight": len(reply),
            "delivered": int(server.received[-1] == message)}
