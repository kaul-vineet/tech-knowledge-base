"""The extracted fines service (new code). Runs in-process or over HTTP on 127.0.0.1.

Solution: Decimal arithmetic with ROUND_HALF_UP, the same rounding rule as the monolith.
"""
import json
import threading
import urllib.parse
from decimal import ROUND_HALF_UP, Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def fine_for(days_late, member_type):
    chargeable = max(0, days_late - 2)
    fine = Decimal("0.25") * chargeable * (Decimal("0.5") if member_type == "student" else 1)
    return str(min(fine, Decimal("10.00")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))  # fix: half-up, exact


def start(port=0, fine=fine_for):
    """Serve GET /fines?days_late=N&member_type=T -> {"fine": "0.13"}. Returns (server, base_url)."""
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            url = urllib.parse.urlparse(self.path)
            q = dict(urllib.parse.parse_qsl(url.query))
            status, body = (200, {"fine": fine(int(q["days_late"]), q["member_type"])}) if url.path == "/fines" \
                else (404, {"error": "not found"})
            data = json.dumps(body).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}"
