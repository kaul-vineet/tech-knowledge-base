"""TLS on localhost with the stdlib ssl module and the lab-9 local CA: handshake, inspect, and two failures."""
import socket
import ssl
import sys
import tempfile
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "09-local-ca"))
import local_ca  # noqa: E402  (lab 9)


def make_pki(folder: Path) -> Path:
    ca_key, ca = local_ca.make_root()
    key, leaf = local_ca.issue_server(ca_key, ca, names=("localhost",), ips=("127.0.0.1",))
    local_ca.save_pem(folder, ca, key, leaf)  # ca.pem, server.pem, server-key.pem
    return folder


def server_context(pki: Path) -> ssl.SSLContext:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2  # refuse TLS 1.0/1.1
    ctx.load_cert_chain(pki / "server.pem", pki / "server-key.pem")  # server proves it owns the cert's key
    return ctx


def start_server(ctx: ssl.SSLContext, port: int = 0, connections: int = 3):
    listener = socket.create_server(("127.0.0.1", port))  # loopback only

    def serve():
        with listener:
            for _ in range(connections):
                raw, _ = listener.accept()
                try:
                    with ctx.wrap_socket(raw, server_side=True) as tls:
                        tls.sendall(b"hello over TLS\n")
                except (ssl.SSLError, OSError):  # a client that rejects our cert aborts the handshake
                    pass
    threading.Thread(target=serve, daemon=True).start()
    return listener.getsockname()[1]


def connect(port: int, cafile: Path, hostname: str):
    ctx = ssl.create_default_context(cafile=str(cafile))  # CERT_REQUIRED + check_hostname, trust ONLY this CA
    with socket.create_connection(("127.0.0.1", port), timeout=5) as raw:
        with ctx.wrap_socket(raw, server_hostname=hostname) as tls:  # SNI + hostname checked against SAN
            return tls.version(), tls.cipher(), tls.recv(64)


def attempt(label, port, cafile, hostname):
    try:
        version, cipher, data = connect(port, cafile, hostname)
        print(f"{label:<16} {version} {cipher[0]} ({cipher[2]}-bit) -> {data!r}")
    except ssl.SSLCertVerificationError as e:  # the client refuses BEFORE any application data
        print(f"{label:<16} REFUSED verify_code={e.verify_code}: {e.verify_message}")


if __name__ == "__main__":
    print("Python ssl uses", ssl.OPENSSL_VERSION)
    if "--serve" in sys.argv:  # python tls_localhost.py --serve 8443  -> try openssl s_client against it
        pki = make_pki(Path("pki"))
        port = int(sys.argv[sys.argv.index("--serve") + 1])
        start_server(server_context(pki), port, connections=1000)
        print(f"serving https on 127.0.0.1:{port}, CA file {pki / 'ca.pem'} (Ctrl+C to stop)")
        threading.Event().wait()
    with tempfile.TemporaryDirectory() as tmp:
        pki, other = make_pki(Path(tmp) / "pki"), make_pki(Path(tmp) / "other")
        port = start_server(server_context(pki))
        attempt("trusted CA", port, pki / "ca.pem", "localhost")
        attempt("wrong hostname", port, pki / "ca.pem", "example.com")
        attempt("untrusted CA", port, other / "ca.pem", "localhost")
