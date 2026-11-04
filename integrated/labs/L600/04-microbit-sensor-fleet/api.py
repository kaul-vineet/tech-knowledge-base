"""Fleet API (application-architecture side): read-only, versioned, served from one backend replica.

/v2/devices/{dev}/latest               {"device","boot","seq","tempC","light","schema","deviceTime","count"}
/v2/devices/{dev}/readings?boot=&after=&limit=   contiguous prefix only ("stableThrough" = the version-vector hw)
/v1/devices/{dev}/latest               {"device","seq","tempC"} + Deprecation (RFC 9745) and Sunset (RFC 8594):
                                       v1 has no "boot", so its "seq" goes backwards after a device reboot.
"latest" = max (boot, seq), never max wall time: deviceTime is a display attribute and can repeat.
Binds 127.0.0.1 only.
"""
import json
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

V1_DEPRECATED = datetime(2027, 1, 1, tzinfo=timezone.utc)
V1_HEADERS = {"Deprecation": "@%d" % int(V1_DEPRECATED.timestamp()),
              "Sunset": "Fri, 01 Oct 2027 00:00:00 GMT",
              "Link": '</v2/devices>; rel="successor-version"'}


def _dev(name):
    if len(name) == 3 and name[0] == "d" and name[1:].isdigit():
        return int(name[1:])
    raise KeyError(name)


def latest(store, name, version):
    rows = store.rows(_dev(name))
    if not rows:
        raise KeyError(name)
    (dev, boot, seq), (wall, temp, light, schema) = max(rows, key=lambda r: r[0])
    if version == 1:
        return {"device": name, "seq": seq, "tempC": temp}, dict(V1_HEADERS)
    return {"device": name, "boot": boot, "seq": seq, "tempC": temp, "light": light, "schema": schema,
            "deviceTime": wall, "count": len(rows)}, {}


def readings(store, name, boot, after=0, limit=100):
    """Only the contiguous prefix of one boot: a reading below the hw can never appear later, so a client
    paging with `after` never skips one that gossip delivers late."""
    rows = store.contiguous_rows(_dev(name), boot)
    items = [{"seq": d[2], "tempC": v[1], "light": v[2]} for d, v in rows if d[2] > after][:limit]
    return {"device": name, "boot": boot, "items": items, "next": items[-1]["seq"] if items else None,
            "stableThrough": store.contiguous(_dev(name), boot)}, {}


def route(store, path):
    url = urlparse(path)
    parts = url.path.strip("/").split("/")
    q = {k: v[0] for k, v in parse_qs(url.query).items()}
    try:
        if len(parts) == 4 and parts[1] == "devices" and parts[3] == "latest" and parts[0] in ("v1", "v2"):
            return (200,) + latest(store, parts[2], int(parts[0][1]))
        if len(parts) == 4 and parts[:2] == ["v2", "devices"] and parts[3] == "readings":
            return (200,) + readings(store, parts[2], int(q.get("boot", 1)), int(q.get("after", 0)),
                                     min(int(q.get("limit", 100)), 1000))
    except KeyError as exc:
        return 404, {"error": "unknown device %s" % exc}, {}
    except ValueError:
        return 400, {"error": "bad query"}, {}
    return 404, {"error": "no route"}, {}


@contextmanager
def serve(store):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, status, body, headers):
            data = json.dumps(body).encode("utf-8")
            self.send_response(status)
            for k, v in dict(headers, **{"Content-Type": "application/json"}).items():
                self.send_header(k, v)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            self._send(*route(store, self.path))

        def do_POST(self):                       # provider-state hook used by contract verification
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            self._send(200, {}, {}) if self.path == "/_contract/state" else self._send(404, {}, {})

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        yield "http://127.0.0.1:%d" % server.server_port
    finally:
        server.shutdown()
        server.server_close()
