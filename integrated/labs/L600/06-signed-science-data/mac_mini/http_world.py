"""Experiment 1 - the release story with mirrors as separate processes and anti-entropy over real HTTP.

python mac_mini/http_world.py --here                    4 mirror processes, releases v1-v4, m3 killed during v4
python mac_mini/http_world.py --mirrors 8 --releases 40 the overnight size (more mirrors, more releases, more kills)
python mac_mini/http_world.py --here --inject float-format   m2 re-serialises JSON on ingest: must FAIL (exit 1)

Same publisher (publisher.Publisher: licence gate, Merkle manifest, Ed25519 + ML-DSA-65, transparency log, timestamp)
and the same verifying client (client.Client) as world.py; only the mirrors change: each one is mirror_server.py in
its own process with its own folder, and every gossip exchange is HTTP on 127.0.0.1 (GET /root, /bucket/i, /obj).
The publisher uploads to m0 only. Each round, every live mirror pulls from one seeded random live peer and that peer
pulls back (push-pull). During the last release the highest-numbered mirror is SIGKILLed before gossip and restarted
from its own disk two rounds later.
H1  every release converges on all mirrors (same Merkle root of the 16 buckets, same timestamp) within MAX_ROUNDS
H2  the client verifies the latest release from EVERY mirror over HTTP (signatures, files, Merkle root, log proofs)
H3  the killed mirror came back with every object it had stored before the kill (recovered from disk)
"""
import argparse
import json
import random
import shutil
import socket
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

import _mac
import client as CL
import mirror_server as MS
import publisher as P

MAX_ROUNDS, SPACING = 20, 1200


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class HttpMirror:
    """What client.Client.fetch needs (name, timestamp, objects) - read over HTTP from one mirror process."""

    def __init__(self, name, port):
        self.name = name
        ts = MS.get(port, "/timestamp")
        self.timestamp = ts
        self.objects = {}
        for i in range(16):
            for key in json.loads(MS.get(port, f"/bucket/{i}") or b"{}"):
                self.objects[key] = MS.get(port, "/obj?" + urllib.parse.urlencode({"key": key}))


class Fleet:
    def __init__(self, run_dir, n, inject):
        self.dir, self.inject = Path(run_dir), inject
        self.names = [f"m{i}" for i in range(n)]
        self.ports = {m: free_port() for m in self.names}
        self.procs = {}
        for m in self.names:
            self.start(m)

    def start(self, m):
        enc = "platform" if (self.inject == "float-format" and m == "m2") else "canonical"
        cmd = [sys.executable, str(Path(MS.__file__)), "--name", m, "--port", str(self.ports[m]), "--dir",
               str(self.dir), "--encoder", enc]
        self.dir.mkdir(parents=True, exist_ok=True)
        with open(self.dir / f"{m}.stderr", "ab") as err:
            self.procs[m] = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=err)
        for _ in range(1200):
            s = MS.get(self.ports[m], "/root", timeout=1)
            if s:
                return json.loads(s)
            if self.procs[m].poll() is not None:
                raise RuntimeError((self.dir / f"{m}.stderr").read_text(errors="replace")[-800:])
            time.sleep(0.05)
        raise RuntimeError(f"{m} did not start")

    def kill(self, m):
        self.procs[m].kill()
        self.procs[m].wait()

    def summaries(self, live):
        return {m: json.loads(MS.get(self.ports[m], "/root")) for m in live}

    def stop(self):
        for m in self.names:
            MS.send(self.ports[m], "/shutdown", timeout=5)
        for p in self.procs.values():
            try:
                p.wait(timeout=10)
            except subprocess.TimeoutExpired:
                p.kill()


def gossip(fleet, rng, down=None, back_at=None, stats=None):
    """Push-pull rounds until every mirror agrees (or MAX_ROUNDS). down: killed now, restarted at round back_at."""
    live = [m for m in fleet.names if m != down]
    for r in range(1, MAX_ROUNDS + 1):
        if down and r == back_at:
            fleet.start(down)
            live = list(fleet.names)
        for m in rng.sample(live, len(live)):
            peer = rng.choice([p for p in live if p != m])
            for a, b in ((m, peer), (peer, m)):
                res = json.loads(MS.send(fleet.ports[a], f"/pull?port={fleet.ports[b]}") or b"{}")
                stats["requests"] += res.get("requests", 0)
                stats["bytes"] += res.get("bytes", 0)
        s = fleet.summaries(live)
        if len(live) == len(fleet.names) and len({(x["root"], x["ts_version"]) for x in s.values()}) == 1:
            return r
    return None


def run(run_dir, mirrors=4, releases=4, seed=6, inject=None, out=None):
    rng, pub = random.Random(seed), P.Publisher()
    t0 = time.perf_counter()
    fleet = Fleet(run_dir, mirrors, inject)
    rounds, stats, victim, before, after = {}, {"requests": 0, "bytes": 0}, fleet.names[-1], None, None
    try:
        for v in range(1, releases + 1):
            now = SPACING * (v - 1)
            objects = pub.publish(v, now)
            for key, raw in objects.items():
                MS.send(fleet.ports["m0"], "/obj?" + urllib.parse.urlencode({"key": key}), "PUT", raw)
            MS.send(fleet.ports["m0"], "/timestamp", "PUT", pub.timestamp(now))
            last = v == releases
            if last:
                before = fleet.summaries([victim])[victim]["objects"]
                fleet.kill(victim)
                after = fleet.start(victim)["recovered_on_start"]   # restart once to prove recovery from disk...
                fleet.kill(victim)                                   # ...then keep it down while v spreads
            rounds[v] = gossip(fleet, rng, victim if last else None, 3 if last else None, stats)
        now = SPACING * (releases - 1) + 60
        verified, reasons = {}, {}
        for m in fleet.names:
            cl = CL.Client(pub.roots[0])    # root v1 shipped with the client; later roots chained (TUF 5.3)
            cl.update_root(pub.roots)
            try:
                verified[m] = bool(cl.fetch(HttpMirror(m, fleet.ports[m]), pub.log, now))
            except (CL.Rejected, KeyError, ValueError) as e:
                verified[m], reasons[m] = False, str(e)[:160]
        conflicts = {m: s["conflicts"][:3] for m, s in fleet.summaries(fleet.names).items() if s["conflicts"]}
    finally:
        fleet.stop()
    elapsed = time.perf_counter() - t0
    rows = [{"experiment": "06 mirrors over HTTP", "mirrors": mirrors, "releases": releases, "seed": seed,
             "inject": inject, "http_requests": stats["requests"], "bytes_moved": stats["bytes"],
             "elapsed_s": round(elapsed, 1), "at": _mac.stamp()},
            {"fitness": "H1 every release converges on every mirror", "rounds_per_release": rounds,
             "max_rounds": MAX_ROUNDS, "conflicts": conflicts, "pass": all(r is not None for r in rounds.values())},
            {"fitness": "H2 client verifies the latest release from every mirror over HTTP", "verified": verified,
             "reasons": reasons, "pass": all(verified.values())},
            {"fitness": "H3 killed mirror recovered its objects from disk", "mirror": victim,
             "objects_before_kill": before, "recovered_on_restart": after, "pass": before == after}]
    for r in rows:
        _mac.emit(r, out)
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--here", action="store_true", help="4 mirrors, 4 releases")
    ap.add_argument("--mirrors", type=int, default=8)
    ap.add_argument("--releases", type=int, default=40)
    ap.add_argument("--seed", type=int, default=6)
    ap.add_argument("--inject", choices=("float-format",))
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    mirrors, releases = (4, 4) if a.here else (a.mirrors, a.releases)
    run_dir = _mac.HERE / "runs" / f"{time.strftime('%Y%m%d-%H%M%S')}-http"
    try:
        rows = run(run_dir, mirrors, releases, a.seed, a.inject, a.out)
    finally:
        if not a.keep:
            shutil.rmtree(run_dir, ignore_errors=True)
    ok = all(r["pass"] for r in rows[1:])
    _mac.emit({"scorecard": "06 mac mirrors over HTTP", "inject": a.inject, "pass": ok, "decided_by": "code"}, a.out)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
