"""Computes every number quoted in the L200 concept notes (content/concepts/L200/*.md).
Run from this folder: python l200_concept_examples.py > l200_concept_examples.out.txt"""
import datetime as dt
import hashlib
import sys
import tempfile
from pathlib import Path

LABS = Path(__file__).resolve().parent.parent / "labs" / "L200"
for d in ("07-ed25519-signatures", "08-hybrid-encryption", "09-local-ca", "10-tls-localhost", "11-tokens"):
    sys.path.insert(0, str(LABS / d))

import local_ca, seal_box, signatures, tls_localhost, tokens  # noqa: E402
from cryptography.hazmat.primitives import hashes, serialization as ser  # noqa: E402
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey  # noqa: E402
from cryptography.hazmat.primitives.kdf.hkdf import HKDF  # noqa: E402

print("== 07 Ed25519 ==")
v = signatures.RFC8032_T1
k = Ed25519PrivateKey.from_private_bytes(v["secret"])
print("T1 public :", k.public_key().public_bytes_raw().hex())
print("T1 sig    :", k.sign(b"").hex(), "len", len(k.sign(b"")))
print("PEM private", len(k.private_bytes(ser.Encoding.PEM, ser.PrivateFormat.PKCS8, ser.NoEncryption())),
      "PEM public", len(k.public_key().public_bytes(ser.Encoding.PEM, ser.PublicFormat.SubjectPublicKeyInfo)))

print("== 08 X25519 + HKDF ==")
r = seal_box.RFC7748
a, b = X25519PrivateKey.from_private_bytes(r["a"]), X25519PrivateKey.from_private_bytes(r["b"])
K = a.exchange(b.public_key())
print("K = X25519(a, B):", K.hex(), "| equals X25519(b, A):", K == b.exchange(a.public_key()))
key = HKDF(algorithm=hashes.SHA256(), length=32, salt=r["A"] + r["B"], info=seal_box.INFO).derive(K)
print("HKDF-SHA256(K, salt=A||B, info=lab label) first 8 bytes:", key[:8].hex())
print("seal overhead bytes:", len(seal_box.seal(b.public_key(), b"x" * 29)) - 29)

print("== 09 local CA ==")
ca_key, ca = local_ca.make_root()
_, leaf = local_ca.issue_server(ca_key, ca)
print("chain length:", len(local_ca.verify(leaf, [ca], "localhost")))
print("leaf validity days:", (leaf.not_valid_after_utc - leaf.not_valid_before_utc).days)
for host, at in (("example.com", None), ("localhost", local_ca.NOW + dt.timedelta(days=31))):
    try:
        local_ca.verify(leaf, [ca], host, at=at)
    except Exception as e:
        print(f"{host} at {'+31d' if at else 'now'}:", str(e).split(" (encountered")[0])

print("== 10 TLS ==")
with tempfile.TemporaryDirectory() as tmp:
    pki, other = tls_localhost.make_pki(Path(tmp) / "p"), tls_localhost.make_pki(Path(tmp) / "o")
    port = tls_localhost.start_server(tls_localhost.server_context(pki))
    print("ok:", tls_localhost.connect(port, pki / "ca.pem", "localhost")[:2])
    for host, ca_file in (("example.com", pki / "ca.pem"), ("localhost", other / "ca.pem")):
        try:
            tls_localhost.connect(port, ca_file, host)
        except Exception as e:
            print(host, "->", e.verify_code, e.verify_message)

print("== 11 tokens ==")
none_header = tokens.b64u(b'{"alg":"none","typ":"JWT"}')
print("alg none header b64url length:", len(none_header), "starts", none_header[:6])
sk = Ed25519PrivateKey.generate()
t = tokens.sign({"sub": "alice", "aud": "orders-api", "exp": 1_800_000_300, "role": "user"}, "EdDSA", sk)
print("EdDSA token length (chars):", len(t), "| signature part chars:", len(t.split(".")[2]))
print("HS256 tag bytes:", len(tokens._hs256(b"k" * 32, b"m")), "| raw Ed25519 public key (attacker's HMAC key) bytes:",
      len(sk.public_key().public_bytes_raw()))
print("python", sys.version.split()[0], "| sha256('abc') sanity", hashlib.sha256(b"abc").hexdigest()[:8])
