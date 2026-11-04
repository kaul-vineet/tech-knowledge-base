"""Writes the lab's CA and a 160 h leaf (PEM) into tool_check/ for step CLI and KeyStore Explorer.
Public certificates only; no private key is written."""
from pathlib import Path

from cryptography.hazmat.primitives import serialization as ser

import cert_lifecycle as cl

out = Path(__file__).resolve().parent / "tool_check"
out.mkdir(exist_ok=True)
ca_key, ca = cl.local_ca.make_root()
leaf = cl.issue(ca_key, ca, cl.T0)
(out / "ca.pem").write_bytes(ca.public_bytes(ser.Encoding.PEM))
(out / "leaf.pem").write_bytes(leaf.public_bytes(ser.Encoding.PEM))
(out / "crl.pem").write_bytes(cl.make_crl(ca_key, ca, [leaf.serial_number], cl.T0).public_bytes(ser.Encoding.PEM))
print("wrote tool_check/ca.pem, leaf.pem, crl.pem")
print("leaf validity hours:", (leaf.not_valid_after_utc - leaf.not_valid_before_utc).total_seconds() / 3600)
print("leaf serial (hex):", format(leaf.serial_number, "x"), "| revoked in crl.pem: yes")
