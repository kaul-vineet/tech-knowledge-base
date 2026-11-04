"""Encrypt to someone's PUBLIC key: X25519 + HKDF-SHA256 + ChaCha20-Poly1305 (the pattern age and HPKE use)."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

INFO = b"kb-crypto-l200/v1/X25519"  # domain-separation label (age uses "age-encryption.org/v1/X25519")
ZERO_NONCE = bytes(12)  # safe ONLY because every message gets a brand-new key (fresh ephemeral key pair)

# RFC 7748 section 6.1 Diffie-Hellman test vector
RFC7748 = {
    "a": bytes.fromhex("77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a"),
    "A": bytes.fromhex("8520f0098930a754748b7ddcb43ef75a0dbf3a0d26381af4eba4a98eaa9b4e6a"),
    "b": bytes.fromhex("5dab087e624a8a4b79e17f8b83800ee66f3bb1292618b6fd1c2f8b27ff88e0eb"),
    "B": bytes.fromhex("de9edb7d7b7dc1b4d35b61c2ece435373f8343c85b78674dadfc7e146f882b4f"),
    "K": bytes.fromhex("4a5d9d5ba4ce2de1728e3bf480350f25e07e21c947d19e3376f09b3c1e161742"),
}


def _key(shared: bytes, eph_pub: bytes, rcpt_pub: bytes) -> bytes:
    if shared == bytes(32):  # RFC 7748 s6: abort on all-zero output (small-order public key)
        raise ValueError("all-zero shared secret")
    # KDF: never use the raw DH output as a key; bind both public keys via the salt (like age)
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=eph_pub + rcpt_pub, info=INFO).derive(shared)


def seal(rcpt: X25519PublicKey, plaintext: bytes, aad: bytes = b"") -> bytes:
    eph = X25519PrivateKey.generate()  # ephemeral key: one per message, then thrown away
    eph_pub, rcpt_pub = eph.public_key().public_bytes_raw(), rcpt.public_bytes_raw()
    key = _key(eph.exchange(rcpt), eph_pub, rcpt_pub)  # key agreement: X25519(eph, recipient)
    return eph_pub + ChaCha20Poly1305(key).encrypt(ZERO_NONCE, plaintext, aad)  # blob = 32 B eph_pub || ct || 16 B tag


def open_(me: X25519PrivateKey, blob: bytes, aad: bytes = b"") -> bytes:
    eph_pub = blob[:32]
    key = _key(me.exchange(X25519PublicKey.from_public_bytes(eph_pub)),  # X25519(me, eph): same shared secret
               eph_pub, me.public_key().public_bytes_raw())
    return ChaCha20Poly1305(key).decrypt(ZERO_NONCE, blob[32:], aad)  # InvalidTag if wrong key / tampered


if __name__ == "__main__":
    a, b = (X25519PrivateKey.from_private_bytes(RFC7748[k]) for k in ("a", "b"))
    print("RFC 7748 6.1 Alice public:  ", a.public_key().public_bytes_raw() == RFC7748["A"])
    print("RFC 7748 6.1 shared secret: ", a.exchange(b.public_key()) == RFC7748["K"] == b.exchange(a.public_key()))

    from cryptography.exceptions import InvalidTag
    bob, eve = X25519PrivateKey.generate(), X25519PrivateKey.generate()
    msg = b"db password rotation at 02:00"
    blob = seal(bob.public_key(), msg, aad=b"to:bob")  # sender needs only Bob's PUBLIC key
    print(f"sealed {len(msg)} B -> {len(blob)} B (overhead {len(blob) - len(msg)} = 32 eph_pub + 16 tag)")
    print("bob opens:   ", open_(bob, blob, aad=b"to:bob"))
    print("same msg sealed twice -> different blobs:", seal(bob.public_key(), msg) != seal(bob.public_key(), msg))
    for label, fn in [("eve opens:   ", lambda: open_(eve, blob, aad=b"to:bob")),
                      ("aad changed: ", lambda: open_(bob, blob, aad=b"to:eve")),
                      ("eph swapped: ", lambda: open_(bob, eve.public_key().public_bytes_raw() + blob[32:], b"to:bob"))]:
        try:
            fn()
        except InvalidTag:
            print(label, "InvalidTag (rejected)")
