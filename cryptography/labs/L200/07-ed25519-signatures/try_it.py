"""Try it: two experiments on Ed25519 signatures (run: python try_it.py)."""
from cryptography.hazmat.primitives import serialization as ser
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import signatures as lab

# 1) Sign the same message twice with the same key: Ed25519 is deterministic (no per-signature nonce from RNG).
k = Ed25519PrivateKey.from_private_bytes(lab.RFC8032_T1["secret"])
s1, s2 = k.sign(b"app-1.0"), k.sign(b"app-1.0")
print("1) same key + same message -> identical signatures:", s1 == s2, "| first 8 bytes:", s1[:8].hex())

# 2) The same public key in three encodings: raw, PEM (SPKI) and OpenSSH. Sizes differ, the 32 key bytes do not.
pub = k.public_key()
raw = pub.public_bytes_raw()
pem = pub.public_bytes(ser.Encoding.PEM, ser.PublicFormat.SubjectPublicKeyInfo)
ssh = pub.public_bytes(ser.Encoding.OpenSSH, ser.PublicFormat.OpenSSH)
print(f"2) raw {len(raw)} B | PEM {len(pem)} B | OpenSSH {len(ssh)} B | PEM loads back to same key:",
      ser.load_pem_public_key(pem).public_bytes_raw() == raw)
print("   OpenSSH form:", ssh.decode())
