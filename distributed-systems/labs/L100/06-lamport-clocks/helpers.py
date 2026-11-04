"""Shared plumbing for this lab (not the lesson's concept): a quiet HTTP handler with a
reply() helper, a proxy-free client opener, a background localhost server, and log printing."""
import json, threading, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # never proxy localhost


class QuietHandler(BaseHTTPRequestHandler):
    def reply(self, status, data=b""):
        """Send one response; dict/list -> JSON body, bytes -> sent as-is."""
        body = data if isinstance(data, bytes) else json.dumps(data).encode()
        self.send_response(status)
        if not isinstance(data, bytes):
            self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        return self.rfile.read(int(self.headers["Content-Length"]))

    def log_message(self, *args):  # keep the console quiet
        pass


def serve(handler, port=0):
    """Run a ThreadingHTTPServer on 127.0.0.1 in a background thread (port 0 = OS picks)."""
    srv = ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def violations(order):
    """Count messages whose 'recv' is listed before its 'send' (an effect before its cause)."""
    pos = {(e[4], e[3].startswith("send")): i for i, e in enumerate(order) if e[4]}
    return sum(pos[(m, False)] < pos[(m, True)] for m, is_send in pos if is_send)


def show(title, order):
    print(f"--- {title}: {violations(order)} causality violation(s) ---")
    for lam, node, wall, text, _ in order:
        print(f"  L={lam:<2} wall={wall:+.3f}s  {node}: {text}")
