"""Shared plumbing for this lab (not the lesson's concept): a quiet JSON HTTP handler, a proxy-free
client call(), a background localhost server and a simulated clock (so every run is identical)."""
import json, threading, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError

OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # never proxy localhost


class SimClock:
    """Simulated seconds: the demo advances time explicitly, so nothing sleeps and runs repeat."""
    def __init__(self, t=0.0):
        self.t = t

    def __call__(self):
        return self.t

    def advance(self, dt):
        self.t += dt


class QuietHandler(BaseHTTPRequestHandler):
    def reply(self, status, data, headers=None):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        return json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")

    def log_message(self, *args):  # keep the console quiet
        pass


def serve(handler, port=0):
    """Run a ThreadingHTTPServer on 127.0.0.1 in a background thread (port 0 = OS picks)."""
    srv = ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=srv.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()
    return srv


def call(url, payload=None, headers=None, timeout=2.0):
    """POST JSON (GET if payload is None). Returns (status, body_dict, headers); 4xx/5xx are returned."""
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **(headers or {})})
    try:
        with OPENER.open(req, timeout=timeout) as r:
            return r.status, json.loads(r.read() or b"{}"), r.headers
    except HTTPError as e:
        return e.code, json.loads(e.read() or b"{}"), e.headers
