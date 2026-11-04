"""Try it: two experiments on post-quantum sizes (run: python try_it.py)."""
import datetime as dt

from cryptography import x509
from cryptography.hazmat.primitives import serialization as ser
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, mldsa, mlkem
from cryptography.x509.oid import NameOID

# 1) The higher-security hybrid SecP384r1MLKEM1024 (RFC 10024 section 7.3): predict its key-share bytes.
p384 = ec.generate_private_key(ec.SECP384R1()).public_key().public_bytes(ser.Encoding.X962, ser.PublicFormat.UncompressedPoint)
k = mlkem.MLKEM1024PrivateKey.generate()
ct = k.public_key().encapsulate()[1]
client, server = len(p384) + len(k.public_key().public_bytes_raw()), len(p384) + len(ct)
print(f"1) SecP384r1MLKEM1024: client share {client} B, server share {server} B, on wire {client + server} B "
      f"(X25519MLKEM768: 2336 B)")


# 2) Post-quantum AUTHENTICATION costs more bytes than PQ key exchange: a root + leaf certificate chain.
def chain_bytes(cls):
    now = dt.datetime(2026, 10, 28, tzinfo=dt.timezone.utc)
    root, leaf = cls.generate(), cls.generate()

    def cert(key, cn):
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
        issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "root")])
        return (x509.CertificateBuilder().subject_name(name).issuer_name(issuer).public_key(key.public_key())
                .serial_number(1).not_valid_before(now).not_valid_after(now + dt.timedelta(days=1)).sign(root, None))
    certs = [cert(root, "root"), cert(leaf, "localhost")]
    return sum(len(c.public_bytes(ser.Encoding.DER)) for c in certs) + len(leaf.sign(b"transcript"))  # + CertificateVerify


ed, ml = chain_bytes(ed25519.Ed25519PrivateKey), chain_bytes(mldsa.MLDSA65PrivateKey)
print(f"2) root+leaf certificates + CertificateVerify: Ed25519 {ed} B, ML-DSA-65 {ml} B ({ml / ed:.0f}x)")
