"""Try it: two small experiments on AEAD (run: python try_it.py)."""
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import aead_demo as lab

aead = AESGCM(AESGCM.generate_key(bit_length=256))
aad = b"user_id=42;v=1"
blob = lab.seal(aead, b"card=4111-1111", aad)

# 1) Flip one bit in the stored nonce (byte 0), leave ciphertext and tag alone.
bad = bytearray(blob)
bad[0] ^= 0x01
print("1) nonce bit flipped ->", lab.try_open(aead, bytes(bad), aad))

# 2) Change the plaintext length: overhead stays 12-byte nonce + 16-byte tag.
for n in (0, 14, 1000):
    b = lab.seal(aead, b"x" * n, aad)
    print(f"2) plaintext {n:4} B -> blob {len(b):4} B (overhead {len(b) - n} B)")
