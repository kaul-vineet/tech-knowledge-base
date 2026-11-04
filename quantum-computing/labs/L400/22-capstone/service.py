"""Capstone API: POST /solve {json request} -> report; GET /health. Binds 127.0.0.1 only (stdlib http.server).

Run:  python service.py --port 8765     then   curl -X POST 127.0.0.1:8765/solve -d '{"n": 8}'
Invalid requests get HTTP 400 with the reason; the pipeline never runs for them.
"""
import argparse
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pipeline


def strip(report):
    """Drop non-JSON internals before sending."""
    return json.loads(json.dumps(report, default=str))


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self._send(200, {"status": "ok"}) if self.path == "/health" else self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/solve":
            return self._send(404, {"error": "not found"})
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            pipeline.validate(req)
        except (ValueError, TypeError) as e:
            return self._send(400, {"error": str(e)})
        self._send(200, strip(pipeline.solve(req)))

    def log_message(self, *args):
        pass


def start(port=0):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    server = ThreadingHTTPServer(("127.0.0.1", parser.parse_args().port), Handler)
    print(f"serving on http://127.0.0.1:{server.server_address[1]}")
    server.serve_forever()
