"""Tamper-evident audit log: a SHA-256 hash chain of small headers + separately stored bodies + signed checkpoints.

entry.hash = SHA-256(prev_hash || canonical(entry without 'hash')); the header pins body_sha256, so a body can be
ERASED for retention/privacy (header stays, chain still verifies) but never silently CHANGED. A signed checkpoint
(seq, head hash) held outside the log catches truncation and a rewritten chain (Crosby & Wallach 2009 discuss why).
Never logged: tokens (only their id + fingerprint), x-sensitive fields (hash + length), secret-looking strings.
"""
import base64
import hashlib
import json
import re

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from manifest import canonical

GENESIS = "0" * 64
SECRET = re.compile(r"sk-[A-Za-z0-9-]{8,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----")
AUDIT_SEED = hashlib.sha256(b"L600-08 demo audit checkpoint key - never seed a real key").digest()  # DEMO ONLY


def audit_key():
    return Ed25519PrivateKey.from_private_bytes(AUDIT_SEED)


def fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def scrub(value):
    if isinstance(value, str):
        return SECRET.sub("[REDACTED]", value)
    if isinstance(value, dict):
        return {k: scrub(v) for k, v in value.items()}
    if isinstance(value, list):
        return [scrub(v) for v in value]
    return value


def redact_args(args, schema):
    """x-sensitive fields -> {sha256, len}; everything else scrubbed for secret patterns."""
    props = (schema or {}).get("properties", {})
    out = {}
    for k, v in args.items():
        if props.get(k, {}).get("x-sensitive") and isinstance(v, str):
            out[k] = {"sha256": fingerprint(v), "len": len(v)}
        else:
            out[k] = scrub(v)
    return out


class AuditLog:
    def __init__(self, clock, redact=True):
        self.clock, self.redact, self.entries, self.bodies = clock, redact, [], {}

    def append(self, event, actor, body):
        body = scrub(body) if self.redact else body  # seeded fault 'log-raw-args' turns this off
        raw = canonical(body)
        head = {"seq": len(self.entries) + 1, "ts": int(self.clock()), "event": event, "actor": actor,
                "prev": self.entries[-1]["hash"] if self.entries else GENESIS,
                "body_sha256": hashlib.sha256(raw).hexdigest()}
        head["hash"] = hashlib.sha256((head["prev"] + canonical(head).decode("utf-8")).encode("utf-8")).hexdigest()
        self.entries.append(head)
        self.bodies[head["seq"]] = body
        return head

    def checkpoint(self, key):
        last = self.entries[-1] if self.entries else {"seq": 0, "hash": GENESIS}
        msg = canonical({"seq": last["seq"], "head": last["hash"]})
        return {"seq": last["seq"], "head": last["hash"], "sig": base64.b64encode(key.sign(msg)).decode()}

    def purge_bodies(self, before_ts):
        """Retention: drop bodies older than before_ts; headers (and the chain) stay."""
        gone = [e["seq"] for e in self.entries if e["ts"] < before_ts and e["seq"] in self.bodies]
        for seq in gone:
            del self.bodies[seq]
        return gone

    def text(self):
        return "\n".join(json.dumps({**e, "body": self.bodies.get(e["seq"])}, sort_keys=True) for e in self.entries)


def verify(entries, bodies, checkpoint, pub, chained=True):
    """Returns a list of problems (empty = intact). chained=False is the seeded fault 'per-entry-hash'."""
    problems, prev = [], GENESIS
    for i, e in enumerate(entries, start=1):
        head = {k: v for k, v in e.items() if k != "hash"}
        if hashlib.sha256((e.get("prev", "") + canonical(head).decode("utf-8")).encode("utf-8")).hexdigest() != e.get("hash"):
            problems.append(f"seq {e.get('seq')}: hash mismatch")
        if chained and (e.get("prev") != prev or e.get("seq") != i):
            problems.append(f"position {i}: broken link")
        body = bodies.get(e.get("seq"))
        if body is not None and hashlib.sha256(canonical(body)).hexdigest() != e.get("body_sha256"):
            problems.append(f"seq {e.get('seq')}: body changed")
        prev = e.get("hash")
    if chained:
        try:
            pub.verify(base64.b64decode(checkpoint["sig"]), canonical({"seq": checkpoint["seq"], "head": checkpoint["head"]}))
        except (InvalidSignature, ValueError, KeyError):
            problems.append("checkpoint signature invalid")
        last = entries[-1] if entries else {"seq": 0, "hash": GENESIS}
        if (last.get("seq"), last.get("hash")) != (checkpoint.get("seq"), checkpoint.get("head")):
            problems.append("head does not match the signed checkpoint")
    return problems
