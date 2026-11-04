"""Shared plumbing for this lab (not the lesson's concept): a quiet HTTP handler with a
reply() helper, a proxy-free client opener, and a background localhost server."""
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
