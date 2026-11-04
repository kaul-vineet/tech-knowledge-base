"""Try it: two experiments on certificates (run: python try_it.py)."""
from cryptography import x509
from cryptography.hazmat.primitives import serialization as ser

import local_ca as lab

ca_key, ca = lab.make_root()

# 1) Issue a cert for DNS name ip-only.test (+ IP 127.0.0.1) and ask for "localhost": only SAN entries count.
_, ip_only = lab.issue_server(ca_key, ca, names=("ip-only.test",), ips=("127.0.0.1",))
lab.attempt("1) ask localhost", ip_only, [ca], "localhost")
lab.attempt("1) ask ip-only.test", ip_only, [ca], "ip-only.test")

# 2) The same certificate in PEM vs DER: PEM is base64 DER plus header lines (~4/3 the size).
_, leaf = lab.issue_server(ca_key, ca)
pem, der = leaf.public_bytes(ser.Encoding.PEM), leaf.public_bytes(ser.Encoding.DER)
print(f"2) DER {len(der)} B, PEM {len(pem)} B, ratio {len(pem) / len(der):.2f};",
      "DER->cert == PEM->cert:", x509.load_der_x509_certificate(der) == x509.load_pem_x509_certificate(pem))
