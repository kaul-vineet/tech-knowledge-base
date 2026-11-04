"""Driven adapters behind the crypto ports (application-architecture: ports and adapters).

The ONLY module of this lab that names concrete primitives (agility lint allow-list). Each adapter advertises the
byte sizes it puts on the wire; the agility<->wire seam test measures real outputs against these numbers.
The hybrid reuses cryptography L400 #18: RFC 10024 share layout (ML-KEM first) and the strict client (no fallback).
"""
import contextlib
import io

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519, mldsa, x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import _kb  # noqa: F401
import pq_hybrid as l18
import solution_strict as l18_strict

derive = l18.derive                     # HKDF-SHA256 over the secret, bound to both shares (lesson 18)
HandshakeError = l18.HandshakeError


class X25519Kex:
    id, codepoint, pq = "X25519", 0x001D, False
    client_share_bytes = server_share_bytes = 32

    def client_hello(self):
        sk = x25519.X25519PrivateKey.generate()
        share = sk.public_key().public_bytes_raw()
        return {"x": sk, "share": share}, share

    def server_respond(self, share):
        if len(share) != self.client_share_bytes:
            raise HandshakeError("illegal_parameter: X25519 client share must be 32 bytes")
        sk = x25519.X25519PrivateKey.generate()
        mine = sk.public_key().public_bytes_raw()
        return mine, derive(sk.exchange(x25519.X25519PublicKey.from_public_bytes(share)), share, mine)

    def client_finish(self, st, server_share):
        if len(server_share) != self.server_share_bytes:
            raise HandshakeError("illegal_parameter: X25519 server share must be 32 bytes")
        return derive(st["x"].exchange(x25519.X25519PublicKey.from_public_bytes(server_share)), st["share"], server_share)


class X25519MLKEM768Kex:
    id, codepoint, pq = "X25519MLKEM768", 0x11EC, True
    client_share_bytes, server_share_bytes = l18.MLKEM_PK + l18.X_LEN, l18.MLKEM_CT + l18.X_LEN   # 1216, 1120

    def client_hello(self):
        return l18.client_hello()

    def server_respond(self, share):
        return l18.server_respond(share)

    def client_finish(self, st, server_share):
        with contextlib.redirect_stdout(io.StringIO()):   # lesson 18's strict client prints its abort event
            key, _ = l18_strict.client_finish(st, server_share)
        return key


class _Sig:
    def keygen(self):
        sk = self.impl.generate()
        return sk, sk.public_key()

    def sign(self, sk, data):
        return sk.sign(data)

    def verify(self, pk, signature, data):
        try:
            pk.verify(signature, data)
            return True
        except InvalidSignature:
            return False


class Ed25519Sig(_Sig):
    id, pq, impl, public_key_bytes, signature_bytes = "Ed25519", False, ed25519.Ed25519PrivateKey, 32, 64


class MLDSA65Sig(_Sig):
    id, pq, impl, public_key_bytes, signature_bytes = "ML-DSA-65", True, mldsa.MLDSA65PrivateKey, 1952, 3309


class MLDSA87Sig(_Sig):
    id, pq, impl, public_key_bytes, signature_bytes = "ML-DSA-87", True, mldsa.MLDSA87PrivateKey, 2592, 4627


class Aes256Gcm:
    id, key_bytes, tag_bytes = "A256GCM", 32, 16

    def seal(self, key, nonce, data, aad=None):
        return AESGCM(key).encrypt(nonce, data, aad)

    def open(self, key, nonce, data, aad=None):
        return AESGCM(key).decrypt(nonce, data, aad)
