"""Wire format: 2-byte header length | JSON header | blobs. The header names every algorithm and blob length,
so a receiver follows the registry instead of guessing (the versioned-envelope idea of cryptography L400 #17).
Tap records each flight the way a packet capture would - it sees bytes, never intentions."""
import json
import struct

VERSION = 2


def encode(header, *blobs):
    h = dict(header, v=VERSION, lens=[len(b) for b in blobs])
    raw = json.dumps(h, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return struct.pack(">H", len(raw)) + raw + b"".join(blobs)


def decode(data):
    n = struct.unpack(">H", data[:2])[0]
    header = json.loads(data[2:2 + n].decode("utf-8"))
    blobs, pos = [], 2 + n
    for length in header["lens"]:
        blobs.append(data[pos:pos + length])
        pos += length
    if pos != len(data):
        raise ValueError("trailing or missing bytes")
    return header, blobs


class Tap:
    def __init__(self):
        self.flights = []

    def record(self, service, direction, data):
        header, blobs = decode(data)
        self.flights.append({"service": service, "dir": direction, "t": header["t"], "bytes": len(data),
                             "groups": header.get("groups"), "group": header.get("group"), "sig": header.get("sig"),
                             "blob_bytes": [len(b) for b in blobs]})


class Network:
    """Carries bytes between a client and a server object and lets the tap see every flight."""

    def __init__(self, tap=None):
        self.tap = tap or Tap()

    def roundtrip(self, service, server, data):
        self.tap.record(service, "c2s", data)
        reply = server.respond(data)
        self.tap.record(service, "s2c", reply)
        return reply
