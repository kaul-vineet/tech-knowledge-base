"""Evidence for the decision: where does a signing key live? File key vs KMS-style remote signing vs token handle.
Each option signs the same message; then we simulate a host compromise followed by clean-up (disable / log out)
and ask whether the attacker can still sign. Latencies are medians on THIS machine (KMS = HTTP on 127.0.0.1)."""
import json
import statistics
import tempfile
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from cryptography.hazmat.primitives import serialization as ser
from cryptography.hazmat.primitives.asymmetric import ed25519

import solution_nonexportable as tok


def median_us(fn, reps=200):
    runs = []
    for _ in range(reps):
        t = time.perf_counter()
        fn()
        runs.append((time.perf_counter() - t) * 1e6)
    return round(statistics.median(runs), 1)


class KMS(BaseHTTPRequestHandler):
    keys, enabled = {"release": ed25519.Ed25519PrivateKey.generate()}, {"release": True}

    def do_POST(self):
        op, name = self.path.strip("/").split("/")
        body = self.rfile.read(int(self.headers["Content-Length"]))
        if op == "disable":
            KMS.enabled[name] = False
        if op == "sign" and not KMS.enabled[name]:
            self.send_response(403)
            self.end_headers()
            return
        out = KMS.keys[name].sign(body).hex().encode() if op == "sign" else b"ok"
        self.send_response(200)
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def log_message(self, *args):
        pass


def kms_call(port, op, data=b"m"):
    req = urllib.request.Request(f"http://127.0.0.1:{port}/{op}/release", data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        return e.code


def main():
    # A) PEM file next to the app (encrypted or not, the app can decrypt it)
    with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent, ignore_cleanup_errors=True) as d:
        pem = Path(d) / "release-key.pem"
        pem.write_bytes(ed25519.Ed25519PrivateKey.generate().private_bytes(ser.Encoding.PEM, ser.PrivateFormat.PKCS8, ser.NoEncryption()))
        key = ser.load_pem_private_key(pem.read_bytes(), None)
        stolen = pem.read_bytes()  # host compromise: the attacker copies what the app can read
        sign_us = median_us(lambda: key.sign(b"m"))
    print(json.dumps({"option": "file key", "app_can_read_key": True, "sign_us": sign_us,
                      "attacker_signs_after_cleanup": ser.load_pem_private_key(stolen, None).sign(b"x") is not None}))

    server = ThreadingHTTPServer(("127.0.0.1", 0), KMS)  # B) KMS-style: key stays in the service, app sends data
    threading.Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_address[1]
    sign_us = median_us(lambda: kms_call(port, "sign"), 100)
    kms_call(port, "disable")  # incident response: disable the key version in the service
    print(json.dumps({"option": "KMS-style remote signing (HTTP, 127.0.0.1)", "app_can_read_key": False, "sign_us": sign_us,
                      "attacker_signs_after_cleanup": kms_call(port, "sign") != 403}))
    server.shutdown()
    server.server_close()

    token = tok.SoftToken("kb-l19", so_pin="so-demo-1234", user_pin="user-demo-5678")  # C) token: handle, not bytes
    s = token.open_session()
    s.login("USER", "user-demo-5678")
    _, priv = s.generate_key_pair(tok.CKM_EDDSA, "release")
    sign_us = median_us(lambda: s.sign(priv, tok.CKM_EDDSA, b"m"))
    try:
        s.get_attribute_value(priv, tok.CKA_VALUE)
        readable = True
    except tok.PKCS11Error:
        readable = False
    s.logout()  # clean-up: session closed / token removed; the attacker kept only a handle number
    try:
        s.sign(priv, tok.CKM_EDDSA, b"x")
        after = True
    except tok.PKCS11Error:
        after = False
    print(json.dumps({"option": "token handle (PKCS#11-shaped, non-exportable)", "app_can_read_key": readable,
                      "sign_us": sign_us, "attacker_signs_after_cleanup": after}))


if __name__ == "__main__":
    main()
