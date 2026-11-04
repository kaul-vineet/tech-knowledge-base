"""GET /reports/overdue over the repository (stdlib http.server on 127.0.0.1). Run: python http_api.py 8016"""
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import loans_repo


def make_handler(repo, conn, lock):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != "/reports/overdue":
                status, body = 404, {"error": "not found"}
            else:
                with lock:  # one SQLite connection shared by the server threads
                    status, body = 200, repo.overdue_report(conn)
            data = json.dumps(body).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *args):
            pass

    return Handler


class Server(ThreadingHTTPServer):
    request_queue_size = 64  # the default backlog (5) drops connections under a burst -> 1 s SYN retries


def start(repo=loans_repo, loans=500, port=0):
    server = Server(("127.0.0.1", port), make_handler(repo, repo.seeded_db(loans=loans), threading.Lock()))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}"


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8016
    server, url = start(port=port)
    print(f"overdue report on {url}/reports/overdue (Ctrl+C to stop)")
    threading.Event().wait()
