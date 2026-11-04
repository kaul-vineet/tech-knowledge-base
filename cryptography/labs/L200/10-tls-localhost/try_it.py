"""Try it: two experiments on TLS (run: python try_it.py)."""
import socket
import ssl
import tempfile
from pathlib import Path

import tls_localhost as lab

with tempfile.TemporaryDirectory() as tmp:
    pki = lab.make_pki(Path(tmp))
    port = lab.start_server(lab.server_context(pki), connections=2)

    # 1) Cap the CLIENT at TLS 1.2: the server (min 1.2) agrees on 1.2 and a TLS 1.2 cipher suite.
    ctx = ssl.create_default_context(cafile=str(pki / "ca.pem"))
    ctx.maximum_version = ssl.TLSVersion.TLSv1_2
    with socket.create_connection(("127.0.0.1", port)) as raw, ctx.wrap_socket(raw, server_hostname="localhost") as t:
        print("1) client max TLS 1.2 ->", t.version(), t.cipher()[0])

    # 2) Ask for the IP address instead of a name: it matches the IP entry in the SAN.
    version, cipher, data = lab.connect(port, pki / "ca.pem", "127.0.0.1")
    print("2) server_hostname='127.0.0.1' ->", version, data)
