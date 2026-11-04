"""Messaging servers for the mixed-version rollout: v1 negotiates X25519 only, v2 prefers X25519MLKEM768.

The server picks the first of ITS groups that the client offered (TLS 1.3 style) and signs the transcript with the
service's signature policy. Driving side = wire bytes in, wire bytes out; driven side = the registry's adapters.
"""
import hashlib

import crypto_registry as registry
import wire


class Server:
    def __init__(self, name, version, service="messaging"):
        self.name, self.version, self.service = name, version, service
        self.groups = registry.server_groups(version)
        self.sig = registry.signer(service, role="server")
        self.sk, self.pk = self.sig.keygen()
        self.key, self.received = None, []

    def respond(self, data):
        header, blobs = wire.decode(data)
        if header["t"] == "data":
            return self._open(header, blobs)
        offered = dict(zip(header["groups"], blobs))
        chosen = next((g for g in self.groups if g in offered), None)
        if chosen is None:
            return wire.encode({"t": "alert", "alert": "handshake_failure: no common group"})
        if self.version >= 2 and registry.pq_required(self.service) and not registry.KEX[chosen].pq:
            return wire.encode({"t": "alert", "alert": "insufficient_security: post-quantum key exchange required"})
        server_share, self.key = registry.kex(chosen, self.service, role="server").server_respond(offered[chosen])
        signature = self.sig.sign(self.sk, hashlib.sha256(data + server_share).digest())
        return wire.encode({"t": "server_hello", "group": chosen, "sig": self.sig.id}, server_share, signature)

    def _open(self, header, blobs):
        nonce, sealed = blobs
        self.received.append(registry.AEAD[header["aead"]].open(self.key, nonce, sealed))
        return wire.encode({"t": "ack"})


def make_fleet(versions, service="messaging"):
    return [Server(f"{service}-{i}", v, service) for i, v in enumerate(versions)]


def run_traffic(channel, servers, messages_per_server=2, network=None):
    """Send messages to every server; returns per-group session counts, refusals and the tap."""
    network = network or wire.Network()
    stats = {"sessions": {}, "refused": 0, "delivered": 0, "results": []}
    for server in servers:
        for i in range(messages_per_server):
            try:
                res = channel.send(network, server, server.pk, f"msg {i} to {server.name}".encode("utf-8"))
            except channel.Refused as exc:
                stats["refused"] += 1
                stats["results"].append({"server": server.name, "refused": str(exc)})
                continue
            stats["sessions"][res["group"]] = stats["sessions"].get(res["group"], 0) + 1
            stats["delivered"] += res["delivered"]
            stats["results"].append({"server": server.name, **res})
    stats["tap"] = network.tap
    return stats


FOLDERS = {"migrated": "migrated/messaging", "bypass": "faults/messaging_bypass", "downgrade": "faults/messaging_downgrade"}


def load_channel(variant="migrated"):
    import _kb
    return _kb.load_file(registry.HERE / FOLDERS[variant] / "channel.py", f"messaging_channel_{variant}")
