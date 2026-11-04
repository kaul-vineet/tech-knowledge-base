"""AEAD with pyca/cryptography: AES-256-GCM and ChaCha20-Poly1305, AAD, tamper detection, nonce reuse."""
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

# RFC 8439 section 2.8.2 test vector (AEAD_CHACHA20_POLY1305)
RFC8439 = {
    "key": bytes(range(0x80, 0xA0)),
    "nonce": bytes.fromhex("07000000") + bytes.fromhex("4041424344454647"),  # constant || IV
    "aad": bytes.fromhex("50515253c0c1c2c3c4c5c6c7"),
    "pt": b"Ladies and Gentlemen of the class of '99: If I could offer you only one tip "
          b"for the future, sunscreen would be it.",
    "ct": bytes.fromhex(
        "d31a8d34648e60db7b86afbc53ef7ec2a4aded51296e08fea9e2b5a736ee62d6"
        "3dbea45e8ca9671282fafb69da92728b1a71de0a9e060b2905d6a5b67ecd3b36"
        "92ddbd7f2d778b8c9803aee328091b58fab324e4fad675945585808b4831d7bc"
        "3ff4def08e4b7a9de576d26586cec64b6116"),
    "tag": bytes.fromhex("1ae10b594f09e26a7e902ecbd0600691"),
}
# GCM spec (McGrew & Viega) Test Case 14: AES-256, zero key/IV, one zero block
GCM_TC14 = {"key": bytes(32), "nonce": bytes(12), "pt": bytes(16),
            "ct": bytes.fromhex("cea7403d4d606b6e074ec5d3baf39d18"),
            "tag": bytes.fromhex("d0d1c8a799996bf0265b98b5d48ab919")}


def seal(aead, plaintext: bytes, aad: bytes) -> bytes:
    nonce = os.urandom(12)  # nonce = number used once: fresh random 96-bit nonce per message
    return nonce + aead.encrypt(nonce, plaintext, aad)  # AEAD output: ciphertext || 16-byte tag; ship nonce with it


def open_(aead, blob: bytes, aad: bytes) -> bytes:
    return aead.decrypt(blob[:12], blob[12:], aad)  # all-or-nothing decrypt: InvalidTag on any change


def try_open(aead, blob, aad) -> str:
    try:
        return open_(aead, blob, aad).decode()
    except InvalidTag:
        return "InvalidTag (rejected)"


if __name__ == "__main__":
    v = RFC8439
    out = ChaCha20Poly1305(v["key"]).encrypt(v["nonce"], v["pt"], v["aad"])
    print("RFC 8439 2.8.2 ChaCha20-Poly1305 vector:", out == v["ct"] + v["tag"])
    g = GCM_TC14
    print("GCM spec TC14 AES-256-GCM vector:       ",
          AESGCM(g["key"]).encrypt(g["nonce"], g["pt"], None) == g["ct"] + g["tag"])

    aad = b"user_id=42;v=1"  # AAD: authenticated, not encrypted
    for name, aead in [("AES-256-GCM", AESGCM(AESGCM.generate_key(bit_length=256))),
                       ("ChaCha20-Poly1305", ChaCha20Poly1305(ChaCha20Poly1305.generate_key()))]:
        blob = seal(aead, b"card=4111-1111", aad)
        flipped = bytearray(blob)
        flipped[15] ^= 0x01
        print(f"--- {name} (blob {len(blob)} bytes = 12 nonce + 14 ct + 16 tag)")
        print("  decrypt ok        ", try_open(aead, blob, aad))
        print("  1 bit flipped     ", try_open(aead, bytes(flipped), aad))
        print("  AAD changed       ", try_open(aead, blob, b"user_id=43;v=1"))

    # Nonce reuse: same key+nonce => XOR of ciphertexts equals XOR of plaintexts.
    k, n = AESGCM.generate_key(bit_length=256), os.urandom(12)
    p1, p2 = b"attack at dawn!!", b"retreat at dusk!"
    c1, c2 = AESGCM(k).encrypt(n, p1, None)[:16], AESGCM(k).encrypt(n, p2, None)[:16]
    leak = bytes(a ^ b for a, b in zip(c1, c2))
    print("nonce reuse leaks p1^p2:", leak == bytes(a ^ b for a, b in zip(p1, p2)))
    print("attacker who knows p1 recovers p2:", bytes(a ^ b for a, b in zip(leak, p1)))
