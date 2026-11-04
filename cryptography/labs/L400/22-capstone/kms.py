"""KMS component: holds the versioned key-encryption keys (lesson 12's Keyring) and answers wrap / unwrap / rewrap /
rotate / retire over mutual TLS on 127.0.0.1 (lessons 9-10). The KEK never leaves this component; the caller's
identity is the CN of its client certificate, and every operation is written to the signed audit log."""
import base64
import http.client
import json
import ssl
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import paths  # noqa: F401  (reused labs on sys.path)
import envelope as l12  # lesson 12: Keyring, wrap, unwrap, KeyInUse, UnknownKey
import solution_mtls  # lesson 10 build task: PKI with a client certificate, server context that demands it


class KMSHandler(BaseHTTPRequestHandler):
    kms = None  # set by start_kms

    def do_POST(self):
        cert = self.connection.getpeercert() or {}
        caller = dict(x[0] for x in cert.get("subject", ()))["commonName"]  # identity from the verified client cert
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        try:
            status, out = 200, self.kms.handle(self.path.strip("/"), caller, body)
        except (l12.KeyInUse, l12.UnknownKey, KeyError, ValueError) as e:
            status, out = 409, {"error": f"{type(e).__name__}: {e}"}
        data = json.dumps(out).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass  # no access log with request bodies: wrapped keys are not for logs


class KMS:
    def __init__(self, audit):
        self.ring, self.audit = l12.Keyring("docs-kek"), audit

    def handle(self, op: str, caller: str, body: dict) -> dict:
        who = f"{caller}/{body.get('on_behalf', '-')}"
        if op == "wrap":
            kid, wdek = l12.wrap(self.ring, base64.b64decode(body["dek"]))
            out = {"kid": kid, "wdek": wdek}
        elif op == "unwrap":
            out = {"dek": base64.b64encode(l12.unwrap(self.ring, body["kid"], body["wdek"])).decode()}
        elif op == "rewrap":
            kid, wdek = l12.wrap(self.ring, l12.unwrap(self.ring, body["kid"], body["wdek"]))  # DEK stays inside
            out = {"kid": kid, "wdek": wdek}
        elif op == "rotate":
            out = {"primary": self.ring.rotate()}
        elif op == "retire":  # retire-after-rewrap (lesson 12): the caller reports records_by_kid, the KMS decides
            version, kid = int(body["version"]), self.ring.kid(int(body["version"]))
            if version == self.ring.primary or body["records_by_kid"].get(kid, 0):
                raise l12.KeyInUse(f"{kid} still wraps {body['records_by_kid'].get(kid, 0)} record(s) or is primary")
            del self.ring.versions[version]
            out = {"retired": kid}
        else:
            raise ValueError(f"unknown operation {op}")
        self.audit.append(who, f"kms.{op}", body.get("doc", body.get("kid", "-")))
        return out


def start_kms(pki, audit):
    ctx = solution_mtls.mtls_server_context(pki)  # TLS 1.2+ with CERT_REQUIRED and our CA
    KMSHandler.kms = KMS(audit)
    server = ThreadingHTTPServer(("127.0.0.1", 0), KMSHandler)
    server.socket = ctx.wrap_socket(server.socket, server_side=True)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, KMSHandler.kms


class KMSClient:
    def __init__(self, port: int, pki, with_cert=True, ca_file=None):
        self.port, self.ctx = port, ssl.create_default_context(cafile=str(ca_file or pki / "ca.pem"))
        if with_cert:
            self.ctx.load_cert_chain(pki / "client.pem", pki / "client-key.pem")

    def call(self, op: str, **body) -> dict:
        conn = http.client.HTTPSConnection("127.0.0.1", self.port, context=self.ctx, timeout=10)
        try:
            conn.request("POST", f"/{op}", body=json.dumps(body), headers={"Content-Type": "application/json"})
            resp = conn.getresponse()
            out = json.loads(resp.read())
        finally:
            conn.close()
        if resp.status != 200:
            raise PermissionError(out.get("error", resp.status))
        return out
