"""Experiment 2 - nonce uniqueness across REAL process failover: 3 replicas = 3 OS processes on 127.0.0.1, the leader
is killed with SIGKILL (Windows: TerminateProcess) at seeded points - half of them while a seal request is in flight -
and restarted from its own disk. Then the project's fitness functions are re-run on what the processes wrote.

python mac_mini/multiproc.py --here                         300 messages, 4 kills (the sandbox / CI size)
python mac_mini/multiproc.py --messages 100000 --kills 400  the overnight size on the Mac mini
python mac_mini/multiproc.py --here --nonce leader-counter  the failure lab across processes: must FAIL (exit 1)
python mac_mini/multiproc.py --here --nonce derived          the build-task solution (term || counter): must PASS

F1  no nonce is used twice under the epoch key, over EVERY envelope any process sealed (harness.nonce_reuse audit,
    cryptography L300 #15 scan_for_reuse)
F2  after the last restart every replica's on-disk log is identical and holds every acknowledged message exactly once
Exit 0 only if both pass. Run folder: mac_mini/runs/<stamp>-<nonce> (kept with --keep; deleted otherwise).
"""
import argparse
import json
import os
import random
import shutil
import socket
import subprocess
import sys
import time
import uuid
from pathlib import Path

import _mac
import replica as R

SENDERS = ("alice", "bob", "carol")


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Cluster:
    def __init__(self, run_dir, nonce, fsync=True):
        self.dir, self.nonce, self.fsync = Path(run_dir), nonce, fsync
        self.dir.mkdir(parents=True, exist_ok=True)
        (self.dir / "epoch1.key").write_text(os.urandom(32).hex())
        self.ports = {f"r{i}": free_port() for i in range(1, 4)}
        self.procs, self.leader, self.failovers, self.restarts = {}, None, 0, 0
        for name in self.ports:
            self.start(name)
        self.elect()

    def start(self, name):
        cmd = [sys.executable, str(Path(R.__file__)), "--name", name, "--port", str(self.ports[name]),
               "--dir", str(self.dir), "--nonce", self.nonce] + ([] if self.fsync else ["--no-fsync"])
        err = self.dir / f"{name}.stderr"
        with open(err, "ab") as f:  # the child keeps its own handle; ours closes here
            p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=f)
        self.procs[name] = p
        for _ in range(1200):  # imports on a slow disk can take a while
            st = R.call(self.ports[name], {"op": "status"}, timeout=1.0)
            if st and st["pid"] == p.pid:
                return st
            if p.poll() is not None:
                raise RuntimeError(f"{name} exited: {err.read_text(errors='replace')[-800:]}")
            time.sleep(0.05)
        raise RuntimeError(f"{name} did not start")

    def status(self):
        return {n: R.call(p, {"op": "status"}, timeout=2.0) for n, p in self.ports.items()}

    def elect(self):
        """Most up-to-date live replica (last term, length) wins a strictly higher term (Raft's two rules here)."""
        live = {n: s for n, s in self.status().items() if s}
        name = max(live, key=lambda n: (live[n]["last_term"], live[n]["len"], n))
        term = max(s["term"] for s in live.values()) + 1
        peers = [p for n, p in self.ports.items() if n != name]
        assert R.call(self.ports[name], {"op": "promote", "term": term, "peers": peers})["ok"]
        self.leader = name
        for n in live:
            if n != name:
                R.call(self.ports[name], {"op": "catchup", "port": self.ports[n]}, timeout=60)
        return name

    def kill(self, name):
        self.procs[name].kill()  # SIGKILL on macOS/Linux: no cleanup handlers, no flush of anything volatile
        self.procs[name].wait()

    def seal(self, ikey, sender, text):
        return R.call(self.ports[self.leader], {"op": "seal", "ikey": ikey, "sender": sender, "text": text}, timeout=30)

    def seal_and_kill(self, ikey, sender, text, rng):
        """Send the request, then kill the leader 0-3 ms later: it may or may not have replicated the entry."""
        try:
            s = socket.create_connection(("127.0.0.1", self.ports[self.leader]), timeout=5)
            s.sendall((json.dumps({"op": "seal", "ikey": ikey, "sender": sender, "text": text}) + "\n").encode())
            time.sleep(rng.uniform(0, 0.003))
        finally:
            self.kill(self.leader)
            s.close()

    def failover(self, rng, inflight=None):
        dead = self.leader
        if inflight:
            self.seal_and_kill(*inflight, rng)
        else:
            self.kill(dead)
        self.elect()
        self.failovers += 1
        self.start(dead)  # restart from its own disk; volatile nonce state is gone
        self.restarts += 1
        R.call(self.ports[self.leader], {"op": "catchup", "port": self.ports[dead]}, timeout=120)

    def stop(self):
        for name, port in self.ports.items():
            R.call(port, {"op": "shutdown"}, timeout=2.0)
        for p in self.procs.values():
            try:
                p.wait(timeout=10)
            except subprocess.TimeoutExpired:
                p.kill()


def audit(run_dir, acked):
    import harness  # the lab's offline nonce audit (loads cryptography L300 #15 nonce_guard)
    run_dir = Path(run_dir)
    names = sorted(p.name for p in run_dir.iterdir() if p.is_dir() and p.name.startswith("r"))
    logs = {n: R.read_log(run_dir / n) for n in names}
    wire = []
    for n in names:
        f = run_dir / n / "sealed.jsonl"
        if f.exists():
            for line in f.read_text(encoding="utf-8").splitlines():
                try:
                    wire.append(json.loads(line))
                except ValueError:
                    pass  # empty or torn line: the process died while writing it, before sending it
    reuse = harness.nonce_reuse(wire)
    reused = sum(map(len, reuse.values()))
    flat = {n: [(e["i"], e["t"], e["ikey"], e["env"]["ct"]) for e in log] for n, log in logs.items()}
    identical = len({json.dumps(v) for v in flat.values()}) == 1
    ikeys = [e["ikey"] for e in logs[names[0]]]
    once = len(ikeys) == len(set(ikeys))
    missing = sorted(set(acked) - set(ikeys))
    f1 = {"fitness": "F1 no nonce reuse across real process failover", "ciphertexts_on_wire": len(wire),
          "reused_nonces": reused, "pass": reused == 0}
    if reused:
        first = next(iter(reuse.values()))
        f1["example_reused_nonce_hex"] = next(iter(first))
    f2 = {"fitness": "F2 every acked message exactly once on every replica's disk", "acked": len(acked),
          "log_lengths": {n: len(v) for n, v in logs.items()}, "logs_identical": identical,
          "duplicates_in_log": len(ikeys) - len(set(ikeys)), "acked_missing": len(missing),
          "pass": identical and once and not missing}
    return f1, f2


def run(messages, kills, nonce, seed, run_dir, fsync=True, out=None):
    rng = random.Random(seed)
    kill_at = set(rng.sample(range(5, messages), min(kills, max(0, messages - 5))))
    t0 = time.perf_counter()
    cl = Cluster(run_dir, nonce, fsync)
    acked, retries, inflight_kills = set(), 0, 0
    try:
        for i in range(messages):
            sender = SENDERS[i % 3]
            ikey, text = str(uuid.UUID(int=rng.getrandbits(128), version=4)), f"msg {i:06d} from {sender}: status green"
            if i in kill_at:
                mid = rng.random() < 0.5
                inflight_kills += mid
                cl.failover(rng, (ikey, sender, text) if mid else None)
            for attempt in range(20):  # client: ONE Idempotency-Key per message, retried until acknowledged
                r = cl.seal(ikey, sender, text)
                if r and r.get("ok"):
                    acked.add(ikey)
                    break
                retries += 1
                if r is None or r.get("err") == "not_leader":
                    cl.elect()
                time.sleep(0.01)
        for name, port in cl.ports.items():
            if name != cl.leader:
                R.call(cl.ports[cl.leader], {"op": "catchup", "port": port}, timeout=300)
    finally:
        cl.stop()
    elapsed = time.perf_counter() - t0
    head = {"experiment": "01 multi-process failover", "nonce": nonce, "messages": messages, "seed": seed,
            "kills": len(kill_at), "kills_with_request_in_flight": inflight_kills, "failovers": cl.failovers,
            "restarts": cl.restarts, "acked": len(acked), "client_retries": retries, "fsync": fsync,
            "elapsed_s": round(elapsed, 1), "msgs_per_s": round(messages / elapsed, 1), "at": _mac.stamp()}
    rows = [head, *audit(run_dir, acked)]
    for row in rows:
        _mac.emit(row, out)
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--here", action="store_true", help="300 messages, 4 kills")
    ap.add_argument("--messages", type=int, default=100000)
    ap.add_argument("--kills", type=int, default=400)
    ap.add_argument("--nonce", choices=("random", "derived", "leader-counter"), default="random")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--no-fsync", action="store_true", help="skip fsync (faster; not crash-safe on power loss)")
    ap.add_argument("--keep", action="store_true", help="keep the run folder (logs, terms, sealed envelopes)")
    ap.add_argument("--dir", help="run folder (default mac_mini/runs/<stamp>-<nonce>)")
    ap.add_argument("--out", help="append JSON lines to this file")
    a = ap.parse_args(argv)
    messages, kills = (300, 4) if a.here else (a.messages, a.kills)
    run_dir = Path(a.dir) if a.dir else _mac.HERE / "runs" / f"{time.strftime('%Y%m%d-%H%M%S')}-{a.nonce}"
    try:
        rows = run(messages, kills, a.nonce, a.seed, run_dir, fsync=not a.no_fsync, out=a.out)
    finally:
        if not a.keep:
            shutil.rmtree(run_dir, ignore_errors=True)
    ok = all(r["pass"] for r in rows[1:])
    _mac.emit({"scorecard": "01 mac multi-process", "nonce": a.nonce, "pass": ok, "decided_by": "code"}, a.out)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
