"""Try it: two experiments on public-key (hybrid) encryption (run: python try_it.py)."""
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

import seal_box as lab

bob = X25519PrivateKey.generate()

# 1) Overhead is fixed: 32-byte ephemeral public key + 16-byte tag, whatever the message size.
for n in (0, 29, 4096):
    print(f"1) plaintext {n:4} B -> blob {len(lab.seal(bob.public_key(), b'x' * n)):4} B")

# 2) Change the HKDF info label on the receiving side only (a different 'protocol version').
blob = lab.seal(bob.public_key(), b"hi")
lab.INFO, saved = b"kb-crypto-l200/v2/X25519", lab.INFO
try:
    lab.open_(bob, blob)
    print("2) opened with a different info label")
except InvalidTag:
    print("2) receiver uses info v2, sender used v1 -> InvalidTag (keys differ, domain separation works)")
lab.INFO = saved
