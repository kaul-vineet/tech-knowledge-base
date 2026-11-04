"""A tiny HTTP "node" for the local multi-node lab (Python stdlib only; macOS, Windows, Linux).

Run one by hand:  python node.py --name node1 --port 8001
Then:             curl http://127.0.0.1:8001/health   (or open it in a browser)
"""
import argparse
import json
import os
import socket
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

WINDOWS = sys.platform == "win32"


class NodeServer(ThreadingHTTPServer):
    # HTTPServer sets SO_REUSEADDR. On Windows that lets a 2nd process bind the SAME port
    # silently (who gets each request is then undefined), so ask for exclusive use there instead.
    allow_reuse_address = not WINDOWS

    def server_bind(self):
        if WINDOWS:
            opt = getattr(socket, "SO_EXCLUSIVEADDRUSE", ~socket.SO_REUSEADDR)  # winsock: ~SO_REUSEADDR
            self.socket.setsockopt(socket.SOL_SOCKET, opt, 1)
        super().server_bind()


def make_handler(name):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != "/health":
                self.send_error(404)
                return
            body = json.dumps({"node": name, "port": self.server.server_port,
                               "pid": os.getpid()}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):  # keep the console quiet
            pass

    return Handler


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--name", default="node1")
    p.add_argument("--host", default="127.0.0.1")  # loopback only; 0.0.0.0 = container or LAN step
    p.add_argument("--port", type=int, default=8001)  # port = address: a second bind fails "in use"
    a = p.parse_args()
    # one HTTP server per node; ThreadingHTTPServer = one thread per request, so a slow
    # request does not block the health check
    srv = NodeServer((a.host, a.port), make_handler(a.name))
    print(f"{a.name} listening on http://{a.host}:{a.port}", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:  # Ctrl+C works the same on macOS and Windows consoles
        pass
    finally:
        srv.server_close()


if __name__ == "__main__":
    main()
