"""The verifying client: trusts one root (shipped out of band) and nothing a mirror says without proof.
Order matters (TUF section 5): fixed start time -> root chain -> timestamp (signature, expiry = freeze, version =
rollback) -> release.json (hash from the timestamp, strict JCS, dual signature within its key window) -> every file
(length + SHA-256 + Merkle root) -> licence/attribution -> transparency log (STH signature, inclusion, consistency)."""
import hashlib
import json

import canonical as C
import merkle
import publisher
import trust
from _kb import INPUTS

Rejected = trust.Rejected


def verify_release(objects: dict, version: int, root: dict, honour_retired: bool = True) -> dict:
    """Everything except freshness: used for old releases and by the tamper fitness function."""
    raw = objects.get(f"releases/v{version}/release.json")
    if raw is None:
        raise Rejected(f"v{version}: release.json missing")
    try:
        env = C.loads_strict(raw)
    except (ValueError, UnicodeDecodeError) as e:
        raise Rejected(f"v{version}: release.json not canonical JSON ({type(e).__name__})") from None
    trust.require_release(env, root, honour_retired)
    m = env["signed"]
    if m.get("_type") != "release" or m["version"] != version:
        raise Rejected(f"release.json is {m.get('_type')} v{m['version']}, asked for v{version}")
    for path, meta in m["files"].items():
        b = objects.get(f"releases/v{version}/{path}")
        if b is None or len(b) != meta["length"] or hashlib.sha256(b).hexdigest() != meta["sha256"]:
            raise Rejected(f"v{version}: {path} missing or changed")
    if merkle.mth(publisher.leaves(m["files"])).hex() != m["merkle_root"]:
        raise Rejected(f"v{version}: Merkle root mismatch")
    lic = objects[f"releases/v{version}/LICENSE.txt"].decode("utf-8").strip()
    ack = objects[f"releases/v{version}/ACKNOWLEDGEMENTS.md"].decode("utf-8")
    if lic != m["licence"] or publisher.licence_problems(lic) or any(i["credit"] not in ack for i in INPUTS.INPUTS):
        raise Rejected(f"v{version}: licence/attribution does not match the inputs' terms")
    return m


class Client:
    def __init__(self, root_env: dict, check_freshness: bool = True):
        self.root = root_env["signed"]  # shipped with the client (TUF 5.2)
        self.check_freshness = check_freshness
        self.seen_release, self.seen_ts, self.sth = 0, 0, None

    def update_root(self, chain: list) -> None:
        for env in chain[self.root["version"]:]:
            self.root = trust.next_root(self.root, env)

    def fetch(self, mirror, log, now: int) -> dict:
        if mirror.timestamp is None:
            raise Rejected(f"{mirror.name}: no timestamp")
        ts_env = C.loads_strict(mirror.timestamp)
        trust.require_role(ts_env, self.root, "timestamp")
        ts = ts_env["signed"]
        if self.check_freshness:
            if ts["expires"] <= now:
                raise Rejected(f"{mirror.name}: timestamp expired at {ts['expires']} (freeze attack or stale mirror)")
            if ts["version"] < self.seen_ts or ts["release"]["version"] < self.seen_release:
                raise Rejected(f"{mirror.name}: offers v{ts['release']['version']}, client has seen "
                               f"v{self.seen_release} (rollback)")
        v = ts["release"]["version"]
        raw = mirror.objects.get(f"releases/v{v}/release.json", b"")
        if hashlib.sha256(raw).hexdigest() != ts["release"]["sha256"]:
            raise Rejected(f"{mirror.name}: release.json v{v} does not match the timestamp")
        m = verify_release(mirror.objects, v, self.root)
        self._check_log(log, v, raw, now)
        self.seen_release, self.seen_ts = max(self.seen_release, v), max(self.seen_ts, ts["version"])
        return m

    def _check_log(self, log, v: int, raw: bytes, now: int) -> None:
        sth_env = log.sth(now)
        trust.require_role(sth_env, self.root, "log")
        sth = sth_env["signed"]
        e = publisher.tlog.entry(publisher.NAME, v, hashlib.sha256(raw).hexdigest())
        if e not in log.entries:
            raise Rejected(f"v{v} is not in the transparency log")
        i = log.index_of(e)
        path = [bytes.fromhex(h) for h in log.inclusion(i, sth["size"])]
        if not merkle.verify_inclusion(e, i, sth["size"], path, bytes.fromhex(sth["root"])):
            raise Rejected(f"v{v}: inclusion proof failed")
        if self.sth and self.sth["size"] < sth["size"]:
            proof = [bytes.fromhex(h) for h in log.consistency(self.sth["size"], sth["size"])]
            if not merkle.verify_consistency(self.sth["size"], sth["size"], bytes.fromhex(self.sth["root"]),
                                             bytes.fromhex(sth["root"]), proof):
                raise Rejected("log is not an extension of the tree head we saw before (history rewritten)")
        elif self.sth and (self.sth["size"] > sth["size"] or
                           (self.sth["size"] == sth["size"] and self.sth["root"] != sth["root"])):
            raise Rejected("log shrank or forked")
        self.sth = sth

    def fetch_any(self, mirrors: list, log, now: int):
        reasons = []
        for mr in mirrors:  # TUF 1.5.2: a bad mirror cannot stop updates from good mirrors
            try:
                return mr.name, self.fetch(mr, log, now), reasons
            except (Rejected, KeyError, json.JSONDecodeError, ValueError) as e:
                reasons.append(f"{mr.name}: {e}")
        raise Rejected("; ".join(reasons))
