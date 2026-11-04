"""One mirror as a real OS process serving HTTP on 127.0.0.1 (started by http_world.py; not run by hand).

python mirror_server.py --name m1 --port 48001 --dir runs/x [--encoder platform]

Storage = mirrors.Mirror (immutable keys, max-version timestamp, 16 Merkle buckets) persisted to <dir>/<name>/:
  objects.jsonl     append-only {"key", "hex"} lines (replayed through Mirror.put on start-up, so the same rules apply)
  timestamps.jsonl  append-only timestamp bytes (replayed through Mirror.put_timestamp)
HTTP API (stdlib http.server, loopback only):
  GET  /root               {"root", "buckets": [16 hex], "ts_version", "objects"}
  GET  /bucket/<i>         {key: sha256} for the keys in bucket i
  GET  /obj?key=K          the stored bytes          PUT /obj?key=K    store (immutable: a different body = conflict)
  GET  /timestamp          timestamp bytes or 404    PUT /timestamp    max-version register
  POST /pull?port=P        anti-entropy: pull from the mirror on port P (roots -> buckets -> missing keys only)
  POST /shutdown
--encoder platform re-serialises every .json object with canonical.platform_dumps on ingest: the failure lab's m2.
"""
import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import canonical as C  # noqa: E402
import mirrors as MR  # noqa: E402


def get(port, path, timeout=10):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=timeout) as r:
            return r.read()
    except (urllib.error.URLError, OSError):
        return None


def send(port, path, method="POST", body=b"", timeout=60):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=body, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except (urllib.error.URLError, OSError):
        return None


class Store:
    def __init__(self, name, folder, encoder=None):
        self.dir = Path(folder)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.m = MR.Mirror(name, encoder=encoder)
        for line in self._lines("objects.jsonl"):
            row = json.loads(line)
            self.m.objects.setdefault(row["key"], bytes.fromhex(row["hex"]))  # already transformed when first stored
        for line in self._lines("timestamps.jsonl"):
            self.m.put_timestamp(bytes.fromhex(line))
        self.recovered = len(self.m.objects)

    def _lines(self, f):
        p = self.dir / f
        return [x for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []

    def _append(self, f, line):
        with open(self.dir / f, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def put(self, key, raw):
        had = key in self.m.objects
        self.m.put(key, raw)
        if not had and key in self.m.objects:
            self._append("objects.jsonl", json.dumps({"key": key, "hex": self.m.objects[key].hex()}))

    def put_timestamp(self, raw):
        before = self.m.timestamp
        self.m.put_timestamp(raw)
        if self.m.timestamp is not before:
            self._append("timestamps.jsonl", raw.hex())

    def summary(self):
        ts = self.m.timestamp
        return {"name": self.m.name, "root": self.m.root().hex(), "buckets": [h.hex() for h in self.m.bucket_hashes()],
                "ts_version": json.loads(ts)["signed"]["version"] if ts else None, "objects": len(self.m.objects),
                "conflicts": sorted(self.m.conflicts), "recovered_on_start": self.recovered}

    def bucket(self, i):
        return {k: hashlib.sha256(v).hexdigest() for k, v in self.m.objects.items() if MR._bucket(k) == i}

    def pull(self, port):
        """mirrors.pull over HTTP: 1 root request; 16 bucket hashes only if roots differ; then only missing keys."""
        stats = {"requests": 1, "bytes": 0}
        peer = get(port, "/root")
        if peer is None:
            return {"ok": False, "err": "peer down", **stats}
        peer = json.loads(peer)
        if peer["ts_version"] is not None and (self.m.timestamp is None or
                                               peer["ts_version"] > json.loads(self.m.timestamp)["signed"]["version"]):
            ts = get(port, "/timestamp")
            stats["requests"] += 1
            if ts:
                self.put_timestamp(ts)
                stats["bytes"] += len(ts)
        if peer["root"] == self.m.root().hex():
            return {"ok": True, **stats}
        mine = [h.hex() for h in self.m.bucket_hashes()]
        for i in (i for i in range(MR.BUCKETS) if mine[i] != peer["buckets"][i]):
            listing = json.loads(get(port, f"/bucket/{i}") or b"{}")
            stats["requests"] += 1
            for key, digest in listing.items():
                have = self.m.objects.get(key)
                if have is not None and hashlib.sha256(have).hexdigest() == digest:
                    continue
                raw = get(port, "/obj?" + urllib.parse.urlencode({"key": key}))
                stats["requests"] += 1
                if raw is not None:
                    self.put(key, raw)
                    stats["bytes"] += len(raw)
        return {"ok": True, **stats}


def serve(store, port):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def reply(self, code, body, ctype="application/json"):
            body = body if isinstance(body, bytes) else json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            u = urllib.parse.urlsplit(self.path)
            q = dict(urllib.parse.parse_qsl(u.query))
            if u.path == "/root":
                return self.reply(200, store.summary())
            if u.path.startswith("/bucket/"):
                return self.reply(200, store.bucket(int(u.path.rsplit("/", 1)[1])))
            if u.path == "/obj" and q.get("key") in store.m.objects:
                return self.reply(200, store.m.objects[q["key"]], "application/octet-stream")
            if u.path == "/timestamp" and store.m.timestamp:
                return self.reply(200, store.m.timestamp, "application/json")
            return self.reply(404, {"err": "not found"})

        def _body(self):
            return self.rfile.read(int(self.headers.get("Content-Length") or 0))

        def do_PUT(self):
            u = urllib.parse.urlsplit(self.path)
            q, body = dict(urllib.parse.parse_qsl(u.query)), self._body()
            if u.path == "/obj":
                store.put(q["key"], body)
            elif u.path == "/timestamp":
                store.put_timestamp(body)
            else:
                return self.reply(404, {"err": "not found"})
            return self.reply(200, {"ok": True})

        def do_POST(self):
            u = urllib.parse.urlsplit(self.path)
            q = dict(urllib.parse.parse_qsl(u.query))
            self._body()
            if u.path == "/pull":
                return self.reply(200, store.pull(int(q["port"])))
            if u.path == "/shutdown":
                self.reply(200, {"ok": True})
                self.server.done = True
                return None
            return self.reply(404, {"err": "not found"})

    srv = ThreadingHTTPServer(("127.0.0.1", port), H)   # loopback only, never 0.0.0.0
    srv.done = False
    while not srv.done:
        srv.handle_request()
    srv.server_close()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--dir", required=True)
    ap.add_argument("--encoder", choices=("canonical", "platform"), default="canonical")
    a = ap.parse_args(argv)
    enc = C.platform_dumps if a.encoder == "platform" else None
    serve(Store(a.name, Path(a.dir) / a.name, enc), a.port)


if __name__ == "__main__":
    main()
