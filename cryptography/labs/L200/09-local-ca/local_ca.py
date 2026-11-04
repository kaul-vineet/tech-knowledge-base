"""A local certificate authority with pyca/cryptography: root CA -> server certificate (SAN, key usage, validity)."""
import datetime as dt
import ipaddress
import sys
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization as ser
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
from cryptography.x509.verification import PolicyBuilder, Store

NOW = dt.datetime.now(dt.timezone.utc)
KU = dict(content_commitment=False, key_encipherment=False, data_encipherment=False,
          key_agreement=False, encipher_only=False, decipher_only=False)


def _name(cn: str) -> x509.Name:
    return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])


def make_root(cn="KB Local Root CA", days=365):
    key = ec.generate_private_key(ec.SECP256R1())
    cert = (x509.CertificateBuilder().subject_name(_name(cn)).issuer_name(_name(cn))  # self-signed: issuer == subject
            .public_key(key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(NOW).not_valid_after(NOW + dt.timedelta(days=days))
            .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)  # may sign leaves only
            .add_extension(x509.KeyUsage(digital_signature=False, key_cert_sign=True, crl_sign=True, **KU), critical=True)
            .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
            .sign(key, hashes.SHA256()))
    return key, cert


def issue_server(ca_key, ca_cert, names=("localhost",), ips=("127.0.0.1",), days=30, not_before=None):
    key = ec.generate_private_key(ec.SECP256R1())
    start = not_before or NOW
    san = [x509.DNSName(n) for n in names] + [x509.IPAddress(ipaddress.ip_address(i)) for i in ips]
    cert = (x509.CertificateBuilder().subject_name(_name(names[0])).issuer_name(ca_cert.subject)
            .public_key(key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(start).not_valid_after(start + dt.timedelta(days=days))  # validity window
            .add_extension(x509.SubjectAlternativeName(san), critical=False)  # SAN: clients match THIS, not the CN
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .add_extension(x509.KeyUsage(digital_signature=True, key_cert_sign=False, crl_sign=False, **KU), critical=True)
            .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
            .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()), critical=False)
            .sign(ca_key, hashes.SHA256()))  # the CA's signature binds name + public key + validity
    return key, cert


def verify(leaf, roots, hostname: str, at=None, intermediates=()):
    """Path validation (RFC 5280 + web-PKI profile). Returns the chain or raises VerificationError."""
    verifier = PolicyBuilder().store(Store(list(roots))).time(at or NOW).build_server_verifier(x509.DNSName(hostname))
    return verifier.verify(leaf, list(intermediates))


def save_pem(folder: Path, ca_cert, key, cert) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "ca.pem").write_bytes(ca_cert.public_bytes(ser.Encoding.PEM))
    (folder / "server.pem").write_bytes(cert.public_bytes(ser.Encoding.PEM))
    (folder / "server-key.pem").write_bytes(  # private key: keep out of git, never paste into a chat/model
        key.private_bytes(ser.Encoding.PEM, ser.PrivateFormat.PKCS8, ser.NoEncryption()))


def attempt(label, *args, **kw):
    try:
        print(f"{label:<22} OK, chain length {len(verify(*args, **kw))}")
    except x509.verification.VerificationError as e:
        print(f"{label:<22} FAIL: {str(e).split(' (encountered')[0]}")


if __name__ == "__main__":
    ca_key, ca = make_root()
    key, leaf = issue_server(ca_key, ca)
    print("root:", ca.subject.rfc4514_string(), "| CA:", ca.extensions.get_extension_for_class(x509.BasicConstraints).value.ca)
    print("leaf SAN:", [str(n.value) for n in leaf.extensions.get_extension_for_class(x509.SubjectAlternativeName).value])
    print("leaf valid:", leaf.not_valid_before_utc.date(), "->", leaf.not_valid_after_utc.date())
    attempt("localhost", leaf, [ca], "localhost")
    attempt("wrong host", leaf, [ca], "example.com")
    attempt("31 days later", leaf, [ca], "localhost", at=NOW + dt.timedelta(days=31))
    attempt("untrusted root", leaf, [make_root("Some Other Root")[1]], "localhost")
    if "--out" in sys.argv:  # python local_ca.py --out pki  -> files for lab 10 / openssl s_client
        save_pem(Path(sys.argv[sys.argv.index("--out") + 1]), ca, key, leaf)
        print("wrote ca.pem, server.pem, server-key.pem")
