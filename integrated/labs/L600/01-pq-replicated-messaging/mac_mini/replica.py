"""One replica as a real OS process (started by multiproc.py; not run by hand).

python replica.py --name r1 --port 47001 --dir runs/x --nonce random|derived|leader-counter

TCP on 127.0.0.1 only, one JSON request + one JSON reply per connection. Durable state lives in --dir/<name>/:
  term.log    append-only, last line = current term (fsync before the replica acts in a new term)
  log.jsonl   append-only replicated log; a {"truncate_to": k} line drops an uncommitted suffix (Raft log repair)
  sealed.jsonl every envelope THIS process ever sealed, committed or not = what went on the wire (for the audit)
Volatile state (lost on kill -9): the nonce source, the leader flag, the peers list. That is the point: the nonce
source of the failure lab (nonce_derived.DerivedNonce) keeps its counter here, so a restarted or newly promoted
process starts again at 1 under the SAME epoch key. Election is done by the supervisor (multiproc.py) with Raft's
rules that matter here: strictly increasing persisted terms, and the most up-to-date live replica (last term, length)
becomes leader. It is not a full Raft implementation (the in-process lab uses lesson 12's Raft for that).
Teaching shortcut: the epoch secret is read from a file the supervisor writes (in pqmsg.py the sealer learns it
from its hybrid welcome in the log).
"""
import argparse
import importlib.util
import json
import os
import socket
import socketserver
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import group_crypto as gc  # noqa: E402  (the lab's envelope + AES-256-GCM seal)
import nonce_derived  # noqa: E402  (shipped build task = the failure lab's counter)

EPOCH = 1


class RandomNonce:  # ADR-01-1, same as pqmsg.RandomNonce: 96 random bits, nothing to remember across restarts
    def next(self, term):
        return os.urandom(12)


def nonce_source(kind):
    if kind == "random":
        return RandomNonce()
    if kind == "leader-counter":
        return nonce_derived.DerivedNonce()
    spec = importlib.util.spec_from_file_location("kb01_solution_nonce", HERE.parent / "solution" / "nonce_derived.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.DerivedNonce()  # term (4 B) || per-term counter (8 B)


def call(port, req, timeout=5.0):
    """One request to another replica; None if it is down (connection refused / reset / timeout)."""
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=timeout) as s:
            s.sendall((json.dumps(req) + "\n").encode())
            data = s.makefile("rb").readline()
        return json.loads(data) if data else None
    except (OSError, ValueError):
        return None


def read_log(folder):
    """Replay log.jsonl (with truncate markers) -> list of entries. Used at start-up and by the auditor."""
    entries = []
    path = Path(folder) / "log.jsonl"
    if path.exists():
        lines = [x for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
        for line in lines:
            try:
                row = json.loads(line)
            except ValueError:
                continue  # torn line (killed mid-write, newline added on restart): never fsynced whole, never acked
            if "truncate_to" in row:
                del entries[row["truncate_to"]:]
            else:
                entries.append(row)
    return entries


def read_term(folder):
    path = Path(folder) / "term.log"
    terms = [int(x) for x in path.read_text(encoding="utf-8").split() if x.isdigit()] if path.exists() else []
    return max(terms, default=0)


class Replica:
    def __init__(self, name, folder, nonce, fsync=True):
        self.name, self.dir, self.fsync = name, Path(folder), fsync
        self.dir.mkdir(parents=True, exist_ok=True)
        for f in ("log.jsonl", "term.log", "sealed.jsonl"):
            p = self.dir / f
            if p.exists() and p.stat().st_size and not p.read_bytes().endswith(b"\n"):
                with open(p, "a", encoding="utf-8") as fh:
                    fh.write("\n")  # terminate a torn last line so the next record starts on its own line
        self.term, self.log = read_term(self.dir), read_log(self.dir)
        self.index = {e["ikey"]: e["i"] for e in self.log}
        self.leader, self.peers, self.nonce = False, [], nonce_source(nonce)
        self.secret = bytes.fromhex((self.dir.parent / "epoch1.key").read_text().strip())

    def _append_line(self, file, row):
        with open(self.dir / file, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
            f.flush()
            if self.fsync:
                os.fsync(f.fileno())

    def set_term(self, term):
        self._append_line("term.log", term)
        self.term = term

    def truncate(self, k):
        if len(self.log) > k:
            for e in self.log[k:]:
                self.index.pop(e["ikey"], None)
            del self.log[k:]
            self._append_line("log.jsonl", {"truncate_to": k})

    def append(self, entries):
        for e in entries:
            self._append_line("log.jsonl", e)
            self.log.append(e)
            self.index[e["ikey"]] = e["i"]

    def digest(self, i):
        return [self.log[i - 1]["t"], self.log[i - 1]["ikey"]] if 0 < i <= len(self.log) else None

    def catch_up(self, port):
        """Leader -> one follower: find the last matching index (walk back), then send the rest (Raft log repair)."""
        st = call(port, {"op": "status"})
        if st is None:
            return False
        k = min(st["len"], len(self.log))
        while k > 0 and call(port, {"op": "digest", "i": k}) != {"d": self.digest(k)}:
            k -= 1
        for start in range(k, len(self.log), 500):
            r = call(port, {"op": "append", "term": self.term, "prev": start, "entries": self.log[start:start + 500]})
            if not r or not r.get("ok"):
                return False
        return True

    def handle(self, req):
        op = req["op"]
        if op == "status":
            return {"name": self.name, "pid": os.getpid(), "term": self.term, "leader": self.leader,
                    "len": len(self.log), "last_term": self.log[-1]["t"] if self.log else 0}
        if op == "digest":
            return {"d": self.digest(req["i"])}
        if op == "promote":
            if req["term"] <= self.term:
                return {"ok": False, "err": f"term {req['term']} <= persisted term {self.term}"}
            self.set_term(req["term"])  # persisted BEFORE the first seal in the new term
            self.leader, self.peers = True, req["peers"]
            return {"ok": True}
        if op == "append":
            if req["term"] < self.term:
                return {"ok": False, "err": "stale leader"}
            if req["term"] > self.term:
                self.set_term(req["term"])
            self.leader = False
            if len(self.log) < req["prev"]:
                return {"ok": False, "need": len(self.log)}
            entries, prev = req["entries"], req["prev"]
            while entries and prev < len(self.log) and self.digest(prev + 1) == [entries[0]["t"], entries[0]["ikey"]]:
                entries, prev = entries[1:], prev + 1  # already have it (a repeated append): skip
            if entries and len(self.log) > prev:
                self.truncate(prev)  # drop a divergent / uncommitted suffix before appending
            self.append(entries)
            return {"ok": True, "len": len(self.log)}
        if op == "catchup":
            return {"ok": self.leader and self.catch_up(req["port"])}
        if op == "seal":
            return self.seal(req)
        if op == "shutdown":
            return {"ok": True, "bye": True}
        return {"ok": False, "err": f"unknown op {op}"}

    def seal(self, req):
        if not self.leader:
            return {"ok": False, "err": "not_leader"}
        if req["ikey"] in self.index:  # retried request: idempotent, no second ciphertext
            return {"ok": True, "i": self.index[req["ikey"]], "dup": True}
        nonce = self.nonce.next(self.term)
        env = gc.seal(self.secret, EPOCH, req["sender"], req["ikey"], req["text"], nonce)
        self._append_line("sealed.jsonl", env)  # on the wire from now on, committed or not
        entry = {"i": len(self.log) + 1, "t": self.term, "ikey": req["ikey"], "env": env}
        self.append([entry])
        acks = 1
        for port in self.peers:
            r = call(port, {"op": "append", "term": self.term, "prev": entry["i"] - 1, "entries": [entry]})
            if r and not r.get("ok") and "need" in r:
                r = {"ok": self.catch_up(port)}
            acks += bool(r and r.get("ok"))
        if acks >= 2:  # majority of 3: committed
            return {"ok": True, "i": entry["i"], "acks": acks}
        return {"ok": False, "err": "no_majority"}  # outcome unknown for the client: retry with the SAME key


def serve(replica, port):
    class Handler(socketserver.StreamRequestHandler):
        def handle(self):
            req = json.loads(self.rfile.readline())
            resp = replica.handle(req)
            self.wfile.write((json.dumps(resp) + "\n").encode())
            if resp.get("bye"):
                self.server.done = True

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", port), Handler) as srv:  # loopback only
        srv.done = False
        while not srv.done:
            srv.handle_request()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--dir", required=True, help="run folder; this replica uses <dir>/<name>/")
    ap.add_argument("--nonce", choices=("random", "derived", "leader-counter"), default="random")
    ap.add_argument("--no-fsync", action="store_true")
    a = ap.parse_args(argv)
    serve(Replica(a.name, Path(a.dir) / a.name, a.nonce, fsync=not a.no_fsync), a.port)


if __name__ == "__main__":
    main()
