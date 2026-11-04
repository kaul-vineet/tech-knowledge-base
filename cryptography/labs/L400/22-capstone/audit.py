"""Signed, hash-chained audit log (format "audit-v1") and deterministic anomaly rules.
Each entry carries the SHA-256 of the previous entry, and the hash of the entry itself is signed through a token
handle (lesson 19), so editing, deleting or reordering entries is detectable by anyone holding the public key.
The rules below DECIDE what is anomalous; an agent may only explain them (agent_explain.py)."""
import base64
import hashlib
import json

GENESIS = "0" * 64
BURST_LIMIT, BURST_WINDOW_S = 5, 60  # more than 5 key unwraps for one user within 60 s is a burst


class FakeClock:
    def __init__(self, start: float = 1_800_000_000.0):
        self.t = start

    def now(self) -> float:
        return self.t

    def advance(self, seconds: float):
        self.t += seconds


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


class AuditLog:
    def __init__(self, signer, clock):
        self.entries, self.signer, self.clock = [], signer, clock  # signer.sign(bytes) -> bytes (token handle)

    def append(self, actor: str, op: str, obj: str, **extra) -> dict:
        prev = entry_hash(self.entries[-1]) if self.entries else GENESIS
        e = {"seq": len(self.entries) + 1, "ts": self.clock.now(), "actor": actor, "op": op, "obj": obj, "prev": prev, **extra}
        e["sig"] = base64.b64encode(self.signer.sign(bytes.fromhex(entry_hash(e)))).decode()
        self.entries.append(e)
        return e

    def lines(self) -> list:
        return [json.dumps(e, sort_keys=True) for e in self.entries]


def entry_hash(e: dict) -> str:
    return hashlib.sha256(canon({k: v for k, v in e.items() if k != "sig"})).hexdigest()


def verify_chain(entries: list, public_key) -> list:
    """Integrity problems: wrong signature, broken chain, missing or reordered sequence numbers."""
    problems, prev, expected = [], GENESIS, 1
    for e in entries:
        if e["seq"] != expected:  # deleted or reordered entries
            problems.append({"rule": "seq_gap", "seq": e["seq"], "summary": f"expected seq {expected}, found {e['seq']}"})
        expected = e["seq"] + 1
        if e["prev"] != prev:
            problems.append({"rule": "chain_break", "seq": e["seq"], "summary": "prev hash does not match the entry before"})
        try:
            public_key.verify(base64.b64decode(e["sig"]), bytes.fromhex(entry_hash(e)))
        except Exception:
            problems.append({"rule": "bad_signature", "seq": e["seq"], "summary": "entry content does not match its signature"})
        prev = entry_hash(e)
    return problems


def detect(entries: list, public_key) -> list:
    """All anomalies, numbered A1, A2, ... : integrity first, then behaviour rules."""
    found = verify_chain(entries, public_key)
    revoked, unwraps, last_ts = {}, {}, None
    for e in entries:
        user = e["actor"].split("/")[-1]
        if last_ts is not None and e["ts"] < last_ts:
            found.append({"rule": "clock_backwards", "seq": e["seq"], "summary": f"ts {e['ts']} before {last_ts}"})
        last_ts = max(last_ts or e["ts"], e["ts"])
        if e["op"] == "doc.revoke":
            revoked[e["obj"]] = e["ts"]
        if e["op"] == "doc.get" and user in revoked and e.get("result") == "ok":
            found.append({"rule": "access_after_revoke", "seq": e["seq"], "summary": f"{user} read {e['obj']} after revocation"})
        if e["op"] == "kms.unwrap":
            recent = [t for t in unwraps.get(user, []) if e["ts"] - t <= BURST_WINDOW_S] + [e["ts"]]
            unwraps[user] = recent
            if len(recent) == BURST_LIMIT + 1:  # report once, when the limit is first exceeded
                found.append({"rule": "unwrap_burst", "seq": e["seq"], "summary": f"{user}: {len(recent)} unwraps in {BURST_WINDOW_S} s"})
    found.sort(key=lambda a: a["seq"])
    return [{"id": f"A{i}", **a} for i, a in enumerate(found, start=1)]
