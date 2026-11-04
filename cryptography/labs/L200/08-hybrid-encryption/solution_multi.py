"""Build-task solution: encrypt ONE payload to SEVERAL recipients (age-style file key + one stanza per recipient)."""
import os
import struct

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

import seal_box

STANZA = 32 + 32 + 16  # eph_pub + wrapped 32-byte file key + tag


def seal_multi(recipients: list, plaintext: bytes) -> bytes:
    file_key = os.urandom(32)  # random symmetric key, used for exactly one payload
    stanzas = b"".join(seal_box.seal(r, file_key) for r in recipients)  # wrap the file key for each recipient
    payload = ChaCha20Poly1305(file_key).encrypt(bytes(12), plaintext, stanzas)  # header is AAD: no stanza swaps
    return struct.pack(">B", len(recipients)) + stanzas + payload


def open_multi(me: X25519PrivateKey, blob: bytes) -> bytes:
    n = blob[0]
    stanzas = blob[1:1 + n * STANZA]
    for i in range(n):
        try:
            file_key = seal_box.open_(me, stanzas[i * STANZA:(i + 1) * STANZA])
        except Exception:  # not addressed to me (InvalidTag) -> try the next stanza
            continue
        return ChaCha20Poly1305(file_key).decrypt(bytes(12), blob[1 + n * STANZA:], stanzas)
    raise ValueError("no stanza for this identity")
