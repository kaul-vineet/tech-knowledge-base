"""Equivalent (pending CI): a real TLS 1.3 handshake on 127.0.0.1 and the key-exchange group it negotiated.
Needs Python 3.15+ (SSLSocket.group()) linked to OpenSSL 3.5+ (native X25519MLKEM768). Uses lab 9's local CA."""
import socket
import ssl
import sys
import tempfile
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "L200" / "09-local-ca"))
import local_ca  # noqa: E402


def probe():
    if not hasattr(ssl.SSLSocket, "group") or ssl.OPENSSL_VERSION_INFO < (3, 5):
        return f"skipped: needs Python 3.15+ with OpenSSL 3.5+ (have Python {sys.version.split()[0]}, {ssl.OPENSSL_VERSION})"
    with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent, ignore_cleanup_errors=True) as d:
        pki = Path(d)
        ca_key, ca = local_ca.make_root()
        key, leaf = local_ca.issue_server(ca_key, ca)
        local_ca.save_pem(pki, ca, key, leaf)
        sctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        sctx.minimum_version = ssl.TLSVersion.TLSv1_3
        sctx.load_cert_chain(pki / "server.pem", pki / "server-key.pem")
        listener = socket.create_server(("127.0.0.1", 0))
        seen = []

        def serve():
            raw, _ = listener.accept()
            with sctx.wrap_socket(raw, server_side=True) as tls:
                seen.append(tls.group())
                tls.sendall(b"ok")
        threading.Thread(target=serve, daemon=True).start()
        cctx = ssl.create_default_context(cafile=str(pki / "ca.pem"))
        with socket.create_connection(listener.getsockname(), timeout=5) as raw:
            with cctx.wrap_socket(raw, server_hostname="localhost") as tls:
                tls.recv(2)
                group = tls.group()
        listener.close()
        return f"negotiated group: {group} (server saw {seen[0] if seen else '?'}) | {ssl.OPENSSL_VERSION}"


if __name__ == "__main__":
    print(probe())
