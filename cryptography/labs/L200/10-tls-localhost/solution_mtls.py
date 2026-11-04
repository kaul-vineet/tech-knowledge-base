"""Build-task solution: mutual TLS (mTLS). The server also demands a client certificate from the lab-9 CA."""
import datetime as dt
import socket
import ssl
import threading
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization as ser
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID

import tls_localhost
from tls_localhost import local_ca


def make_pki_with_client(folder: Path, client_cn="build-agent-7") -> Path:
    ca_key, ca = local_ca.make_root()
    key, leaf = local_ca.issue_server(ca_key, ca)
    local_ca.save_pem(folder, ca, key, leaf)
    ck = ec.generate_private_key(ec.SECP256R1())
    cc = (x509.CertificateBuilder().subject_name(local_ca._name(client_cn)).issuer_name(ca.subject)
          .public_key(ck.public_key()).serial_number(x509.random_serial_number())
          .not_valid_before(local_ca.NOW).not_valid_after(local_ca.NOW + dt.timedelta(days=30))
          .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
          .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CLIENT_AUTH]), critical=False)  # client role
          .sign(ca_key, hashes.SHA256()))
    (folder / "client.pem").write_bytes(cc.public_bytes(ser.Encoding.PEM))
    (folder / "client-key.pem").write_bytes(ck.private_bytes(ser.Encoding.PEM, ser.PrivateFormat.PKCS8,
                                                             ser.NoEncryption()))
    return folder


def mtls_server_context(pki: Path) -> ssl.SSLContext:
    ctx = tls_localhost.server_context(pki)
    ctx.verify_mode = ssl.CERT_REQUIRED  # demand a client certificate ...
    ctx.load_verify_locations(cafile=str(pki / "ca.pem"))  # ... issued by our CA
    return ctx


def start_mtls_server(ctx, seen: list):
    listener = socket.create_server(("127.0.0.1", 0))

    def serve():
        with listener:
            raw, _ = listener.accept()
            try:
                with ctx.wrap_socket(raw, server_side=True) as tls:
                    cn = dict(x[0] for x in tls.getpeercert()["subject"])["commonName"]
                    seen.append(cn)
                    tls.sendall(f"hello {cn}\n".encode())
            except (ssl.SSLError, OSError) as e:
                seen.append(f"rejected: {getattr(e, 'reason', e)}")
    threading.Thread(target=serve, daemon=True).start()
    return listener.getsockname()[1]


def connect_mtls(port: int, pki: Path, with_cert=True) -> bytes:
    ctx = ssl.create_default_context(cafile=str(pki / "ca.pem"))
    if with_cert:
        ctx.load_cert_chain(pki / "client.pem", pki / "client-key.pem")
    with socket.create_connection(("127.0.0.1", port), timeout=5) as raw:
        with ctx.wrap_socket(raw, server_hostname="localhost") as tls:
            return tls.recv(64)  # TLS 1.3: a missing client cert surfaces here, after the handshake
