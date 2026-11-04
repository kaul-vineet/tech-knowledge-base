"""Try it: two small experiments comparing the three tools (run: python try_it.py)."""
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import compare as lab

# 1) Change SECRET to b"Hi": encodings shrink with the input, a hash is always 64 hex chars.
key = AESGCM.generate_key(bit_length=256)
e = lab.encode(b"Hi")
print("1) base64:", e["base64"], "| hex:", e["hex"], "| sha256 hex chars:", len(lab.hash_(b"Hi")),
      "| AES-GCM blob bytes:", len(lab.encrypt(b"Hi", key)))

# 2) Change the last character of SECRET: count how many output characters change.
a, b = lab.SECRET, lab.SECRET[:-1] + b"u"


def diff(x: str, y: str) -> int:
    return sum(c1 != c2 for c1, c2 in zip(x, y))


print("2) base64 chars changed:", diff(lab.encode(a)["base64"], lab.encode(b)["base64"]), "of", len(lab.encode(a)["base64"]),
      "| sha256 hex chars changed:", diff(lab.hash_(a), lab.hash_(b)), "of 64")
