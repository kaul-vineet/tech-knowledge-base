"""Mirrors and anti-entropy (distributed systems). Each mirror holds immutable release objects (key -> bytes) and the
newest timestamp it has seen. Anti-entropy is push-pull gossip with one random peer per round (Demers et al. 1987),
comparing a Merkle tree over 16 key buckets first and exchanging only differing buckets (Dynamo 4.7).
Rounds run on distributed-systems L400 #17's seeded event loop (Sim): simulated seconds, nothing sleeps.
A mirror built with encoder=... re-serialises JSON on ingest (the seeded platform fault); default stores bytes as-is."""
import hashlib
import json

import canonical as C
import merkle
from _kb import SIM

BUCKETS, PERIOD = 16, 60  # gossip round every 60 simulated seconds


def _digest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class Mirror:
    def __init__(self, name: str, encoder=None):
        self.name, self.encoder, self.objects, self.timestamp, self.conflicts = name, encoder, {}, None, set()

    def put(self, key: str, raw: bytes) -> None:
        if self.encoder and key.endswith(".json"):
            raw = self.encoder(json.loads(raw))  # 'normalise' through the local JSON stack: changes bytes, not values
        if key in self.objects and self.objects[key] != raw:
            self.conflicts.add(key)  # immutable keys never get overwritten; a conflict means somebody changed bytes
            return
        self.objects.setdefault(key, raw)

    def put_timestamp(self, raw: bytes) -> None:
        if self.timestamp is None or _ts_version(raw) > _ts_version(self.timestamp):
            self.timestamp = raw  # max-version register: a join, so gossip order does not matter

    def bucket_hashes(self) -> list:
        return bucket_hashes(self.objects)

    def root(self) -> bytes:
        return merkle.mth(self.bucket_hashes())


def _bucket(key: str) -> int:
    return int(_digest(key.encode())[:2], 16) % BUCKETS


def bucket_hashes(objects: dict) -> list:
    b = [[] for _ in range(BUCKETS)]
    for k, v in objects.items():
        b[_bucket(k)].append([k, _digest(v)])
    return [merkle.H(C.dumps(sorted(x))) for x in b]


def _ts_version(raw: bytes) -> int:
    return json.loads(raw)["signed"]["version"]


def pull(dst: Mirror, src_objects: dict, src_ts, stats: dict) -> None:
    """dst learns from a snapshot of a peer: roots first (1 hash), then 16 bucket hashes, then only the missing keys."""
    stats["messages"] += 1
    if src_ts and (dst.timestamp is None or _ts_version(src_ts) > _ts_version(dst.timestamp)):
        dst.put_timestamp(src_ts)
        stats["bytes"] += len(src_ts)
    mine, theirs = dst.bucket_hashes(), bucket_hashes(src_objects)
    if merkle.mth(mine) == merkle.mth(theirs):
        return
    stats["messages"] += 1
    for i in (i for i in range(BUCKETS) if mine[i] != theirs[i]):
        for k, v in src_objects.items():
            if _bucket(k) == i and dst.objects.get(k) != v:
                dst.put(k, v)
                stats["bytes"] += len(v)


def converged(mirrors: list) -> bool:
    return len({m.root() for m in mirrors}) == 1 and len({m.timestamp for m in mirrors}) == 1


def gossip(mirrors: list, seed: int, max_rounds: int = 20, down_until: dict = None) -> dict:
    """Synchronous push-pull rounds: every up mirror picks one random up peer; both learn what the other knew at the
    START of the round (exchanges in one round run concurrently). down_until: name -> first round it is reachable.
    rounds = round number (1-based) after which all mirrors agree; None if not within max_rounds."""
    sim, stats, down_until = SIM.Sim(seed), {"messages": 0, "bytes": 0, "rounds": None}, down_until or {}
    by_name = {m.name: m for m in mirrors}

    def round_(r):
        sim.down = {n for n, back in down_until.items() if r < back}
        up = [n for n in by_name if n not in sim.down]
        snap = {n: (dict(by_name[n].objects), by_name[n].timestamp) for n in up}
        for n in up:
            peer = sim.rng.choice([p for p in up if p != n] or [n])
            pull(by_name[n], *snap[peer], stats)  # pull
            pull(by_name[peer], *snap[n], stats)  # push
        if stats["rounds"] is None and not sim.down and converged(mirrors):
            stats["rounds"] = r + 1

    for r in range(max_rounds):
        sim.at(r * PERIOD, round_, r)
    sim.run(until=max_rounds * PERIOD)
    stats["converged"] = stats["rounds"] is not None
    return stats
