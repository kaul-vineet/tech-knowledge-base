"""SEEDED FAULT (failure lab, --inject bypass): a "latency fast path" added during an incident.

Key exchange loads the curve module named in a config string and skips the registry; signature checking and AEAD
still go through the registry, so the file looks compliant. The AST inventory and the agility lint both pass it.
Only the runtime wire contract (tests/test_seam_wire_contract.py) sees that messaging now negotiates X25519 alone.
"""
import hashlib
import importlib
import os

import crypto_registry as registry
import wire
from adapters import derive

SERVICE = "messaging"
FASTPATH = os.environ.get("MSG_FASTPATH_MODULE", "cryptography.hazmat.primitives.asymmetric.x25519")


class Refused(Exception):
    """The handshake is aborted instead of continuing with weaker protection."""


def _fast():
    mod = importlib.import_module(FASTPATH)
    stem = mod.__name__.rsplit(".", 1)[1].upper()
    return getattr(mod, stem + "PrivateKey"), getattr(mod, stem + "PublicKey"), stem


def send(network, server, pinned_pk, message):
    private_cls, public_cls, group = _fast()
    sk = private_cls.generate()
    share = sk.public_key().public_bytes_raw()
    hello = wire.encode({"t": "client_hello", "service": SERVICE, "groups": [group]}, share)
    reply = network.roundtrip(SERVICE, server, hello)
    header, blobs = wire.decode(reply)
    if header["t"] != "server_hello":
        raise Refused(header.get("alert", "unexpected message"))
    server_share, signature = blobs
    if not registry.verifier(SERVICE, header["sig"]).verify(pinned_pk, signature, hashlib.sha256(hello + server_share).digest()):
        raise Refused("bad transcript signature")
    key = derive(sk.exchange(public_cls.from_public_bytes(server_share)), share, server_share)
    aead, nonce = registry.aead(SERVICE), os.urandom(12)
    record = wire.encode({"t": "data", "aead": aead.id}, nonce, aead.seal(key, nonce, message))
    network.roundtrip(SERVICE, server, record)
    return {"group": header["group"], "pq": False, "client_flight": len(hello), "server_flight": len(reply),
            "delivered": int(server.received[-1] == message)}
